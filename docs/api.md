# Fortuna 6 API

Everything documented here is exported directly from `Fortuna`. Names not in
`Fortuna.__all__` are implementation details and may change without notice.

Fortuna uses MT19937-64. It is **not** a cryptographically secure random number
generator; use `secrets` for passwords, tokens, keys, and other security work.

## Versions and engines

| API | Meaning |
| --- | --- |
| `__version__` | The installed Fortuna version string. |
| `storm_version()` | The version string reported by the vendored Storm engine. |
| `Generator(seed=0)` | An explicit generator deterministically initialized from an unsigned 64-bit seed. `0` is an ordinary deterministic seed. |
| `seed(value=0)` | Deterministically seed the calling thread's module-level generator. Other threads and explicit generators are unaffected. |
| `from_entropy()` | Construct an entropy-managed explicit `Generator`. |
| `for_stream(root_seed, stream_id)` | Deterministically derive an explicit `Generator` from an unsigned 64-bit root seed and an `int`, `str`, or `bytes` stream identifier. Identifier types are distinct. |

The equivalent constructors are also available as `Generator.from_entropy()`
and `Generator.for_stream(root_seed, stream_id)`. When invoked on a `Generator`
subclass, both class factories construct and return that subclass through
`cls(...)`; a subclass constructor must return an instance of `cls`. An explicit
generator also provides `generator.seed(value=0)` and
`generator.reseed_from_entropy()`.

Module-level generation functions use a Fortuna-owned thread-local generator.
The initial state in each thread comes from process-local entropy. After
`fork`, a child invalidates an inherited module default before its next draw.
An entropy-managed explicit generator also reseeds on its first child-process
draw. A deterministically seeded explicit generator intentionally retains its
copied state after `fork`; use `for_stream` to assign a distinct deterministic
stream to each worker.

Built-in native methods on one `Generator` instance are serialized, including
methods inherited unchanged by a subclass. This prevents concurrent engine
mutation, but the order in which threads receive draws depends on scheduling.
A subclass or custom generator is responsible for synchronizing its overrides.
Use one derived generator per worker when result
assignment must be reproducible. Do not fork while another thread is actively
using a shared explicit generator: the child could inherit its native mutex in
a locked state.

## Module functions and `Generator` methods

Every numeric generation function below is available both as a module function
and as a method with the same name and arguments:

```python
import Fortuna

module_value = Fortuna.random_int(1, 6)
generator = Fortuna.Generator(42)
owned_value = generator.random_int(1, 6)
```

The module form draws from the calling thread's module default. The method form
draws from that explicit generator.

### Bulk generation

Every numeric generation function in the following four sections accepts the
keyword-only argument `count=None`:

```python
one = Fortuna.normal_variate(0.0, 1.0)
many = Fortuna.normal_variate(0.0, 1.0, count=100_000)
```

With `count=None`, the return value is a scalar. A nonnegative integer `count`
returns a list of exactly that length; `count=0` returns `[]`. Bulk sampling
runs in the native extension without holding the Python GIL. Arguments are
validated before the engine advances.

### Boolean, integer, and dice generation

| API | Result |
| --- | --- |
| `percent_true(percent=50.0, *, count=None)` | Boolean with the given probability expressed in `[0, 100]`. |
| `bernoulli_variate(probability=0.5, *, count=None)` | Boolean with success probability in `[0, 1]`. |
| `random_below(limit, *, count=None)` | Uniform integer in `[0, limit)` for positive `limit` and `(limit, 0]` for negative `limit`; `limit` must be nonzero and `abs(limit) <= 2**64`. |
| `random_index(size, *, count=None)` | Uniform integer in `[0, size)` for positive `size` and `[size, 0)` for negative `size`; `size` must be nonzero and `abs(size) <= SIZE_MAX`. |
| `random_int(low, high, *, count=None)` | Uniform signed 64-bit integer in the inclusive interval `[low, high]`. |
| `random_range(start, stop=None, step=1, *, count=None)` | Uniform member of the nonempty integer range described by Python `range` arguments. Inputs must fit the signed 64-bit domain. |
| `d(sides=20, *, count=None)` | One die roll in the inclusive interval `[1, sides]`. |
| `dice(rolls=1, sides=20, *, count=None)` | Sum of `rolls` independent `d(sides)` rolls; zero rolls returns zero. |
| `ability_dice(rolls=4, *, count=None)` | Roll `rolls` six-sided dice and sum the best three; at least three rolls are required. |
| `plus_or_minus(radius=1, *, count=None)` | Uniform signed integer in `[-radius, radius]`. |
| `plus_or_minus_triangular(radius=1, *, count=None)` | Signed integer in `[-radius, radius]`, triangularly concentrated near zero. |
| `plus_or_minus_normal(radius=1, *, count=None)` | Signed integer in `[-radius, radius]`, normally concentrated near zero. |

For positive inputs, `random_below` and `random_index` both produce the usual
zero-based interval. Their negative continuations deliberately preserve
different structures:

```python
Fortuna.random_below(-10)  # one of -9, -8, ..., -1, 0
Fortuna.random_index(-10)  # one of -10, -9, ..., -2, -1
Fortuna.random_range(-10)  # ValueError: the implied range(0, -10) is empty
```

`random_below` reflects the positive result around zero. `random_index`
preserves Python's positive/negative indexing equivalence: for a ten-item
sequence, every positive index `i` corresponds to the negative index `i - 10`.
An explicit two-bound range remains valid, so `random_range(-10, 0)` produces
a member of `range(-10, 0)`.

Zero is outside both bounded domains. `random_below(0)` and `random_index(0)`
raise `ValueError`, including when `count=0`, because neither describes a
possible result.

`random_below` accepts magnitudes through `2**64`, covering the complete
unsigned 64-bit draw domain at that magnitude. `random_index` accepts
magnitudes through C++ `SIZE_MAX`: on a 64-bit build that is `2**64 - 1`, not
Python's typically smaller `sys.maxsize`. Collection helpers naturally pass
positive Python collection lengths, but the numeric primitive itself is not
restricted to Python's signed sequence-length domain.

### Floating-point generation

| API | Result |
| --- | --- |
| `canonical(*, count=None)` | Uniform float in `[0.0, 1.0)`. |
| `random_float(low=0.0, high=1.0, *, count=None)` | Uniform float in `[low, high)`; equal bounds return that bound. |
| `triangular(low, high, mode, *, count=None)` | Triangular float on `[low, high]` with `low <= mode <= high`; equal bounds return that bound. |

`canonical` consumes one MT19937-64 engine result, discards its lowest 11 bits,
and scales the remaining 53 bits by `2**-53`. Bulk generation preserves the
exact scalar sequence while preparing the engine only once per operation.

### Probability distributions

| API | Parameters and result |
| --- | --- |
| `beta_variate(alpha, beta, *, count=None)` | Beta distribution with shapes `alpha` and `beta` in `[1e-12, 1e12]`; result in `[0, 1]`. |
| `pareto_variate(alpha, *, count=None)` | Pareto distribution with shape `alpha` in `[1e-12, 1e12]`; result at least `1`. |
| `vonmises_variate(mu, kappa, *, count=None)` | Circular von Mises distribution with finite location `mu` and nonnegative concentration `kappa`; result in `[0, 2π)`. |
| `binomial_variate(trials, probability, *, count=None)` | Number of successes in `0 <= trials <= 1_000_000`, with probability in `[0, 1]`. |
| `negative_binomial_variate(successes, probability, *, count=None)` | Failures before `1 <= successes <= 1_000_000`; probability is in `(0, 1]` and the expected result must be safely representable. |
| `geometric_variate(probability, *, count=None)` | Failures before the first success; probability is in `(0, 1]` and the expected result must be safely representable. |
| `poisson_variate(mean, *, count=None)` | Poisson count with `mean` in `[0, 2**63]`; a zero mean returns zero. |
| `exponential_variate(rate, *, count=None)` | Exponential distribution with positive rate. |
| `gamma_variate(shape, scale, *, count=None)` | Gamma distribution with shape in `[1e-12, 1e12]`, positive scale, and a safely representable mean. |
| `weibull_variate(shape, scale, *, count=None)` | Weibull distribution with shape in `[1e-12, 1e12]` and a positive, safely representable scale. |
| `normal_variate(mean, std_dev, *, count=None)` | Normal distribution with nonnegative standard deviation; zero returns `mean`. |
| `log_normal_variate(log_mean, log_deviation, *, count=None)` | Log-normal distribution with nonnegative log-space deviation. |
| `extreme_value_variate(location, scale, *, count=None)` | Extreme-value distribution with positive scale. |
| `chi_squared_variate(degrees_of_freedom, *, count=None)` | Chi-squared distribution with degrees of freedom in `[1e-12, 1e12]`. |
| `cauchy_variate(location, scale, *, count=None)` | Cauchy distribution with positive scale. |
| `fisher_f_variate(degrees_1, degrees_2, *, count=None)` | Fisher F distribution with both degrees of freedom in `[1e-12, 1e12]`. |
| `student_t_variate(degrees_of_freedom, *, count=None)` | Student's t distribution with degrees of freedom in `[1e-12, 1e12]`. |

All real-valued distribution parameters must be finite. Fixed shape and count
limits keep the C++ standard-library transforms terminating across supported
platforms. Fortuna also rejects parameter combinations whose expected value,
scale, or conservative tail margin is not safely representable. A floating
distribution either returns finite values or raises `OverflowError`; it does
not return `NaN` or infinity as a successful draw. Discrete distributions also
raise `OverflowError` instead of returning a saturated unsigned sentinel.

| Safety bound | Contract |
| --- | --- |
| Standard shape and degrees parameters | `[1e-12, 1e12]` for beta, Pareto, gamma, Weibull, chi-squared, Fisher F, and Student's t. |
| Standard discrete counts | At most `1_000_000` binomial trials or negative-binomial successes. |
| Poisson mean | `[0, 2**63]`. |
| Floating mean, scale, and tail safety | Combinations that could exceed Fortuna's conservative finite-output margin raise `OverflowError` before sampling. |
| Saturated discrete output | A standard-library `UINT64_MAX` sentinel raises `OverflowError` instead of being returned as a draw. |

Validation failures use `TypeError` for incompatible argument types,
`ValueError` for values outside a function's supported domain, and
`OverflowError` when an input or result is not representable. Boolean values
are not accepted as integers or real-valued parameters.

### Positional index profiles

Every profile takes `size` and returns an integer in `[0, size)`. `size` must be
positive. Fortuna 6.0.2 deliberately retains only the three bounded triangular
profiles: they are useful, honest about their algorithms, and preserve stable
integer-only draw schedules.

| API | Bias |
| --- | --- |
| `front_triangular(size, *, count=None)` | Toward the front, using the smaller of two uniform indexes. |
| `center_triangular(size, *, count=None)` | Toward the center, using the integer midpoint of two uniform indexes. |
| `back_triangular(size, *, count=None)` | Toward the back, using the larger of two uniform indexes. |

Exact seeded sequences for Fortuna/Storm-owned bounded integer algorithms and
the bounded-only triangular profiles are stable throughout the Fortuna 6 line.
Other floating-point transforms—including custom triangular, Pareto, and von
Mises transforms—and distributions built on them are deterministic within one
platform and toolchain build, but their exact seeded sequences are not a
cross-platform contract.

## Collection helpers

The module helpers accept an optional explicit generator. Without one, they
draw from the calling thread's module default.

| API | Meaning |
| --- | --- |
| `random_value(data, *, generator=None)` | Materialize a nonempty iterable and return one uniformly selected value. |
| `shuffle(array, *, generator=None)` | Unbiased in-place Knuth-B shuffle of a mutable sequence; returns `None`. Fortuna generators use the native loop; custom generator-like objects retain a Fisher-Yates fallback. |
| `sample(population, k, *, generator=None)` | Return `k` uniformly selected values without replacement from an iterable. |

Explicit generators provide corresponding
`generator.random_value(data)`, `generator.shuffle(data)`, and
`generator.sample(population, k)` methods. These always use that generator and
do not accept a separate `generator=` argument.

Sequence advancement is deliberate at degenerate sizes. Selecting from a
singleton with `random_value`, or sampling its sole value with `k=1`, consumes
one bounded draw. Sampling with `k=0` consumes none. Shuffling a sequence of
length zero or one consumes no draw.

Fortuna's native `Generator.shuffle` implementation consumes its complete
swap-index schedule atomically under the generator lock, then releases the lock
before invoking mutable-sequence callbacks. This includes the implementation
when inherited unchanged by a subclass and permits callback re-entry without
deadlock. If a callback raises, the sequence may be partially mutated and the
complete schedule has still been consumed. Custom generator-like objects
without their own `shuffle` use the Python Fisher-Yates fallback; every
injected index is validated before use. The same validation boundary applies
when `random_value` or `sample` receives a custom generator or a `Generator`
subclass override.

## Value engines

Value engines are prepared callable selectors. Each constructor accepts
`resolve_callables=True` and `generator=None`; each also provides
`take(count, *args, **kwargs)` for repeated calls to its default strategy. With
callable resolution enabled, arguments are passed to the initially selected
callable, and any callables it returns are then invoked without arguments.
Callable cycles and runaway chains raise `RuntimeError`. Callable resolution is
an engine behavior, not a separately exported public helper.

| API | Construction and behavior |
| --- | --- |
| `RandomValue(collection, *, resolve_callables=True, generator=None)` | Prepare a materialized nonempty iterable. Calling the object or its `uniform` method selects uniformly. `cycle` advances in input order, `truffle_shuffle` uses the stateful wide-uniform strategy, and `front_triangular`, `center_triangular`, and `back_triangular` select through the corresponding positional profile. The truffle selector is created lazily on its first use. `take(count, ...)` repeats the default uniform strategy. |
| `TruffleShuffle(collection, *, resolve_callables=True, generator=None)` | Shuffle once, then rotate a nonempty collection by randomized short distances before each selection. |
| `WeightedChoice(weighted_table, *, resolve_callables=True, generator=None)` | Select from `(weight, value)` pairs using finite nonnegative relative weights. The table must be nonempty, at least one weight must be positive, and the finite total must be representable. Draws supplied by custom generators, subclass overrides, or monkeypatched module functions must be finite real numbers in `[0, total)`. |

`RandomValue` methods are ordinary bound callables, which supports the prepared
generator pattern directly:

```python
loot = Fortuna.RandomValue(["copper", "potion", "wand"])

uniform_drop = loot()
loot_gen = loot.front_triangular
front_loaded_drop = loot_gen()
next_in_order = loot.cycle()

rarity = Fortuna.WeightedChoice([(80, "common"), (18, "rare"), (2, "legendary")])
result = rarity()
```

The generator binding exposed by a value engine is read-only. Value engines may
maintain cycles, rotations, or other mutable selection state and are not
promised to be thread-safe. Supplying one exact native `Generator` serializes
that generator's engine calls only; it does not make the surrounding selector
state atomic. Use one value-engine instance per worker or provide external
synchronization when sharing one.

See the [Fortuna 5 to 6 migration guide](migration-5-to-6.md) for renamed and
removed interfaces.
