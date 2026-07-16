# Fortuna

Fortuna is a fast random generation toolkit with explicit engine ownership,
deterministic streams, honest positional profiles, and native bulk generation.
Fortuna's native shuffle uses Knuth-B, optimized for large workloads while
remaining competitive at ordinary sizes.

Fortuna 6 is a clean break from the historical API. It supports Python 3.11
through 3.14, vendors the immutable Storm 5.0.1 header, and is licensed under
MIT.

> Fortuna 6.0.0 is under active development and has not been published to PyPI.

> **Security:** Fortuna uses MT19937-64 and is not a cryptographically secure
> random number generator. Do not use it for passwords, tokens, keys, secrets,
> authentication, cryptography, or security decisions. Python's `secrets`
> module is the appropriate standard-library starting point for those tasks.
> Entropy-seeded construction does not make Fortuna cryptographically secure.

## Development installation

```bash
uv sync --group dev --no-build-isolation-package Fortuna --reinstall-package Fortuna
```

## Engine model

Module-level functions use a Fortuna-owned thread-local generator. Each thread
starts from process-local entropy, and a forked child invalidates the inherited
module default before its next draw.

Seeded explicit generators are deterministic:

```python
import Fortuna

first = Fortuna.Generator(42)
second = Fortuna.Generator(42)
assert first.random_int(1, 100) == second.random_int(1, 100)

worker = Fortuna.for_stream(42, "worker-3")
independent = Fortuna.from_entropy()
```

`seed(value)` deterministically seeds only the calling thread's module default,
including `seed(0)`. Built-in native methods that share one `Generator` across
threads are serialized, including methods inherited unchanged by a subclass;
scheduling still determines which thread receives each draw. Subclasses own
synchronization for their overrides. A
`Generator(seed)` or `for_stream(root_seed, stream_id)` inherited through
`fork` deliberately keeps its copied deterministic state; derive a distinct
stream for each worker when workers must not repeat one another. A generator
created by `from_entropy()` or later passed to `reseed_from_entropy()` is
entropy-managed instead: a forked child detects its new process identity and
reseeds that generator before its next draw. A spawned worker starts a new
interpreter and initializes its own state.

Do not fork while another thread is actively using a shared explicit generator;
the child could inherit that generator's native mutex in a locked state.

Fortuna's bounded integer, index, range, dice, canonical, bounded-triangular
profile, stream-derivation, and collection draw-schedule algorithms are stable
across supported platforms throughout the Fortuna 6 line. Other floating-point
transforms—including custom triangular, Pareto, and von Mises transforms—and
profiles or distributions built on them are repeatable within one platform and
toolchain build, but their exact seeded sequences are not a cross-platform
contract.

## Scalar and bulk generation

Numeric generation functions and their `Generator` methods accept an optional
keyword-only `count`:

```python
value = Fortuna.random_int(-10, 10)
values = Fortuna.random_int(-10, 10, count=100_000)
```

Bulk generation performs the sampling loop natively without holding the Python
GIL and returns a list. `count=0` returns an empty list; negative counts are an
error.

## Development commands

```bash
uv run pytest
uv run ruff check .
uv run python -m benchmarks
uv build
```

Correctness tests and statistical validation live in `tests/`. Performance
measurement lives in `benchmarks/`; benchmark timing is not an ordinary CI pass
condition.

Fortuna's native Knuth-B shuffle is deliberately optimized for larger
workloads, where its forward traversal has shown the clearest advantage over
reverse Fisher-Yates in this project's controlled benchmarks.

See the [API reference](docs/api.md) for the complete public surface and the
[migration guide](docs/migration-5-to-6.md) for renamed and removed interfaces.
