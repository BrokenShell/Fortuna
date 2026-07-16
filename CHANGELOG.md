# Changelog

## 6.0.0 - Unreleased

Fortuna 6 is a clean, intentionally breaking reconstruction.

### Added

- MIT licensing.
- Python 3.14 support.
- Fortuna-owned `Generator` instances and deterministic stream derivation.
- Process-local entropy defaults with thread isolation and fork recovery.
- Serialized access to shared explicit generators.
- Native bulk generation through the keyword-only `count` argument.
- Honest positional-profile names and the retained `QuantumMonty` strategy.
- Structured correctness, statistical, concurrency, and benchmark suites.
- Modern `uv` and `meson-python` build workflow.

### Changed

- Vendored Storm was upgraded from 4.0.4 to the immutable 5.0.1 release.
- `seed(0)` is deterministic. Entropy construction is explicit.
- Ranges now follow directed Python `range` semantics.
- Indexes, dice sizes, and counts reject historical negative sentinels.
- Callable resolution propagates user exceptions and has a recursion guard.
- Positional recipes use names matching their actual algorithms.
- `random_below(2**64)` covers the complete unsigned 64-bit result domain.
- Distribution inputs use explicit safe domains; floating results are finite or
  raise `OverflowError` instead of leaking NaN, infinity, or saturated sentinels.
- `shuffle` uses the native Knuth-B loop with one lock per explicit-generator
  operation instead of routing every swap through Python selector machinery.
- `canonical` uses dedicated scalar and bulk paths that preserve its seeded
  sequence while avoiding generic validation, dispatch, and per-value engine
  preparation.
- Priority scalar APIs use dedicated native paths instead of paying the generic
  bulk dispatcher and validation cost for each individual draw.
- Uniform value selection has direct exact-tuple and native-generator paths
  while preserving snapshot semantics for mutable inputs.

### Removed

- MonkeyScope and the `scope` installation extra.
- `fortuna_extras`, Docker experiments, and publishing shell scripts.
- Numeric-limit and clamp helpers.
- ZeroCool, signed sentinel behavior, MultiChoice, TruffleShuffle2,
  FloatDistributionRange, duplicate shuffle APIs, and the public
  WeightedChoice base.
- Historical positional-profile names and redundant profile mixtures.
