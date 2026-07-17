# Algorithm and design notes

This document explains the models behind Fortuna's distinctive behavior. The
[API reference](api.md) defines the supported domains and exceptions.

## The Fortuna and Storm boundary

Storm is Fortuna's vendored C++20 random engine and numeric algorithm layer.
Fortuna owns the Python-facing contracts around it:

- Engine ownership, deterministic streams, thread defaults, and fork behavior.
- Python type and domain validation.
- Bulk return values and GIL behavior.
- Collection materialization, callable resolution, and value-engine ergonomics.
- Public names, documentation, and compatibility guarantees.

This boundary keeps numeric state and hot loops native while Fortuna owns
Python behavior, callable invocation, and mutable collection callbacks outside
the C++ lock.

Fortuna vendors an immutable Storm release. The exact tag, commit, source
checksum, header checksum, and license are recorded in
`src/Fortuna/vendor/Storm/README.md`.

## Engine model

The underlying engine is `std::mt19937_64`. Fortuna exposes it through two
ownership models.

### Module defaults

Each Python thread has a Fortuna-owned module generator. It is initialized from
process-local entropy on first use. `seed(value)` replaces that state
deterministically for the calling thread only.

After `fork`, the child marks its inherited module generator as requiring new
entropy. The next module draw reseeds it before sampling. This prevents the
parent and child from silently continuing the same entropy-initialized stream.

### Explicit generators

`Generator(seed)` is deterministic and owned by its Python object. A forked
child inherits a deliberate copy at the same position. `for_stream` derives
deterministic seeds for named components or workers so callers can avoid
accidental repetition.

`from_entropy()` creates an entropy-managed explicit generator. It remembers
its process identity and reseeds lazily when first used in a forked child.

Native operations on one exact `Generator` acquire its mutex around engine
access. This protects the engine from concurrent mutation. Thread scheduling
remains nondeterministic, and surrounding Python value engines require their
own synchronization.

## Bounded unsigned sampling

Uniform bounded integers are a foundation for integer APIs, positional
profiles, collection selection, sampling, and shuffle schedules.

Storm uses rejection sampling to eliminate modulo bias. For a bound `n`, it
rejects the high tail of the 64-bit engine domain that would make some
remainders more common than others, then maps the accepted result into the
requested interval.

This avoids modulo bias and defines a stable Fortuna-owned draw schedule. The
same bounded primitive supports the complete unsigned 64-bit domain, including
the special span represented by `2**64`.

## Canonical floating draws

`canonical()` constructs a uniform binary64 value in `[0.0, 1.0)` directly
from one engine result:

1. Discard the lowest 11 bits of the 64-bit result.
2. Select 53 bits of precision.
3. Scale by `2**-53`.

This is a small, auditable algorithm with an exact cross-platform seeded
schedule. `canonical(count=n)` uses the same operation repeatedly, so its bulk
result matches `n` scalar calls from an equivalent generator.

## Negative bounded continuations

`random_below` and `random_index` agree on positive inputs and deliberately
diverge on negative inputs.

For a positive magnitude of ten:

```text
random_below(10) ->  0 ...  9
random_index(10) ->  0 ...  9
```

`random_below` reflects that interval around zero:

```text
random_below(-10) -> -9 ... 0
```

`random_index` continues the domain according to Python's negative-index
equivalence:

```text
positive index:  0  1  2 ...  9
negative index: -10 -9 -8 ... -1
```

Thus `items[random_index(-len(items))]` uniformly addresses the same elements
through their negative spellings.

The two functions deliberately preserve different structures beyond the
ordinary positive domain. Zero remains a true
singularity for both: neither “an integer below zero” in the bounded interval
nor “an index into a sequence of size zero” describes a possible result.

`random_range` follows Python's directed `range` semantics.

## Bounded triangular profiles

The three positional profiles draw two uniform indexes, `left` and `right`, in
`[0, size)`:

- `front_triangular` returns `min(left, right)`.
- `center_triangular` returns the integer midpoint of the two indexes.
- `back_triangular` returns `max(left, right)`.

They are bounded, integer-only algorithms with stable Fortuna-owned seeded
schedules.

The profiles are most useful when a sequence is already ordered by rarity,
priority, progression, or some other meaningful axis.

## Knuth-B shuffle

Fortuna's native shuffle uses the forward Knuth-B form. Given positions from
the front of the sequence toward the back, it selects a partner uniformly from
the unprocessed suffix and swaps the two values.

It is distributionally equivalent to the familiar reverse Fisher-Yates form
when both use unbiased bounded indexes. The traversal and index ranges differ,
giving each form a distinct deterministic draw schedule.

Fortuna selected Knuth-B for its large-workload behavior. Controlled macOS
arm64 release-build measurements show a substantial advantage at one million
elements, while intermediate sizes are close enough for either traversal to
take a small win. The project prioritizes the large-workload result rather than
claiming one traversal wins every size. Both the choice and the seeded schedule
are part of Fortuna 6's collection contract.

For exact native generators, Fortuna consumes the complete index schedule while
holding the generator lock, then releases the lock before mutating arbitrary
Python sequences. This prevents Python callbacks from running under the native
mutex. If a sequence callback fails, the index schedule has still been
consumed, although the sequence may be partially modified.

## TruffleShuffle and wide distributions

TruffleShuffle began with a question about efficient “wide distributions”:
how can a selector combine broad general coverage with less of the locally
clumpy texture of independent uniform draws?

Fortuna's answer is a prepared stateful selector:

1. Materialize the input collection.
2. Produce one unbiased Knuth-B permutation.
3. Set a rotation width to the integer square root of the collection size.
4. On each draw, sample a Poisson distance with mean `rotation_width / 4`.
5. Reject distances outside the rotation width.
6. Move forward by one plus that distance, wrapping around the permutation.
7. Return the value at the resulting position.

The mandatory step of at least one guarantees movement on every draw. The short
randomized movement tends to spread adjacent outputs across the prepared
permutation, combining broad coverage with reduced localized repetition.

TruffleShuffle allows repeats after wraparound or when sampled movement reaches
a value again. Applications requiring a hard cooldown, a shuffle bag, or
sampling without replacement should model that contract directly.

Storm 5.0.2 owns the native permutation, cursor, and Poisson distribution for
exact Fortuna generators. Fortuna owns value lookup, callable resolution,
custom-generator fallbacks, and process semantics. The native representation
matches Fortuna's established Knuth-B construction, unsigned Poisson type,
cursor direction, and engine advancement.

## Prepared weighted selection

`WeightedChoice` converts relative weights into monotonically increasing
cumulative boundaries once during construction. A draw then:

1. Samples a uniform real value in `[0, total_weight)`.
2. Uses an upper-bound search to locate the first cumulative boundary greater
   than the draw.
3. Returns the value at that index.

Zero-weight entries occupy no interval and receive zero selection probability.
At least one weight must be positive, and the cumulative total must remain
finite and representable.

For exact native generators, Storm owns the prepared cumulative table and
performs logarithmic lookup. Fortuna owns the Python values and callable
resolution. Custom generators and generator subclasses use a validated Python
fallback so injected draws cannot escape the weighted interval.

## Callable resolution

Value engines keep selected values in Python. If callable resolution is
enabled, Fortuna invokes the initially selected callable with the caller's
arguments, then invokes any callable values it returns without additional
arguments until a noncallable result is reached.

This boundary is deliberately outside native generator locks. User code may
raise, recurse into Fortuna, acquire application locks, or perform arbitrary
work without holding an engine mutex.

Fortuna tracks callable identities and a maximum resolution depth. Cycles and
runaway chains raise `RuntimeError`; user exceptions propagate unchanged.

## Bulk generation

Bulk APIs use the scalar probability model. They validate one parameter set
and repeat the same scalar native operation into a contiguous C++ buffer before
converting the result to a Python list.

The loop runs without the Python GIL. For stable Fortuna-owned algorithms, bulk
and scalar calls on equivalent generators produce the same sequence and leave
the engines in the same state.

## Reproducibility tiers

Fortuna documents two tiers of deterministic reproducibility.

### Stable across supported Fortuna 6 builds

- Bounded integer, index, and directed-range algorithms.
- Dice and ability dice.
- `canonical`.
- Bounded triangular positional profiles.
- Stream derivation.
- Uniform collection selection, sampling, and shuffle.

### Repeatable within one platform and toolchain build

- `random_float` and standard-library probability distribution transforms.
- TruffleShuffle's standard-library Poisson movement.
- WeightedChoice's standard-library real draw.
- Custom triangular, Pareto, and von Mises transforms.
- Distributions composed from toolchain-dependent floating transforms.

The second tier remains deterministic for a fixed build. Its exact seeded
sequence is platform-and-toolchain-specific. Applications that persist seeds
for long-term portable replay should build critical decisions from the stable
tier.

## Performance evidence

Fortuna's benchmark suite is repository-local and opt-in. Benchmark cases
consume their results, report fixed workload metadata, and can compare
compatible JSON artifacts. Correctness gates use deterministic and statistical
tests; timing evidence requires controlled hardware because shared CI machines
provide variable latency.

Performance changes must preserve the relevant output distribution, seeded
schedule where promised, engine advancement, validation boundary, and ownership
contract. A faster algorithm with a different deterministic schedule requires
an explicit behavior-contract change.
