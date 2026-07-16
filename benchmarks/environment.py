"""Capture enough context to make benchmark output interpretable."""

from __future__ import annotations

import datetime as dt
import hashlib
import importlib
import importlib.metadata
import json
import multiprocessing
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

REPOSITORY = Path(__file__).resolve().parents[1]
_BUILD_OPTION_NAMES = {
    "buildtype",
    "optimization",
    "debug",
    "b_lto",
    "b_ndebug",
    "b_pie",
    "c_args",
    "cpp_args",
    "c_link_args",
    "cpp_link_args",
}


def _git(*args: str) -> str | None:
    try:
        completed = subprocess.run(
            ("git", *args),
            cwd=REPOSITORY,
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return completed.stdout.strip()


def _package_versions() -> dict[str, Any]:
    try:
        fortuna = importlib.import_module("Fortuna")
    except Exception as error:
        return {"available": False, "import_error": f"{type(error).__name__}: {error}"}

    version = getattr(fortuna, "__version__", getattr(fortuna, "version", None))
    storm_version = getattr(fortuna, "storm_version", None)
    try:
        storm = storm_version() if callable(storm_version) else None
    except Exception as error:
        storm = f"unavailable ({type(error).__name__}: {error})"
    return {"available": True, "fortuna": version, "storm": storm}


def _distribution_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _meson_toolchain(extension: Path) -> dict[str, Any]:
    info = extension.parent / "meson-info"
    raw_compilers = _load_json(info / "intro-compilers.json")
    host = raw_compilers.get("host", {}) if isinstance(raw_compilers, dict) else {}
    compilers = {
        language: {
            key: details.get(key)
            for key in ("id", "version", "full_version", "linker_id", "exelist")
        }
        for language, details in sorted(host.items())
        if isinstance(details, dict)
    }

    raw_options = _load_json(info / "intro-buildoptions.json")
    build_options = {}
    if isinstance(raw_options, list):
        build_options = {
            item["name"]: item.get("value")
            for item in raw_options
            if isinstance(item, dict) and item.get("name") in _BUILD_OPTION_NAMES
        }
    return {
        "build_metadata_available": bool(compilers or build_options),
        "compilers": compilers or None,
        "build_options": build_options or None,
        "build_packages": {
            name: _distribution_version(name)
            for name in ("Cython", "meson", "meson-python", "ninja")
        },
        "environment": {
            name: os.environ[name]
            for name in ("CC", "CXX", "CFLAGS", "CXXFLAGS", "CPPFLAGS", "LDFLAGS", "ARCHFLAGS")
            if name in os.environ
        },
    }


def _native_build_identity() -> dict[str, Any]:
    try:
        core = importlib.import_module("Fortuna._core")
        location = getattr(core, "__file__", None)
        if not location:
            raise RuntimeError("Fortuna._core has no file location")
        extension = Path(location).resolve()
        stat = extension.stat()
        return {
            "available": True,
            "extension": {
                "module": "Fortuna._core",
                "path": str(extension),
                "size_bytes": stat.st_size,
                "sha256": _sha256(extension),
            },
            "toolchain": _meson_toolchain(extension),
        }
    except Exception as error:
        return {"available": False, "error": f"{type(error).__name__}: {error}"}


def _cpu_affinity() -> list[int] | None:
    getter = getattr(os, "sched_getaffinity", None)
    if getter is None:
        return None
    try:
        return sorted(getter(0))
    except OSError:
        return None


def _cpu_model() -> str | None:
    system = platform.system()
    try:
        if system == "Darwin":
            return subprocess.run(
                ("sysctl", "-n", "machdep.cpu.brand_string"),
                check=True,
                capture_output=True,
                text=True,
                timeout=2,
            ).stdout.strip()
        if system == "Linux":
            with Path("/proc/cpuinfo").open(encoding="utf-8") as stream:
                for line in stream:
                    if line.lower().startswith("model name"):
                        return line.split(":", 1)[1].strip()
    except (OSError, IndexError, subprocess.SubprocessError):
        return None
    return platform.processor() or None


def collect_environment() -> dict[str, Any]:
    commit = _git("rev-parse", "HEAD")
    dirty = _git("status", "--porcelain")
    return {
        "timestamp_utc": dt.datetime.now(dt.UTC).isoformat(),
        "repository": str(REPOSITORY),
        "git": {"commit": commit, "dirty": bool(dirty) if dirty is not None else None},
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "executable": sys.executable,
            "build": platform.python_build(),
            "compiler": platform.python_compiler(),
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "cpu": {
            "model": _cpu_model(),
            "logical_count": os.cpu_count(),
            "affinity": _cpu_affinity(),
        },
        "execution": {
            "process_id": os.getpid(),
            "benchmark_threads": 1,
            "multiprocessing_start_method": multiprocessing.get_start_method(),
        },
        "packages": _package_versions(),
        "native_build": _native_build_identity(),
    }


def dump_json(payload: dict[str, Any], path: Path | None) -> str:
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
    return rendered
