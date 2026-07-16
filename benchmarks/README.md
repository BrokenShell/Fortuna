# Fortuna benchmarks

This directory is Fortuna-owned development infrastructure. It is not installed
as part of the runtime package and nothing here is part of Fortuna's public API.
Correctness and distribution validation belong in `tests/`; these measurements
answer only performance questions.

## Run

From the repository root:

```console
uv run python -m benchmarks
uv run python -m benchmarks --suite fortuna-scalar
uv run python -m benchmarks --suite shuffle-algorithms
uv run python -m benchmarks --case '*shuffle*'
uv run python -m benchmarks --list
```

For a quick harness smoke test rather than a meaningful measurement:

```console
uv run python -m benchmarks --suite reference --case random --warmups 0 --samples 2 --target-ms 1
```

The defaults perform three warmups followed by eleven independent samples.
Calibration chooses enough calls to target 50 milliseconds per sample. Every
reported scalar measurement is in nanoseconds per call. Bulk measurements are
in nanoseconds per generated value and also report values per second.

## Artifacts and baselines

Write a machine-readable artifact alongside the table:

```console
uv run python -m benchmarks --output benchmark-results/local.json
```

The JSON records the raw normalized samples, median, minimum, quartiles, IQR,
median absolute deviation, runner configuration, Git state, Python runtime,
platform, CPU availability, and Fortuna/Storm versions when importable.

Compare a later run made on the same controlled machine:

```console
uv run python -m benchmarks \
  --baseline benchmark-results/baseline.json \
  --threshold 10 \
  --output benchmark-results/candidate.json
```

Add `--fail-on-regression` only in a controlled release-performance job. Shared
CI runners are too noisy for timing gates. Ordinary CI should execute a short
smoke run to prove the harness and all available cases still work.

The comparator rejects differences in its recorded machine, operating-system,
Python runtime and compiler identity, CPU, affinity, thread-count, and
`values_per_call` metadata. Case identifiers must remain tied to the same
arguments and setup. The explicit `--allow-incomparable-baseline` escape hatch
exists for exploratory analysis; such a comparison is not release evidence.

A comparison is meaningful only when hardware, power state, operating system,
Python build, compiler options, workload, and process conditions are comparable.
The artifact does not capture native extension compiler flags or every workload
argument, so release evidence must control and review those separately. The
runner does not pretend metadata can correct an uncontrolled experiment.

## Case design

`BenchmarkCase.operation` is a zero-argument callable. For mutable input or any
state that must be fresh for each independent sample, provide `setup` instead:

```python
def setup_shuffle():
    values = list(range(1000))
    return lambda: shuffle(values)

BenchmarkCase("fortuna-scalar", "shuffle-1000", setup=setup_shuffle)
```

Setup runs outside the timed interval for calibration, every warmup, and every
measured sample. It must return the operation to time.

Bulk cases declare `unit="value"` and the number produced by each call:

```python
BenchmarkCase(
    "fortuna-bulk",
    "random-ints-10000",
    operation=lambda: random_int(-1000, 1000, count=10_000),
    unit="value",
    values_per_call=10_000,
)
```

All assumptions about Fortuna's API live in `suites/fortuna.py`. Unavailable
cases are reported explicitly and cause a failing exit status. Use
`--allow-skips` only for a deliberate partial-development run; release evidence
must execute every selected case.

## Interpretation

The median is the primary result. Minimum can expose the best observed path but
is not described as “typical.” IQR describes the middle half of samples, and MAD
is a robust measure of sample dispersion. Raw samples remain in JSON so later
analysis is possible without rerunning the benchmark.

Benchmarks must not:

- claim that fast output is statistically correct;
- use timing assertions in the normal test suite;
- silently discard errors;
- include input construction in a measurement unintentionally;
- paste stale result transcripts into project documentation.

The `shuffle-algorithms` suite is an internal native-loop comparison. It runs
Knuth-B and reverse Fisher-Yates through same-shaped Cython entry points, the
same Storm generator, module ownership model, and lock policy. It resets the
generator and creates a fresh list outside every timed sample; each timed batch
then repeatedly shuffles that list. The loops differ only in their bounded-index
order and swap traversal.
