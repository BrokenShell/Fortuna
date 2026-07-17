# Practical Fortuna guide

This guide develops Fortuna's main patterns through game-oriented examples.
The same generator, bulk, distribution, and prepared-selector designs apply to
simulation, procedural content, testing, and generative systems.

For exact parameter domains and exception behavior, use the
[API reference](api.md).

## Choose the random source first

Fortuna offers three ownership models. Choosing one explicitly prevents most
reproducibility and multiprocessing mistakes.

| Need | Use |
| --- | --- |
| Convenient independent draws | Module functions such as `Fortuna.d(20)` |
| Repeatable owned sequence | `Fortuna.Generator(seed)` |
| Repeatable component or worker stream | `Fortuna.for_stream(root_seed, stream_id)` |
| Owned nondeterministic sequence | `Fortuna.from_entropy()` |

Module defaults are thread-local and initialized from process-local entropy.
`seed(value)` changes only the calling thread's module default and is always
deterministic, including `seed(0)`.

## Dice and character generation

The direct dice functions cover common tabletop operations:

```python
import Fortuna

attack_roll = Fortuna.d(20)
greatsword_damage = Fortuna.dice(2, 6)
healing = Fortuna.d(8) + 3
ability_scores = Fortuna.ability_dice(count=6)
```

`ability_dice(rolls=4)` rolls four six-sided dice and sums the best three.
The `rolls` argument sets how many dice are rolled; the highest three are
summed:

```python
standard_score = Fortuna.ability_dice(4)
generous_score = Fortuna.ability_dice(5)
```

At least three rolls are required.

The three symmetric adjustment functions model different kinds of variation:

```python
uniform_noise = Fortuna.plus_or_minus(3)
centered_noise = Fortuna.plus_or_minus_triangular(3)
soft_noise = Fortuna.plus_or_minus_normal(3)
```

- `plus_or_minus` gives every integer in the interval equal weight.
- `plus_or_minus_triangular` concentrates values near zero with bounded integer
  arithmetic.
- `plus_or_minus_normal` produces a bounded bell-shaped result.

## A reproducible campaign

One explicit generator makes a complete generation sequence replayable:

```python
import Fortuna

world = Fortuna.Generator(8128)

region_count = world.random_int(3, 7)
settlement_sizes = world.random_int(50, 5_000, count=region_count)
weather_rolls = world.d(100, count=30)
```

Reconstructing `Generator(8128)` and making the same calls in the same order
reproduces the results.

Large systems are easier to maintain when independent concerns have independent
derived streams:

```python
root_seed = 8128

terrain = Fortuna.for_stream(root_seed, "terrain")
encounters = Fortuna.for_stream(root_seed, "encounters")
treasure = Fortuna.for_stream(root_seed, "treasure")
```

Terrain, encounters, and treasure advance independently. Stream identifiers
are inputs to seed derivation, not decorative labels, so changing one produces
a different deterministic generator sequence. They may be `int`, `str`, or
`bytes`; those types define separate identifier domains.

Use the same pattern for deterministic workers:

```python
def generator_for_worker(root_seed: int, worker_id: int) -> Fortuna.Generator:
    return Fortuna.for_stream(root_seed, worker_id)
```

Assign a distinct derived stream to each worker. Reuse a seed when identical
copied streams are intentional.

## Bulk generation

Every numeric function accepts keyword-only `count`. Use it when all values
share one validated parameter set:

```python
initiative_rolls = Fortuna.d(20, count=10_000)
hit_points = Fortuna.dice(8, 10, count=10_000)
heights = Fortuna.normal_variate(170.0, 10.0, count=10_000)
```

Bulk calls validate once, run the sampling loop natively without the Python
GIL, and return a list. They preserve the corresponding scalar draw schedule:

```python
first = Fortuna.Generator(42)
second = Fortuna.Generator(42)

bulk = first.random_int(1, 100, count=50)
scalar = [second.random_int(1, 100) for _ in range(50)]

assert bulk == scalar
```

Use scalar calls when parameters change per draw or when intermediate results
control subsequent generation.

## Uniform and cyclic value tables

`RandomValue` prepares an iterable once and exposes several bound strategies:

```python
loot = Fortuna.RandomValue(
    ["copper pieces", "healing potion", "spell scroll", "enchanted weapon"]
)

drop = loot()             # uniform
another = loot.uniform()  # explicitly uniform
next_item = loot.cycle()  # input order, wrapping at the end
```

The object snapshots the input iterable during construction, fixing the
prepared table at that point.

Methods can be stored as dedicated callables:

```python
front_loaded_loot = loot.front_triangular

first_drop = front_loaded_loot()
second_drop = front_loaded_loot()
```

This makes each selection strategy usable as a lightweight prepared generator.

## Callable values and procedural composition

Callable values are evaluated only after selection:

```python
coins = Fortuna.RandomValue(
    [
        lambda: f"{Fortuna.dice(3, 6)} copper pieces",
        lambda: f"{Fortuna.dice(2, 6)} silver pieces",
        lambda: f"{Fortuna.d(6)} gold pieces",
    ]
)

loot = Fortuna.RandomValue(
    [
        coins,
        lambda: "one healing potion",
        lambda: f"a scroll of spell level {Fortuna.d(5)}",
    ]
)

result = loot()
```

Resolution is recursive, so selecting `coins` calls it and then resolves the
callable it selects. Cycles and runaway chains raise `RuntimeError`.

Arguments supplied to a value engine are passed to the initially selected
callable:

```python
greeting = Fortuna.RandomValue(
    [
        lambda name: f"Welcome, {name}.",
        lambda name: f"State your business, {name}.",
    ]
)

line = greeting("traveler")
```

Set `resolve_callables=False` when functions, classes, or other callable
objects are intended as data.

## Wide encounter tables with TruffleShuffle

Uniform independent draws can feel clumpy: the same result may appear several
times close together even when the long-run distribution is fair.
`TruffleShuffle` is designed for tables where that localized texture is
undesirable:

```python
encounter_table = [
    "goblin scouts",
    "hungry wolves",
    "roadside bandits",
    "restless skeletons",
    "giant spiders",
    "a traveling merchant",
]
encounter = Fortuna.TruffleShuffle(encounter_table)

week = encounter.take(7)
```

It prepares a randomized permutation and advances through it by randomized
short distances. This tends to spread nearby selections across the table while
maintaining broad coverage. Values may repeat; use a cooldown or no-repeat
model when that is the required contract.

Supply an explicit generator when its construction and draws belong to a
reproducible stream:

```python
encounter_rng = Fortuna.for_stream(8128, "encounters")
encounter = Fortuna.TruffleShuffle(encounter_table, generator=encounter_rng)
```

The table's preparation consumes that generator's shuffle schedule immediately.

## Weighted tables with WeightedChoice

Use relative weights when each number expresses an entry's share:

```python
rarity = Fortuna.WeightedChoice(
    relative=[
        (80, "common"),
        (18, "rare"),
        (2, "legendary"),
    ]
)
```

Weights are relative, so `(80, 18, 2)`, `(40, 9, 1)`, and `(0.80, 0.18,
0.02)` describe the same probabilities. They must be finite and nonnegative,
and at least one must be positive.

Passing the table as the first positional argument is equivalent to using
`relative=`. The explicit keyword is useful when a module contains several
table styles.

Many tabletop books publish cumulative roll tables. Their upper boundaries can
be entered directly:

```python
treasure = Fortuna.WeightedChoice(
    cumulative=[
        (30, "coins"),       # rolls 1–30
        (60, "gem"),         # rolls 31–60
        (90, "potion"),      # rolls 61–90
        (100, "magic item"), # rolls 91–100
    ]
)

drop = treasure()
```

Cumulative boundaries must be finite, nonnegative, and nondecreasing, and the
last boundary must be positive. Equal adjacent boundaries give an entry zero
probability.

Values may be procedural callables:

```python
treasure = Fortuna.WeightedChoice(
    relative=[
        (80, lambda: f"{Fortuna.dice(3, 6)} silver pieces"),
        (18, lambda: "a potion of healing"),
        (2, lambda: f"a +{Fortuna.d(3)} weapon"),
    ]
)

drop = treasure()
```

Both input forms prepare the same cumulative representation. Native draws use
logarithmic lookup in Storm.

## Positional table profiles

The positional profiles are useful when ordering already expresses rarity or
priority:

```python
treasure_table = [
    "copper",
    "silver",
    "gold",
    "potion",
    "scroll",
    "enchanted weapon",
]

common_leaning = treasure_table[Fortuna.front_triangular(len(treasure_table))]
middle_leaning = treasure_table[Fortuna.center_triangular(len(treasure_table))]
rare_leaning = treasure_table[Fortuna.back_triangular(len(treasure_table))]
```

`RandomValue` exposes the same profiles directly and avoids repeating the
indexing expression:

```python
treasure = Fortuna.RandomValue(treasure_table)
rare_leaning = treasure.back_triangular()
```

These profiles are bounded integer algorithms with stable Fortuna 6 draw
schedules.

## Sampling and shuffling

Use `sample` for values without replacement:

```python
party = ["fighter", "wizard", "rogue", "cleric", "ranger"]
watch_order = Fortuna.sample(party, 3)
```

Use `shuffle` to mutate a sequence in place:

```python
deck = list(range(52))
Fortuna.shuffle(deck)
```

An explicit generator owns the complete operation:

```python
deck_rng = Fortuna.for_stream(8128, "deck")
deck_rng.shuffle(deck)
hand = deck_rng.sample(deck, 5)
```

## Negative bounded continuations

Fortuna defines two intentionally different negative domains:

```python
Fortuna.random_below(-10)  # -9 through 0
Fortuna.random_index(-10)  # -10 through -1
```

`random_below` reflects the positive bounded interval around zero.
`random_index` preserves Python's equivalence between positive and negative
indexes:

```python
items = list("abcdefghij")
index = Fortuna.random_index(-len(items))
value = items[index]
```

Zero is an empty-domain singularity for both functions and raises `ValueError`.
`random_range` follows Python's directed `range` contract instead:

```python
Fortuna.random_range(-10, 0)  # valid
Fortuna.random_range(-10)     # ValueError: range(0, -10) is empty
```

## Simulation distributions

Fortuna's probability distributions use explicit safe domains and reject
nonfinite parameters:

```python
arrival_delays = Fortuna.exponential_variate(0.25, count=10_000)
measurements = Fortuna.normal_variate(100.0, 5.0, count=10_000)
rare_event_counts = Fortuna.poisson_variate(2.5, count=10_000)
success_counts = Fortuna.binomial_variate(20, 0.65, count=10_000)
```

Standard-library floating distributions may differ in exact seeded output
between C++ toolchains. Use stable bounded integer primitives when exact
cross-platform replay is required.

## Error handling

Fortuna uses explicit exceptions:

- `TypeError` for incompatible types, including booleans passed as integers.
- `ValueError` for values outside an operation's domain.
- `OverflowError` when an input or result is not safely representable.

Invalid calls raise before sampling, preserving generator state:

```python
generator = Fortuna.Generator(42)

try:
    generator.random_range(10, 10)
except ValueError:
    pass
```

Consult the [API reference](api.md) when domain boundaries are part of the
application contract.

## Next references

- [API reference](api.md) for every public function and exact validation rule.
- [Algorithm and design notes](algorithms.md) for implementation models and
  reproducibility boundaries.
- [Fortuna 5 migration guide](migration-5-to-6.md) for the clean-break upgrade.
- [Development guide](development.md) for building, testing, and benchmarking.
