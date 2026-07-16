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
algorithms and stream derivation. Standard-library distribution transforms,
including profiles built from them, can produce different exact sequences under
libc++, libstdc++, and Microsoft's standard library even with the same seed.

## Renamed positional profiles

| Fortuna 5 | Fortuna 6 |
| --- | --- |
| `front_linear` | `front_triangular` |
| `middle_linear` | `center_triangular` |
| `back_linear` | `back_triangular` |
| `quantum_linear` | `mixed_triangular` |
| `front_gauss` | `front_exponential` |
| `middle_gauss` | `center_normal` |
| `back_gauss` | `back_exponential` |
| `quantum_gauss` | `mixed_exponential_normal` |
| `middle_poisson` | `edge_poisson` |

`quantum_poisson` was distributionally redundant and has been removed.
`quantum_monty` remains as an equal strategy mixture of the nine front,
center/edge, and back triangular, exponential/normal, and Poisson profiles.

## Other renames

| Fortuna 5 | Fortuna 6 |
| --- | --- |
| `flatten` | `resolve` |
| `flat=` | `resolve_callables=` |
| `plus_or_minus_linear` | `plus_or_minus_triangular` |
| `plus_or_minus_gauss` | `plus_or_minus_normal` |
| `version` | `__version__` |

## Removed interfaces

The following concepts do not have compatibility replacements:

- Negative `random_below`, negative indexes, signed dice, and reordered ranges.
- `ZeroCool`; use `IndexProfile` and `IndexSelector`.
- `DistributionRange` and `FloatDistributionRange`.
- `MultiChoice`.
- `TruffleShuffle2` and the `truffle_shuffle` function factory.
- `knuth_a` and `fisher_yates`; use `shuffle`.
- Numeric limit and clamp helpers.
- The public `WeightedChoice` base and `cumulative_weighted_choice` function.
- MonkeyScope integration and `Fortuna[scope]`.

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
