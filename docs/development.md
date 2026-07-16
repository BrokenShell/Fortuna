# Developing Fortuna

Fortuna uses uv for project environments, locked dependencies, test commands,
and package builds. The compiled extension is built by Meson through
meson-python; no legacy setup or shell build script is part of the workflow.

## Set up the checkout

Install [uv](https://docs.astral.sh/uv/), then run from the repository root:

```console
uv sync --frozen --group dev --no-build-isolation-package Fortuna --reinstall-package Fortuna
uv run python -c "import Fortuna; print(Fortuna.storm_version())"
```

`--frozen` makes the checked-in `uv.lock` authoritative for the development,
test, and native editable-build toolchain. Cython, Meson, meson-python, and
Ninja are explicit development dependencies. The setup command disables build
isolation only for the editable Fortuna checkout and forces a local rebuild so
Meson's loader records the current environment's persistent Ninja path rather
than reusing an environment-specific cached loader. The same tools are pinned
in `build-system.requires` because
standalone PEP 517 builds do not consume `uv.lock`. Review both sets of pins
deliberately when updating the toolchain. When changing dependencies, update
the project metadata and lock together with `uv add`, `uv remove`, or `uv lock`;
review both changes.

After changing Cython, C++, or Meson inputs, force an editable rebuild if uv has
not already detected it:

```console
uv sync --reinstall-package Fortuna --group dev
```

## Engine and process contract

The module-level engine is thread-local and entropy-initialized. After `fork`,
the child invalidates the inherited module default and reseeds it before its
next draw. A spawned worker starts a new interpreter and initializes its own
module state.

Explicit generators have two deliberate process behaviors. `Generator(seed)`
and `for_stream(root_seed, stream_id)` are deterministic, so a forked child
inherits a copy at the same position. Worker code should derive a distinct
stream per worker when repetition is not intended. `Generator.from_entropy()`
and generators later passed to `reseed_from_entropy()` are entropy-managed;
they detect a changed process identity and reseed lazily before the child's
next draw. Built-in native methods sharing one `Generator` are serialized,
including methods inherited unchanged by a subclass, though assignment of
draws to threads remains scheduling-dependent. Generator subclasses and custom
generator-like objects own synchronization for their overrides. Do not fork
while another thread is actively using a shared explicit generator because the
child could inherit its native mutex in a locked state. Keep the concurrency
and process tests aligned with this contract.

## API hardening contracts

Optimization must preserve draw schedules, validation boundaries, and callback
behavior, not just result ranges. In particular:

- `random_index` accepts the C++ `std::size_t` domain, which may extend beyond
  Python's `sys.maxsize`.
- Singleton `random_value` and `sample(..., 1)` consume one bounded draw;
  `shuffle` on zero or one element consumes none.
- The native `Generator.shuffle` path, including an unchanged inherited method,
  consumes its full index schedule under one lock before mutable-sequence
  callbacks. Callback failure may leave partial mutation, but the full schedule
  remains consumed.
- Indexes and weighted draws returned by injected custom behavior must be
  validated. Do not extend native trust to subclasses or monkeypatched methods.
- `Generator` class factories preserve `cls`, and `QuantumMonty` initializes
  its truffle strategy lazily.
- `FlexCat` validates selector ownership and configuration and materializes all
  categories before randomized selector construction begins. Failures after
  selector construction starts do not roll back already consumed randomness.
- Stateful selectors and value engines are not promised thread-safe. A native
  generator lock protects its engine, not surrounding Python selection state.

Regression tests should assert the next draw where a change could silently
alter a seeded sequence, and should exercise invalid injected results before a
fast path is treated as trusted.

## Lint and test

Run the same static checks used by CI:

```console
uv run ruff check .
uv run ruff format --check .
```

The test surfaces have distinct jobs:

- Ordinary tests prove deterministic behavior, bounds, error contracts, API
  shape, seeding, thread behavior, and process behavior. They must be fast and
  reliable: `uv run pytest -m "not statistical" -n auto`.
- Statistical tests check declared distributions with explicit hypotheses,
  sample sizes, tolerances, and deterministic seeds: `uv run pytest -m statistical`.
  They do not prove security and must not become vague “looks random” tests.
- Benchmarks measure performance only. They cannot prove correctness or
  distribution quality and ordinary CI never fails on timing differences.

Python 3.14 is the supported interpreter series. CI exercises it on Ubuntu,
macOS, and Windows, and the wheel workflow covers every approved native target.
Local development pins the current approved patch release in `.python-version`.

## Benchmarks

The repository-owned harness is under `benchmarks/` and is not part of Fortuna's
installed public API. List and run cases with:

```console
uv run python -m benchmarks --list
uv run python -m benchmarks --suite fortuna-scalar
uv run python -m benchmarks --suite fortuna-bulk
```

For usage, JSON artifacts, controlled baseline comparisons, and case-authoring
rules, read `benchmarks/README.md`. CI performs only a short reference-case smoke
run. Performance regression decisions require comparable controlled hardware.

## Build and verify locally

Build both the source distribution and the native wheel:

```console
uv build --no-sources
```

Do not treat a successful build as installation proof. Install the wheel into a
fresh environment and import it without the source checkout on `sys.path`:

```console
uv venv --python 3.14.6 .wheel-check
uv pip install --python .wheel-check/bin/python dist/*.whl
cd /tmp
/path/to/Fortuna/.wheel-check/bin/python -c \
  "import Fortuna; print(Fortuna.storm_version())"
```

On Windows, use `.wheel-check\Scripts\python.exe` instead. Verify wheel contents,
module import, version metadata, vendored Storm version, and a small deterministic
seeded call. The CI build job performs the isolated import check for the native
Linux wheel.

The release-wheel workflow uses cibuildwheel to create CPython 3.14 wheels for:

- macOS arm64 and x86_64;
- manylinux x86_64 and aarch64;
- Windows AMD64.

Each wheel is imported and asked for its Storm version before it is retained as
a GitHub Actions artifact. Linux aarch64 is built and tested under QEMU, while
both macOS architectures and Windows AMD64 use native hosted runners. Download
the artifacts and smoke-test representative wheels on real target machines
before treating a release candidate as complete.

## Bump the release version

A release version is repeated deliberately at packaging and verification
boundaries. Update all of these in one change:

- `pyproject.toml` project metadata;
- `meson.build` project metadata;
- `src/Fortuna/__init__.py` public version;
- version assertions in `.github/workflows/ci.yml` and
  `.github/workflows/wheels.yml`;
- the release heading in `CHANGELOG.md`.

Refresh `uv.lock`, then build from committed source and run the isolated wheel
and source-distribution checks before tagging.

## The publication boundary

Building is authorized; publishing is not. The repository workflows stop after
creating and verifying GitHub artifacts. They intentionally have:

- no PyPI upload step;
- no PyPI environment or trusted-publishing permission;
- no access to a publish token;
- no invocation of `uv publish` or another uploader.

Do not add a local publishing command to routine development instructions. A
future PyPI release requires an explicit human decision after the version,
license, source distribution, complete wheel set, installation checks, changelog,
and release notes have all been reviewed. Possession of credentials does not
authorize their use.
