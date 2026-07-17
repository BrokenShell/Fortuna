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

For a quick harness smoke test:

```console
uv run python -m benchmarks --suite reference --case random --warmups 0 --samples 2 --target-ms 1
```

The defaults perform three warmups followed by eleven independent samples.
Calibration chooses enough calls to target 50 milliseconds per sample. Every
reported scalar measurement is in nanoseconds per call. Bulk measurements are
in nanoseconds per generated value and also report values per second.

The unfiltered suite is intentionally exhaustive and currently takes roughly
four minutes on the primary development machine. During implementation, select
the affected suite or cases; run the complete inventory for baseline and
release evidence.

## Artifacts and baselines

Write a machine-readable artifact alongside the table:

```console
uv run python -m benchmarks --output benchmark-results/local.json
```

The JSON records the raw normalized samples, median, minimum, quartiles, IQR,
median absolute deviation, runner configuration, Git state, Python runtime,
platform, CPU availability, Fortuna/Storm versions, and the loaded native
extension's SHA-256 identity. When the extension came from a discoverable Meson
build directory, the artifact also records its compiler identities, selected
build options, and build-tool versions.

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

`--fail-on-regression` is a strict gate: it requires `--baseline`, and every
selected case must have a successful baseline result with the same explicitly
declared workload identity. Use `--require-complete-baseline` to enforce those
completeness rules without making the measured delta determine the exit status.
Schema-v1 artifacts and cases without declared workload metadata remain usable
for exploratory comparisons, but cannot pass a strict gate.

The comparator rejects differences in its recorded machine, operating-system,
Python runtime and compiler identity, CPU, affinity, thread-count, and
discoverable native compiler/build options. The extension hash is provenance
only because a candidate binary is expected to differ from its baseline. The
comparator also rejects changed metrics, `values_per_call`, or serialized
workload identities. The explicit
`--allow-incomparable-baseline` escape hatch exists for exploratory analysis;
such a comparison is not release evidence.

A comparison is meaningful only when hardware, power state, operating system,
Python build, compiler options, workload, and process conditions are comparable.
Native build metadata is best-effort: an installed wheel may expose the binary
hash but not its original Meson introspection files. Release evidence must still
control and review conditions that are not discoverable. The runner does not
pretend metadata can correct an uncontrolled experiment.

## Case design

`BenchmarkCase.operation` is a zero-argument callable. For mutable input or any
state that must be fresh for each independent sample, provide `setup` instead:

```python
def setup_shuffle():
    values = list(range(1000))
    return lambda: shuffle(values)

BenchmarkCase(
    "fortuna-scalar",
    "shuffle-1000",
    setup=setup_shuffle,
    workload={
        "args": [],
        "kwargs": {},
        "seed": 8675309,
        "input": {"kind": "integer-list", "size": 1000},
        "setup_variant": "fresh-list-and-reset-generator-per-sample",
    },
)
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
    workload={
        "args": [-1000, 1000],
        "kwargs": {"count": 10_000},
        "seed": 8675309,
        "input": None,
        "setup_variant": "direct-operation",
    },
)
```

Workload metadata is deliberately explicit and JSON-safe. It always records
`args`, `kwargs`, `seed`, `input`, and `setup_variant`; the canonical serialized
form is SHA-256 signed in the artifact. A changed argument, seed, input shape,
or setup policy therefore cannot silently reuse an old timing baseline. Opaque
callables are not introspected. A case that omits `workload` is marked
`declared: false` and is excluded from strict comparisons until its suite owner
describes it.

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

Fortuna selects Knuth-B for its large-workload behavior. Current macOS arm64
release-build measurements show a substantial advantage at one million
elements, while intermediate sizes are close and can exchange small wins. The
benchmark suite keeps both native loops visible so the choice can be revisited
with its rationale attached to reproducible evidence.
