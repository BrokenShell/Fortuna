# Developing Fortuna

Fortuna uses uv for project environments, locked dependencies, test commands,
and package builds. The compiled extension is built by Meson through
meson-python.

## Set up the checkout

Install [uv](https://docs.astral.sh/uv/), then run from the repository root:

```console
uv sync --frozen --group dev --no-build-isolation-package Fortuna --reinstall-package Fortuna
uv run python -c "import Fortuna; print(Fortuna.storm_version())"
```

`--frozen` makes the checked-in `uv.lock` authoritative for the development,
test, and native editable-build toolchain. Cython, Meson, meson-python, and
Ninja are explicit development dependencies. The setup command disables build
isolation only for the editable Fortuna checkout; `tool.uv` also records that
requirement so ordinary `uv sync` and `uv run` commands cannot build Fortuna in
a temporary isolated environment. Meson's loader therefore records the current
environment's persistent Ninja path. The same tools are pinned in
`build-system.requires` because
standalone PEP 517 builds do not consume `uv.lock`. Review both sets of pins
deliberately when updating the toolchain. When changing dependencies, update
the project metadata and lock together with `uv add`, `uv remove`, or `uv lock`;
review both changes.

After changing Cython, C++, or Meson inputs, force an editable rebuild if uv has
not already detected it:

```console
uv sync --reinstall-package Fortuna --group dev
```

If an editable loader created before this configuration still references a
deleted `.cache/uv/builds-v0/.tmp*/bin/ninja`, discard the cached editable wheel
and rebuild it in the project environment:

```console
uv sync --reinstall-package Fortuna --no-cache
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
generator-like objects own synchronization for their overrides. Fork after
concurrent use of a shared explicit generator has quiesced because the child
could otherwise inherit its native mutex in a locked state. Keep the
concurrency and process tests aligned with this contract.

## API hardening contracts

Optimization must preserve draw schedules, validation boundaries, and callback
behavior, not just result ranges. In particular:

- `random_below` reflects negative inputs around zero, while `random_index`
  offsets negative inputs into Python's negative-index interval. Their positive
  draws and native magnitudes remain the source sequences for those
  continuations.
- `random_index` accepts positive and negative magnitudes through the C++
  `std::size_t` domain, which may extend beyond Python's `sys.maxsize`.
- Singleton `random_value` and `sample(..., 1)` consume one bounded draw;
  `shuffle` on zero or one element consumes none.
- The native `Generator.shuffle` path, including an unchanged inherited method,
  consumes its full index schedule under one lock before mutable-sequence
  callbacks. Callback failure may leave partial mutation, but the full schedule
  remains consumed.
- Indexes and weighted draws returned by injected custom behavior must be
  validated. Apply the untrusted-input boundary to subclasses and monkeypatched
  methods.
- `Generator` class factories preserve `cls`, and `RandomValue` initializes its
  truffle strategy lazily. Construction, uniform selection, triangular
  selection, and cycling must not pay the shuffle cost or advance the truffle
  schedule.
- A bare `RandomValue` call is uniform. Keep its bound methods
  (`uniform`, `cycle`, `truffle_shuffle`, and the three triangular profiles)
  independently callable; `take` repeats the default uniform strategy.
- Callable resolution belongs to value engines internally. Preserve exception
  propagation and the cycle and depth guards.
- `WeightedChoice` accepts only relative `(weight, value)` tables. Validate
  finite, nonnegative weights, a positive finite total, and untrusted injected
  draws before selection.
- Callers own synchronization for stateful value engines. A native generator
  lock protects its engine; surrounding Python selection state requires its own
  synchronization.

Regression tests should assert the next draw where a change could silently
alter a seeded sequence, and should exercise invalid injected results before a
fast path is treated as trusted.

## Experimental work

Experimentation belongs in Fortuna. Experiments have an explicitly provisional
contract until they graduate into the stable API.

Early work should live under `experiments/<name>/` and remain outside the built
wheel and `Fortuna.__all__`. Each experiment needs a short README stating:

- the question or hypothesis it explores;
- what, if anything, is safe for users to rely on;
- how to run its tests or benchmarks;
- the evidence that would justify promotion; and
- the condition for concluding or removing the experiment.

Experimental results may be documented, benchmarked, and shared. Stable
compatibility begins when an experiment graduates through a deliberate release
change with a durable name and contract, correctness tests, relevant
statistical or performance evidence, user documentation, and migration notes
where needed. An installed experimental namespace or separate distribution
requires its own design decision.

This structure gives invention a clear path through exploration, evidence, and
graduation. Concluded experiments should leave a brief result when the lesson
is useful, then be archived or removed.

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
  Security claims require a separate threat model, and each statistical test
  must state more than “looks random.”
- Benchmarks measure performance. Correctness and distribution quality belong
  to their corresponding test suites, and ordinary CI ignores timing
  differences.

Python 3.14 is the supported interpreter series. CI exercises it on Ubuntu,
macOS, and Windows, and the wheel workflow covers every approved native target.
Local development pins the current approved patch release in `.python-version`.

## Benchmarks

The repository-owned benchmark harness lives under `benchmarks/`. List and run
cases with:

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

A release check includes installing the built wheel into a fresh environment
and importing it with the source checkout absent from `sys.path`:

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

Each wheel is imported and asked for its Storm version before it is saved as
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
