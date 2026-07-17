# Changelog

## 6.0.4

Fortuna 6.0.4 tunes release builds for their native compiler and architecture
while preserving public behavior and seeded schedules.

### Added

- Public benchmark coverage for module-level and explicit-generator shuffle
  paths from empty inputs through one million elements.

### Changed

- macOS arm64 release wheels enable link-time optimization. Controlled
  fresh-process measurements showed approximately 13–18% faster public shuffle
  throughput from one thousand through one million elements, with priority
  selector and numeric APIs remaining within the accepted regression ceiling.
- Windows release wheels explicitly activate MSVC, preventing an unrelated
  compiler on `PATH` from introducing nonstandard runtime dependencies.
- Windows release wheels bundle their required MSVC C++ Standard Library DLL,
  allowing imports on pristine systems without a separate runtime installer.
- macOS x86_64, Linux, and Windows retain the verified non-LTO release policy.

## 6.0.3

Fortuna 6.0.3 adopts Storm's prepared selector primitives at the native boundary
without changing Fortuna's public value-engine contracts or seeded schedules.

### Added

- A practical usage guide with game-oriented examples and an algorithm guide
  describing Fortuna's engine, reproducibility, and selector designs.
- A documented path for developing and sharing experiments without presenting
  them as stable installed APIs.

### Changed

- The public documentation is organized into a concise project README, a
  practical usage guide, an API contract reference, algorithm notes, a Fortuna
  5 migration guide, and contributor documentation.
- Historical API context is centralized in the migration guide and changelog,
  keeping current-product documentation focused on Fortuna 6.
- Vendored Storm was upgraded from 5.0.1 to the immutable 5.0.2 release.
- Exact native `Generator` and module-level `TruffleShuffle` paths now keep the
  wide-index permutation, cursor, and Poisson distribution in Storm while value
  and callable resolution remain in Fortuna.
- Exact native `WeightedChoice` paths now use Storm's prepared cumulative-weight
  selector, avoiding a Python linear scan on every draw.
- `ability_dice` inherits Storm 5.0.2's fixed-size top-three insertion path.
- Custom generators and generator subclasses retain Fortuna's validated Python
  fallbacks. `WeightedChoice` also continues to validate monkeypatched module
  `random_float` draws.

## 6.0.2

Fortuna 6.0.2 removes low-value experiments and gives the surviving value
engines a smaller, faster, more direct API.

### Added

- A single relative-weight `WeightedChoice` value engine.
- Focused benchmark coverage for every retained `RandomValue` strategy.

### Changed

- A bare `RandomValue(items)()` now performs uniform selection. The object also
  exposes bound `uniform`, `cycle`, `truffle_shuffle`, `front_triangular`,
  `center_triangular`, and `back_triangular` methods.
- `RandomValue` now carries the useful prepared-selector implementation and
  ergonomics formerly associated with `QuantumMonty`.
- Relative weighted selection is exposed directly as `WeightedChoice` instead
  of splitting the concept across relative and cumulative classes.
- Callable resolution remains an internal value-engine behavior with cycle and
  depth guards; it is no longer a separate public helper.
- Prepared value engines now inline their hot selection and callable-resolution
  paths. Uniform, cyclic, triangular, Truffle, and weighted pulls avoid generic
  helper dispatch while preserving injected-generator validation and draw
  schedules.

### Removed

- The public `random_uint` API. `random_below(2**64)` remains the full unsigned
  64-bit draw.
- `QuantumMonty`, `FlexCat`, `IndexProfile`, and `IndexSelector`.
- `RelativeWeightedChoice` and `CumulativeWeightedChoice`; relative tables use
  `WeightedChoice`, while cumulative-threshold tables have no replacement.
- All positional profiles except `front_triangular`, `center_triangular`, and
  `back_triangular`, including the former mixed, exponential/normal, Poisson,
  and quantum recipes.
- Compatibility aliases for the removed selector and profile APIs.

## 6.0.1

Fortuna 6 is a clean, intentionally breaking reconstruction.

### Added

- MIT licensing.
- Fortuna-owned `Generator` instances and deterministic stream derivation.
- Process-local entropy defaults with thread isolation and fork recovery.
- Serialized access to shared explicit generators.
- Native bulk generation through the keyword-only `count` argument.
- Honest positional-profile names and the retained `QuantumMonty` strategy.
- Structured correctness, statistical, concurrency, and benchmark suites.
- Modern `uv` and `meson-python` build workflow.

### Changed

- Python 3.14, already supported by Fortuna 5, became Fortuna 6's required
  runtime line.
- Vendored Storm was upgraded from 4.0.4 to the immutable 5.0.1 release.
- `seed(0)` is deterministic. Entropy construction is explicit.
- Ranges now follow directed Python `range` semantics.
- `random_below` and `random_index` restore their distinct negative
  continuations while rejecting their shared zero singularity; `random_range`
  retains directed Python `range` semantics.
- Dice sizes and counts reject historical negative sentinels.
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
- ZeroCool, signed dice sentinels, MultiChoice, TruffleShuffle2,
  FloatDistributionRange, duplicate shuffle APIs, and the public
  WeightedChoice base.
- Historical positional-profile names and redundant profile mixtures.
