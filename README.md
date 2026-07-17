# Fortuna

Fortuna is a fast random-generation toolkit for Python 3.14. It combines an
explicit generator model, deterministic stream derivation, native bulk
generation, practical probability distributions, and prepared value selectors
for games, simulations, procedural generation, and generative systems.

Fortuna 6 is a deliberate clean break from the historical API. It is built on
the vendored, immutable Storm 5.0.2 engine and is licensed under MIT.

> **Not for cryptography:** Fortuna uses MT19937-64. Do not use it for
> passwords, tokens, keys, secrets, authentication, cryptography, gambling
> security, or security decisions. Entropy-seeded construction does not make
> Fortuna cryptographically secure. Python's `secrets` module is the standard
> library starting point for security-sensitive randomness.

## Installation

Fortuna requires Python 3.14:

```bash
python -m pip install Fortuna
```

With uv:

```bash
uv add Fortuna
```

A source build requires a C++20 toolchain. Contributors working from a checkout
should use the reproducible development setup in
[the development guide](https://github.com/BrokenShell/Fortuna/blob/main/docs/development.md).

## Five-minute tour

Fortuna's module functions are convenient when a process-local random stream is
appropriate:

```python
import Fortuna

initiative = Fortuna.d(20)
fireball_damage = Fortuna.dice(8, 6)
ability_scores = Fortuna.ability_dice(count=6)
morale_adjustment = Fortuna.plus_or_minus_triangular(2)
```

The corresponding methods on `Generator` provide explicit ownership and
repeatability:

```python
world = Fortuna.Generator(0xD06E_0A5E)

room_count = world.random_int(5, 12)
room_sizes = world.random_int(3, 10, count=room_count)
```

Two generators with the same seed produce the same stable Fortuna-owned draw
schedule:

```python
first = Fortuna.Generator(42)
second = Fortuna.Generator(42)

assert first.dice(3, 6, count=20) == second.dice(3, 6, count=20)
```

## Module defaults and explicit generators

Module-level calls use a Fortuna-owned thread-local generator initialized from
process-local entropy. They are appropriate for convenient independent draws:

```python
wand_charges = Fortuna.random_int(1, 20)
```

Use an explicit `Generator` when ownership, reproducibility, or worker stream
identity matters:

```python
campaign_seed = 8128
encounters = Fortuna.for_stream(campaign_seed, "encounters")
treasure = Fortuna.for_stream(campaign_seed, "treasure")

encounter_roll = encounters.d(100)
treasure_roll = treasure.d(100)
```

`for_stream(root_seed, stream_id)` deterministically derives a generator from
an unsigned 64-bit root seed and an `int`, `str`, or `bytes` identifier. The
stream identifier is an input to seed derivation, not a decorative label, so
changing it produces a different deterministic generator sequence. Identifier
types are intentionally distinct.

Use `from_entropy()` when an explicitly owned but nondeterministic generator is
required:

```python
generator = Fortuna.from_entropy()
```

`seed(value)` is deterministic, including `seed(0)`. It changes only the
calling thread's module default. It does not seed other threads or existing
explicit generators.

## Scalar and bulk generation

Every numeric generation function and its `Generator` method accepts the
keyword-only argument `count`:

```python
one_roll = Fortuna.d(20)
many_rolls = Fortuna.d(20, count=100_000)

one_sample = Fortuna.normal_variate(0.0, 1.0)
many_samples = Fortuna.normal_variate(0.0, 1.0, count=100_000)
```

Bulk generation performs the sampling loop in the native extension without
holding the Python GIL and returns a list. `count=0` returns an empty list.
Arguments are validated before the engine advances.

The public numeric families include:

- Uniform booleans, integers, ranges, indexes, floats, and canonical draws.
- Dice, ability dice, and symmetric `plus_or_minus` distributions.
- Triangular, normal, log-normal, exponential, gamma, Weibull, beta, Pareto,
  von Mises, binomial, negative-binomial, geometric, Poisson, extreme-value,
  chi-squared, Cauchy, Fisher F, and Student's t distributions.
- Front, center, and back triangular positional profiles.

The complete domains and failure contracts live in the
[API reference](https://github.com/BrokenShell/Fortuna/blob/main/docs/api.md).

## Collection operations

Fortuna provides uniform selection, sampling without replacement, and an
in-place native Knuth-B shuffle:

```python
monsters = ["goblin", "owlbear", "mimic", "dragon"]

monster = Fortuna.random_value(monsters)
patrol = Fortuna.sample(monsters, 2)
Fortuna.shuffle(monsters)
```

An explicit generator can be supplied to each module helper or used directly:

```python
generator = Fortuna.Generator(7)

monster = Fortuna.random_value(monsters, generator=generator)
patrol = generator.sample(monsters, 2)
generator.shuffle(monsters)
```

The Knuth-B implementation is deliberately optimized for larger workloads,
where its forward traversal has shown the clearest advantage in Fortuna's
controlled benchmarks while remaining competitive at ordinary sizes.

## Prepared value generation

Prepared value engines materialize their inputs once and remain ordinary
Python callables. They are useful when the same table is drawn repeatedly.

### RandomValue

`RandomValue` combines uniform, cyclic, wide, and positional selection behind
one small interface:

```python
loot = Fortuna.RandomValue(["copper", "potion", "wand"])

uniform_drop = loot()
same_as_uniform = loot.uniform()
next_in_order = loot.cycle()
front_loaded_drop = loot.front_triangular()
center_loaded_drop = loot.center_triangular()
back_loaded_drop = loot.back_triangular()
wide_drop = loot.truffle_shuffle()
```

Its methods are normal bound callables. This supports the prepared-generator
pattern directly:

```python
loot_gen = Fortuna.RandomValue(["copper", "potion", "wand"]).front_triangular

drop = loot_gen()
more_drops = [loot_gen() for _ in range(20)]
```

`take(count, ...)` repeats the engine's default uniform strategy:

```python
loot = Fortuna.RandomValue(["copper", "potion", "wand"])
treasure_pile = loot.take(10)
```

### TruffleShuffle

`TruffleShuffle` is a stateful wide selector intended for tables where general
uniformity is desirable but locally clumpy output is not. It shuffles the table
once, then moves through that permutation by randomized short distances:

```python
encounter = Fortuna.TruffleShuffle(
    ["goblins", "wolves", "bandits", "skeletons", "giant spiders"]
)

next_encounter = encounter()
encounter_week = encounter.take(7)
```

It does not promise that repeats are impossible. It is designed to reduce the
feel of localized repetition while retaining broad long-run coverage. See
[Algorithm and design notes](https://github.com/BrokenShell/Fortuna/blob/main/docs/algorithms.md)
for the model and its origin.

### WeightedChoice

`WeightedChoice` accepts finite, nonnegative relative weights:

```python
rarity = Fortuna.WeightedChoice(
    [
        (80, "common"),
        (18, "rare"),
        (2, "legendary"),
    ]
)

item_rarity = rarity()
```

Weights need not add to 100. A weight of zero is allowed, but at least one
weight must be positive. Native generators use Storm's prepared cumulative
selector, so repeated draws do not scan the table in Python.

### Callable values

Prepared value engines resolve selected callables by default. This makes nested
procedural tables concise without eagerly evaluating their contents:

```python
coins = Fortuna.RandomValue(
    [
        lambda: f"{Fortuna.dice(3, 6)} copper pieces",
        lambda: f"{Fortuna.dice(2, 6)} silver pieces",
        lambda: f"{Fortuna.d(6)} gold pieces",
    ]
)

treasure = coins()
```

Pass `resolve_callables=False` when callable objects are the intended values.
Callable cycles and runaway chains raise `RuntimeError`.

## Positional profiles

The retained positional profiles describe their actual bounded triangular
algorithms:

```python
table = ["common", "uncommon", "rare", "very rare", "legendary"]

front = table[Fortuna.front_triangular(len(table))]
center = table[Fortuna.center_triangular(len(table))]
back = table[Fortuna.back_triangular(len(table))]
```

- `front_triangular` uses the smaller of two uniform indexes.
- `center_triangular` uses their integer midpoint.
- `back_triangular` uses the larger index.

## Process and thread behavior

Module defaults are thread-local. A forked child invalidates the inherited
module default and reseeds it before its next draw. A generator created through
`from_entropy()` behaves similarly.

Explicit deterministic generators intentionally retain copied state through
`fork`. Derive a separate stream for each worker when repeated worker streams
are not intended:

```python
worker_generator = Fortuna.for_stream(root_seed, worker_id)
```

Built-in operations sharing one exact `Generator` are serialized, but thread
scheduling still determines which thread receives each draw. Value engines
also contain mutable strategy state and are not promised to be thread-safe.
Use one value-engine instance per worker or synchronize it externally.

Do not fork while another thread is actively using a shared explicit generator;
the child could inherit its native mutex in a locked state.

## Reproducibility boundary

Fortuna's bounded integer, index, range, dice, canonical, bounded-triangular,
stream-derivation, uniform value-selection, sampling, and shuffle schedules are
stable across supported platforms throughout the Fortuna 6 line.

Standard-library probability distributions, `random_float`, custom floating
transforms, `TruffleShuffle`'s Poisson movement, and `WeightedChoice`'s real
draw depend partly on C++ standard-library implementations. They are repeatable
within one platform and toolchain build, but their exact seeded sequences are
not a cross-platform contract. See
[Algorithm and design notes](https://github.com/BrokenShell/Fortuna/blob/main/docs/algorithms.md)
for the complete boundary.

## Documentation

- [Practical guide](https://github.com/BrokenShell/Fortuna/blob/main/docs/guide.md):
  game-oriented examples and composition patterns.
- [API reference](https://github.com/BrokenShell/Fortuna/blob/main/docs/api.md):
  complete public surface, domains, and failure contracts.
- [Algorithm and design notes](https://github.com/BrokenShell/Fortuna/blob/main/docs/algorithms.md):
  engine boundaries, TruffleShuffle, profiles, shuffle, and reproducibility.
- [Migrating from Fortuna 5](https://github.com/BrokenShell/Fortuna/blob/main/docs/migration-5-to-6.md):
  renamed, changed, and removed interfaces.
- [Development guide](https://github.com/BrokenShell/Fortuna/blob/main/docs/development.md):
  build, test, benchmark, process, and contribution contracts.
- [Changelog](https://github.com/BrokenShell/Fortuna/blob/main/CHANGELOG.md):
  release-level changes.

## Development

```bash
uv sync --frozen --group dev --reinstall-package Fortuna
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run python -m benchmarks
uv build
```

Correctness and statistical validation live under `tests/`. Performance
measurement lives under `benchmarks/`; timing is evidence for engineering
decisions, not an ordinary CI pass/fail condition.

## License

Fortuna is available under the
[MIT License](https://github.com/BrokenShell/Fortuna/blob/main/LICENSE). Its
vendored Storm header is also MIT licensed; provenance and checksums are
recorded in the
[vendoring record](https://github.com/BrokenShell/Fortuna/blob/main/src/Fortuna/vendor/Storm/README.md).
