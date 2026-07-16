"""Capture enough context to make benchmark output interpretable."""

from __future__ import annotations

import datetime as dt
import importlib
import json
import multiprocessing
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

REPOSITORY = Path(__file__).resolve().parents[1]


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
    }


def dump_json(payload: dict[str, Any], path: Path | None) -> str:
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
    return rendered
