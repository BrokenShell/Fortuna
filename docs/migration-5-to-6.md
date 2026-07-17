# Migrating from Fortuna 5 to Fortuna 6

Fortuna 6 deliberately does not carry a compatibility facade. Removed names
raise normal import or attribute errors instead of emitting deprecation
warnings.

The [Fortuna 6 API reference](api.md) documents the complete replacement
surface.

## Engine and seed behavior

| Fortuna 5 | Fortuna 6 |
| --- | --- |
| Global Storm 4 engine behavior | Fortuna-owned thread-local module default |
| `seed(0)` requested implicit entropy | `seed(0)` is deterministic |
| Multiprocessing behavior was implicit | Module defaults invalidate after fork |
| No owned Python engine | `Generator`, `from_entropy`, and `for_stream` |

An explicitly seeded `Generator` retains copied deterministic state after a
fork. Derive a generator for each deterministic worker:

```python
generator = Fortuna.for_stream(root_seed, worker_id)
```

Generators created with `from_entropy()` or later reseeded with
`reseed_from_entropy()` are entropy-managed and lazily reseed after detecting a
forked child. Built-in native methods sharing one `Generator` are serialized,
including methods inherited unchanged by a subclass, but their assignment to
threads is scheduling-dependent. Subclasses and custom generators own
synchronization for their overrides. Do not fork while another thread is
actively using that shared generator.

Exact cross-platform stream stability applies to Fortuna/Storm-owned bounded
integer algorithms, bounded-only triangular profiles, stream derivation,
uniform value selection, sampling, and shuffle. Standard-library probability
distributions, `random_float`, custom floating transforms, TruffleShuffle's
Poisson movement, and WeightedChoice's real draw are deterministic within one
platform and toolchain build but are not exact cross-platform sequence
contracts.

## Retained positional profiles

| Fortuna 5 | Fortuna 6 |
| --- | --- |
| `front_linear` | `front_triangular` |
| `middle_linear` | `center_triangular` |
| `back_linear` | `back_triangular` |

These are the only public positional index profiles in Fortuna 6. The
mixed, exponential/normal, Poisson, and quantum profile families were removed
instead of being carried forward under aliases. The standard probability
distribution primitives, including `normal_variate`, `exponential_variate`,
and `poisson_variate`, remain public.

## Other renames

| Fortuna 5 | Fortuna 6 |
| --- | --- |
| `plus_or_minus_linear` | `plus_or_minus_triangular` |
| `plus_or_minus_gauss` | `plus_or_minus_normal` |
| `version` | `__version__` |

The former `flatten`/`resolve` helper is not public in Fortuna 6. Callable value
resolution remains an option on `RandomValue`, `TruffleShuffle`, and
`WeightedChoice` through `resolve_callables=`.

## Prepared value engines

`RandomValue` now owns the small, useful prepared-selector interface formerly
associated with `QuantumMonty`:

```python
loot = Fortuna.RandomValue(["copper", "potion", "wand"])

uniform = loot()                  # bare call is uniform
front_loaded = loot.front_triangular()
ordered = loot.cycle()

loot_gen = loot.front_triangular  # retain a strategy as a callable
another = loot_gen()
```

The complete retained strategy set is `uniform`, `cycle`, `truffle_shuffle`,
`front_triangular`, `center_triangular`, and `back_triangular`. The object also
provides `take`; its default repeated strategy is uniform. `QuantumMonty` is
removed without an alias.

`WeightedChoice` accepts relative `(weight, value)` pairs and replaces
`RelativeWeightedChoice`. Cumulative-threshold tables and
`CumulativeWeightedChoice` have no replacement:

```python
rarity = Fortuna.WeightedChoice([(80, "common"), (18, "rare"), (2, "legendary")])
```

## Negative integer continuations

Fortuna 6 retains the two intentional negative continuations from Fortuna 5:

```python
random_below(-10)  # [-9, 0]
random_index(-10)  # [-10, -1]
```

`random_below` reflects the ordinary positive draw around zero, while
`random_index` preserves Python's equivalence between positive and negative
indexes. `random_range` instead follows Python's directed `range` contract:
`random_range(-10)` is empty and raises `ValueError`, while
`random_range(-10, 0)` is valid.

Unlike Fortuna 5, Fortuna 6 rejects zero for both bounded functions. Zero is a
true empty-domain singularity: there is no integer below zero in the requested
interval and no index into a sequence of size zero.

## Removed interfaces

The following concepts do not have compatibility replacements:

- Signed dice and reordered ranges.
- `random_uint`; use `random_below(2**64)` for a full-domain unsigned draw, or
  the bounded API whose interval contract matches the actual use case.
- `ZeroCool`, `IndexProfile`, and `IndexSelector`.
- `DistributionRange` and `FloatDistributionRange`.
- `MultiChoice`.
- `TruffleShuffle2` and the `truffle_shuffle` function factory.
- `knuth_a` and `fisher_yates`; use `shuffle`.
- Numeric limit and clamp helpers.
- `FlexCat`; compose ordinary mappings and retained value engines where needed.
- `QuantumMonty`; use `RandomValue` and an explicit retained strategy.
- Public `resolve`, `RelativeWeightedChoice`, `CumulativeWeightedChoice`, and
  `cumulative_weighted_choice`.
- Mixed, exponential/normal, Poisson, and quantum positional profiles.
- MonkeyScope integration and `Fortuna[scope]`.

Fortuna does not export compatibility aliases for these names. This is a hard
API cut intended to leave the retained functionality with a smaller, clearer
surface.

## Validation

Fortuna 6 uses exceptions rather than public `assert` statements:

- `TypeError` for an incompatible type.
- `ValueError` for a value outside the function's domain.
- `OverflowError` for an integer outside the required native representation.

Empty collections, empty ranges, invalid probabilities, NaN, infinity, zero
steps, and invalid distribution parameters are rejected before sampling.
Floating distribution draws return finite values or raise `OverflowError`;
Fortuna does not return NaN, infinity, or saturated integer sentinels as valid
distribution results.
