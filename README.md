# Fortuna: Generative Modeling Toolkit for Python3
© 2024 Robert Sharp, all rights reserved.

Fortuna's main goal is to provide a quick and easy way to build custom random 
functions for your data that are byte-code fast and thread aware. Fortuna also 
offers a variety of high-performance random number functions like 
`random_range(start, stop, step)` and `dice(rolls, sides)`.

The core functionality of Fortuna (the Storm Engine) was created 
by the same developer - Robert Sharp. While Storm is a high quality, hardware 
seeded random engine - it is not appropriate for cryptography of any kind. 
Fortuna is intended for games, data science, Generative A.I. and experimental 
programming... not security, hashing or gambling! Fortuna is free for 
non-commercial use. Contact the developer for details about commercial licensing 
and current availability of FortunaPro.

### Quick Install `$ pip install Fortuna`

### Installation Notes:
- Fortuna is optimized for macOS & Linux.
- New in version 5, Fortuna now supports Windows.
- Installation requires C++ Compiler and C++ Standard Library.
- On Linux, Fortuna requires Python3 developer environment.

### Installation Examples:
- macOS & Windows
  - `pip install Fortuna`
- Linux & WSL: Debian (you may need sudo)
  - `apt update`
  - `apt upgrade`
  - `apt install build-essential`
  - `apt install python3-dev python3-pip`
  - Optionally Make a Virtual Environment
    - `apt install python3.11-venv`
    - `python3 -m venv venv`
    - `source venv/bin/activate`
  - `pip install --upgrade pip setuptools wheel`
  - `pip install Fortuna`


### Sister Projects:
- [MonkeyScope](https://pypi.org/project/MonkeyScope): Framework for testing non-deterministic components.
- [Storm](https://github.com/BrokenShell/Storm): High Performance C++ Random Number Engine & Toolkit.


---

### Table of Contents:
- Numeric Limits
    - `Storm::Metrics`
- Random Value Classes
    - `RandomValue(Iterable[Any]) -> Callable -> Any`
    - `TruffleShuffle(Iterable[Any]) -> Callable -> Any`
    - `QuantumMonty(Iterable[Any]) -> Callable -> Any`
    - `CumulativeWeightedChoice(Iterable[Tuple[int, Any]]) -> Callable -> Any`
    - `RelativeWeightedChoice(Iterable[Tuple[int, Any]]) -> Callable -> Any`
    - `FlexCat(Dict[str, Iterable[Any]]) -> Callable -> Any`
- Random Value Functions
    - `random_value(data: Sequence[Any]) -> Any`
    - `cumulative_weighted_choice(Sequence[Tuple[int, Any]]) -> Any`
    - `truffle_shuffle(data: Iterable[Any]) -> Callable -> Any`
- Random Integer Functions
    - `random_below(Integer) -> Integer`
    - `random_int(Integer, Integer) -> Integer`
    - `random_range(Integer, Integer, Integer) -> Integer`
    - `d(Integer) -> Integer`
    - `dice(Integer, Integer) -> Integer`
    - `plus_or_minus(Integer) -> Integer`
    - `plus_or_minus_linear(Integer) -> Integer`
    - `plus_or_minus_gauss(Integer) -> Integer`
    - `binomial_variate(Integer, Float) -> Integer`
    - `negative_binomial_variate(Integer, Float) -> Integer`
    - `geometric_variate(Float) -> Integer`
    - `poisson_variate(Float) -> Integer`
- Random Index Functions 
    - ZeroCool Specification: `f(N) -> [0, N)` or `f(-N) -> [-N, 0)`
    - `random_index(Integer) -> Integer`
    - `front_gauss(Integer) -> Integer`
    - `middle_gauss(Integer) -> Integer`
    - `back_gauss(Integer) -> Integer`
    - `quantum_gauss(Integer) -> Integer`
    - `front_poisson(Integer) -> Integer`
    - `middle_poisson(Integer) -> Integer`
    - `back_poisson(Integer) -> Integer`
    - `quantum_poisson(Integer) -> Integer`
    - `front_linear(Integer) -> Integer`
    - `middle_linear(Integer) -> Integer`
    - `back_linear(Integer) -> Integer`
    - `quantum_linear(Integer) -> Integer`
    - `quantum_monty(Integer) -> Integer`
- Random Float Functions
    - `canonical() -> Float`
    - `random_float(Float, Float) -> Float`
    - `triangular(Float, Float, Float) -> Float`
    - `normal_variate(Float, Float) -> Float`
    - `lognormal_variate(Float, Float) -> Float`
    - `exponential_variate(Float) -> Float`
    - `gamma_variate(Float, Float) -> Float`
    - `weibull_variate(Float, Float) -> Float`
    - `extreme_value_variate(Float, Float) -> Float`
    - `chi_squared_variate(Float) -> Float`
    - `cauchy_variate(Float, Float) -> Float`
    - `fisher_f_variate(Float, Float) -> Float`
    - `student_t_variate(Float) -> Float`
    - `beta_variate(Float, Float) -> Float`
    - `pareto_variate(Float) -> Float`
    - `vonmises_variate(Float, Float) -> Float`
- Random Boolean Functions
    - `percent_true(Float) -> Boolean`
    - `bernoulli_variate(Float) -> Boolean`
- Inplace Shuffle Algorithms
    - `shuffle(List[Any]) -> None`
    - `knuth_a(List[Any]) -> None`
    - `fisher_yates(List[Any]) -> None`
- Utilities
    - `seed(int) -> None`
    - `sample(population: Sequence, k: int) -> List`
    - `flatten(Object, *args, Boolean, **kwargs) -> Object`
    - `smart_clamp(Integer, Integer, Integer) -> Integer`
    - `float_clamp(Float, Float, Float) -> Float`
    - `distribution_range(Callable, Integer, Integer) -> Callable`
    - `max_unit() -> Unsigned Integer`
    - `min_int() -> Integer`
    - `max_int() -> Integer`
    - `min_float() -> Float`
    - `max_float() -> Float`
    - `min_below() -> Float`
    - `min_above() -> Float`
- Development Log
- Test Suite Output
- Legal Information


#### Numeric Limits:
- Unsigned Integer: 64 bit unsigned integer.
    - Range: 0-18446744073709551615, approximately 18.4 billion-billion
- Integer: 64 bit signed integer.
    - Range: ±9223372036854775807, approximately ±9.2 billion-billion
- Float: 64 bit floating point.
    - Range: ±1.7976931348623157e+308
    - Epsilon Delta: 5e-305 to 5e-324, platform dependent

----

## Random Value Engines

### Fortuna.RandomValue
`Fortuna.RandomValue(collection: Iterable[Any], zero_cool=random_index, flat=True) -> Callable -> Value`
Random Value Engine Class that supports dependency injection.

Takes an iterable (tuple) and a distribution function and returns
a callable to produce random values from the iterable with the same distribution.

- @param collection :: Iterable of Values. Tuple recommended.
- @param zero_cool :: Optional ZeroCool Callable, kwarg only. Default = random_index(). This function must follow the ZeroCool Spec.
- @param flat :: Bool. Default: True. Option to automatically flatten callable values with lazy evaluation.
- @return :: Callable Object. `Callable(*args, **kwargs) -> Value`
    - @param *args, **kwargs :: Optional arguments used to flatten the return Value (below) if Callable.
    - @return Value or Value(*args, **kwargs) if the value itself is callable. This is recursive.

#### RandomValue Dependency Injection: Rare Apples Example
RandomValue supports dependency injection, it is the only Fortuna class to do so.
The injected functor must follow the ZeroCool Specification:
f(x: int) -> int in [0, x) with any distribution. Many ZeroCool functions are provided,
in the following example we'll see front_linear and back_linear used together.

> If one of the builtin ZeroCool distributions is required, it is 
highly recommended to employ QuantumMonty rather than RandomValue. 
ZeroCool distributions are used here for the demonstration of RandomValue only. 
QuantumMonty offers the same ZeroCool distributions, but with less overhead. 
RandomValue is specifically designed for custom dependency injection, 
where you might design your own distribution and use it with RandomValue.

```python
from Fortuna import RandomValue, front_linear, back_linear


# Setup
random_apple = RandomValue((
    "Delicious", 
    "Empire", 
    "Granny Smith", 
    "Honey Crisp", 
    "Macintosh",
), zero_cool=front_linear)

random_fruit = RandomValue((
    lambda: f"Apple, {random_apple()}",
    "Banana",
    "Cherry",
    "Grapes",
    "Orange",
), zero_cool=back_linear)

# Usage
print(random_fruit())
# prints a random 'Fruit' with a compound linear distribution
# where 'Delicious' is the most common 'Apple' and 'Apple' is the rarest 'Fruit'

```
#### QuantumMonty: Rare Apples Example
Same as above but with QuantumMonty - for syntax comparison.
```python
from Fortuna import QuantumMonty


# Setup
random_apple = QuantumMonty((
    "Delicious", 
    "Empire", 
    "Granny Smith", 
    "Honey Crisp", 
    "Macintosh",
)).front_linear

random_fruit = QuantumMonty((
    lambda: f"Apple, {random_apple()}",
    "Banana",
    "Cherry",
    "Grapes",
    "Orange",
)).back_linear

# Usage
print(random_fruit())
# prints a random fruit with the correct compound distribution
```

### Auto Flattening
Auto Flattening works with all random generator classes in Fortuna, and it's on by default.
Flattening is lazy: it happens at call time as the last step. 
Flattening is recursive: this allows a nested lambda stack to be collapsed automatically.
Flattening is resilient: if for any reason a callable can not be flatted - it will 
be returned in an un-flattened state without error. 

#### Example: RandomValue with Auto Flattening
```python
from Fortuna import RandomValue


auto_flat = RandomValue([lambda: 1, lambda: 2, lambda: 3])
print(auto_flat())  # will print the value 1, 2 or 3.
# Note: the lambda will not be called until call time and stays dynamic for the life of the object.

auto_flat_with = RandomValue([lambda x: x, lambda x: x + 1, lambda x:  x + 2])
print(auto_flat_with(2))  # will print the value 2, 3 or 4
# Note: if this is called with no args it will simply return the lambda in an uncalled state.

un_flat = RandomValue([lambda: 1, lambda: 2, lambda: 3], flat=False)
print(un_flat()())  # will print the value 1, 2 or 3, 
# mind the double-double parenthesis, they are required to manually unpack the lambdas

auto_un_flat = RandomValue([lambda x: x, lambda x: x + 1, lambda x:  x + 2], flat=False)
# Note: flat=False is not required here because the lambdas can not be called without input x satisfied.
# It is recommended to specify flat=False if non-flat output is intended.
print(auto_un_flat()(1))  # will print the value 1, 2 or 3, mind the double-double parenthesis.
```

#### Mixing Static Objects with Callable Objects
Auto Flattening works with all random generator classes in Fortuna, and it's on by default.
```python
from Fortuna import RandomValue


""" With automatic flattening active, `lambda() -> int` can be treated as an `int`. """
mixed_flat = RandomValue([1, 2, lambda: 3])
print(mixed_flat())  # will print 1, 2 or 3

""" Mixed Anti-pattern """
mixed_un_flat = RandomValue([1, 2, lambda: 3], flat=False) # this is not recommended.
print(mixed_flat())  # will print 1, 2 or "Function <lambda at some_address>"
# This pattern is not recommended because you won't know the nature of what you get back.
# This is almost always not what you want, and it can give rise to messy logic in other areas of your code.
```

#### Dynamic Strings
To successfully express a dynamic string, and keep it dynamic for the duration of the program, at least one level of indirection is required. Without a lambda - the f-string would collapse into a static string too soon.
This works with all random generator classes in Fortuna.

```python
from Fortuna import RandomValue, d


# d() is a simple dice function, d(n) -> [1, n] flat uniform distribution.
dynamic_string = RandomValue((
    # while the probability of all A == all B == all C, individual probabilities of each possible string will differ based on the number of possible outputs of each category.
    lambda: f"A{d(2)}",  # -> A1 - A2, each are twice as likely as any particular B, and three times as likely as any C.
    lambda: f"B{d(4)}",  # -> B1 - B4, each are half as likely as any particular A, and 3/2 as likely as any C.
    lambda: f"C{d(6)}",  # -> C1 - C6, each are 1/3 as likely as any particular A and 2/3 as likely of any B.
))

print(dynamic_string())  # prints a random dynamic string, generated at call time.
```

### TruffleShuffle
`Fortuna.TruffleShuffle(collection: Iterable[Any], flat=True) -> Callable -> Value`
- @param collection :: Iterable of Values. Set recommended but not required.
- @param flat :: Bool. Default: True. Option to automatically flatten callable values with lazy evaluation.
- @return :: Callable Object. `Callable(*args, **kwargs) -> Value`
    - @param *args, **kwargs :: Optional arguments used to flatten the return Value (below) if Callable.
    - @return :: Random value from the collection with a Wide Uniform Distribution. 
    
Wide Uniform Distribution: "Wide" refers to the average distance between consecutive occurrences of the same value. The average width of the output distribution will naturally scale up with the size of the collection. The goal of this type of distribution is to keep the output sequence free of clumps or streaks of the same value, while maintaining randomness and uniform probability. This is not the same as a flat uniform distribution. The two distributions over time will be statistically similar for any given set, but the repetitiveness of the output sequence will be very different.

#### TruffleShuffle, Basic Use
```python
from Fortuna import TruffleShuffle

# Setup
list_of_values = { 1, 2, 3, 4, 5, 6 }
truffle_shuffle = TruffleShuffle(list_of_values)

# Usage
print(truffle_shuffle())  # this will print one of the numbers 1-6, 
# repeated calls will produce a wide distribution.
```

#### Nesting Dolls
This works with all random generator classes in Fortuna, interchangeably.
```python
from Fortuna import RandomValue, TruffleShuffle

# Setup
nesting_dolls = TruffleShuffle((
    RandomValue(("A", "B", "C", "D", "E")),
    RandomValue(("F", "G", "H", "I", "J")),
    RandomValue(("K", "L", "M", "N", "O")),
    RandomValue(("P", "Q", "R", "S", "T")),
))

# Usage
print(nesting_dolls())  
# Prints one of the letters A-T.
# Produces a wide distribution of each category -
# and a flat uniform distribution within each category.
```

### QuantumMonty
`Fortuna.QuantumMonty(collection: Iterable[Any], flat=True) -> Callable -> Value`
- @param collection :: Iterable of Values. Tuple recommended.
- @param flat :: Bool. Default: True. Option to automatically flatten callable values with lazy evaluation.
- @return :: Callable Object with Monty Methods for producing various distributions of the data.
    - @param *args, **kwargs :: Optional arguments used to flatten the return Value (below) if Callable.
    - @return :: Random value from the data. The instance will produce random values from the list using the selected distribution model or "monty". The default monty is the Quantum Monty Algorithm.

```python
from Fortuna import QuantumMonty

# Setup
list_of_values = [1, 2, 3, 4, 5, 6]
monty = QuantumMonty(list_of_values)

# Usage
print(monty())               # prints a random value from the list_of_values
                             # uses the default Quantum Monty Algorithm

print(monty.flat_uniform())  # prints a random value from the list_of_values
                             # uses the "flat_uniform" monty
                             # equivalent to random.choice(list_of_values)
```
The QuantumMonty class represents a diverse collection of strategies for producing random values from a sequence where the output distribution is based on the method you choose. Generally speaking, each value in the sequence will have a probability that is based on its position in the sequence. For example: the "front" monty produces random values where the beginning of the sequence is geometrically more common than the back. Given enough samples the "front" monty will always converge to a 45 degree slope down for any list of unique values.

There are three primary method families: linear, gaussian, and poisson. Each family has three base methods; 'front', 'middle', 'back', plus a 'quantum' method that incorporates all three base methods. The quantum algorithms for each family produce distributions by overlapping the probability waves of the other methods in their family. The Quantum Monty Algorithm incorporates all nine base methods.

```python
import Fortuna

# Setup
monty = Fortuna.QuantumMonty(
    ["Alpha", "Beta", "Delta", "Eta", "Gamma", "Kappa", "Zeta"]
)

# Usage
# Each of the following methods will return a random value from the sequence.
# Each method has its own unique distribution model.

""" Flat Base Case """
monty.flat_uniform()        # Flat Uniform Distribution

""" Geometric Positional """
monty.front_linear()        # Linear Descending, Triangle
monty.middle_linear()       # Linear Median Peak, Equilateral Triangle
monty.back_linear()         # Linear Ascending, Triangle
monty.quantum_linear()      # Linear Overlay, 3-way monty.

""" Gaussian Positional """
monty.front_gauss()         # Front Gamma
monty.middle_gauss()        # Scaled Gaussian
monty.back_gauss()          # Reversed Gamma
monty.quantum_gauss()       # Gaussian Overlay, 3-way monty.

""" Poisson Positional """
monty.front_poisson()       # 1/4 Mean Poisson
monty.middle_poisson()      # 1/2 Mean Poisson
monty.back_poisson()        # 3/4 Mean Poisson
monty.quantum_poisson()     # Poisson Overlay, 3-way monty.

""" Quantum Monty Algorithm: Default Monty """
monty()                     # Quantum Monty Algorithm, 9-way monty.
monty.quantum_monty()       #  same as above
```

### Weighted Choice: Base Class
Weighted Choice offers two strategies for selecting random values from a sequence where programmable rarity is desired. Both produce a custom distribution of values based on the weights of the values.

The choice to use one strategy over the other is purely about which one suits you or your data best. Relative weights are easier to understand at a glance. However, many RPG Treasure Tables map rather nicely to a cumulative weighted strategy.

#### Cumulative Weighted Choice
`Fortuna.CumulativeWeightedChoice(weighted_table: Iterable[Tuple[int, Any]], flat=True) -> Callable -> Value`
- @param weighted_table :: Table of weighted pairs. Tuple of Tuples recommended.
- @param flat :: Bool. Default: True. Option to automatically flatten callable values with lazy evaluation.
- @return :: Callable Instance
    - @param *args, **kwargs :: Optional arguments used to flatten the return Value (below) if Callable.
    - @return :: Random value from the weighted_table, distribution based on the weights of the values.

_Note: Logic dictates Cumulative Weights must be unique!_

```python
from Fortuna import CumulativeWeightedChoice

# Setup
cum_weighted_choice = CumulativeWeightedChoice((
    (7, "Apple"),
    (11, "Banana"),
    (13, "Cherry"),
    (23, "Grape"),
    (26, "Lime"),
    (30, "Orange"),  # same as relative weight 4 because 30 - 26 = 4
))
# Usage
print(cum_weighted_choice())  # prints a weighted random value
```

#### Relative Weighted Choice
`Fortuna.RelativeWeightedChoice(weighted_table: Iterable[Tuple[int, Any]]) -> Callable -> Value`
- @param weighted_table :: Table of weighted pairs. Tuple of Tuples recommended.
- @param flat :: Bool. Default: True. Option to automatically flatten callable values with lazy evaluation.
- @return :: Callable Instance
    - @param *args, **kwargs :: Optional arguments used to flatten the return Value (below) if Callable.
    - @return :: Random value from the weighted_table, distribution based on the weights of the values.

```python
from Fortuna import RelativeWeightedChoice

# Data
population = ["Apple", "Banana", "Cherry", "Grape", "Lime", "Orange"]
rel_weights = [7, 4, 2, 10, 3, 4]

# Setup
rel_weighted_choice = RelativeWeightedChoice(zip(rel_weights, population))

# Usage
print(rel_weighted_choice())  # prints a weighted random value
```

### FlexCat
`Fortuna.FlexCat(matrix_data: Matrix, key_bias="front_linear", val_bias="truffle_shuffle", flat=True) -> Callable -> Value`
- @param matrix_data :: Dictionary of Sequences. `Dict[str, Iterable[Any]]`
- @parm key_bias :: Default is "front_linear". String indicating the name of the algorithm to use for random key selection.
- @parm val_bias :: Default is "truffle_shuffle". String indicating the name of the algorithm to use for random value selection.
- @param flat :: Bool. Default is True. Option to automatically flatten callable values with lazy evaluation.
- @return :: Callable Instance
    - @param cat_key :: Optional String. Default is None. Key selection by name. If specified, this will override the key_bias for a single call.
    - @param *args, **kwargs :: Optional arguments used to flatten the return Value (below) if Callable.
    - @return :: Value. Returns a random value generated with val_bias from a random sequence generated with key_bias.

FlexCat is like a multidimensional QuantumMonty.

The constructor takes two optional keyword arguments to specify the algorithms to be used to make random selections. The algorithm specified for selecting a key need not be the same as the one for selecting values. An optional key may be provided at call time to bypass the random key selection. Keys passed in this way must exactly match a key in the Matrix.

By default, FlexCat will use key_bias="front_linear" and val_bias="truffle_shuffle", this will make the top of the data structure geometrically more common than the bottom, and it will truffle shuffle the sequence values. This config is known as TopCat, it produces a descending-step, micro-shuffled distribution sequence. Many other combinations are available.

Algorithmic Options: _See QuantumMonty & TruffleShuffle for more details._
- "front_linear", Linear Descending
- "middle_linear", Linear Median Peak
- "back_linear", Linear Ascending
- "quantum_linear", Linear 3-way monty
- "front_gauss", Gamma Descending
- "middle_gauss", Scaled Gaussian
- "back_gauss", Gamma Ascending
- "quantum_gauss", Gaussian 3-way monty
- "front_poisson", Front 1/3 Mean Poisson
- "middle_poisson", Middle Mean Poisson
- "back_poisson", Back 1/3 Mean Poisson
- "quantum_poisson", Poisson 3-way monty
- "quantum_monty", Quantum Monty Algorithm, 9-way monty
- "flat_uniform", uniform flat distribution
- "truffle_shuffle", TruffleShuffle wide uniform distribution

```python
from Fortuna import FlexCat, d


#                           |- Collection Generator, does not require lambda.
# Data                      |
matrix_data = {#            $                         |- Dynamic Value Expression
    "Cat_A": (f"A{i}" for i in range(1, 6)),  #       |  Lazy, 1 of 4 possibilities
    "Cat_B": ("B1", "B2", "B3", "B4", "B5"),  #       $  lambda required for dynamic eval
    "Cat_C": ("C1", "C2", "C3", f"C4.{d(2)}", lambda: f"C5.{d(4)}"),
}#   $       $       $              $                        $
#    |       |       |- Value       |                        |- Fair die method: d4
#    |       |                      |
#    |       |- Collection          |- Static Value Expression
#    |                              |  Eager, 1 or 2 permanently
#    |- Collection Key, "cat_key"

#                               |- Collection Algorithm     |- Value Algorithm
# Setup                         $  y-axis                   $  x-axis
flex_cat = FlexCat(matrix_data, key_bias="front_linear", val_bias="flat_uniform")
#    $       $       $
#    |       |       |- Dictionary of Collections
#    |       |
#    |       |- FlexCat Constructor
#    |       
#    |- Callable Random Value Generator

# Usage
flex_cat()  # returns a Value from the Matrix.
flex_cat(cat_key="Cat_B")  # returns a Value specifically from the "Cat_B" Collection.
```
### Random Value Functions
`Fortuna.random_value(Sequence[Any]) -> Any`

Essentially the same as Random.choice()
- @param data :: Sequence of Values
- @return :: Random value from the sequence. Flat uniform distribution.

`Fortuna.cumulative_weighted_choice(weighted_table: Sequence[Tuple[int, Any]]) -> Any`

Similar to Random.choices()
- @param weighted_table :: Sequence of weighted value pairs. `[(w1, v1), (w2, v2)...]`
- @return :: Returns a random value. Distribution depends on weights.

### Random Integer Functions
`Fortuna.random_below(limit: int) -> int`
- @param limit :: Any 64bit Integer
- @return :: Returns a random integer in the range...
    - `random_below(N) -> [0, N)` for positive limit.
    - `random_below(N) -> (N, 0]` for negative limit.
    - `random_below(0) -> 0` Always returns zero when limit is zero
- Flat uniform distribution.


`Fortuna.random_int(left_limit: int, right_limit: int) -> int`

Essentially the same as Random.randint()
- @param left_limit :: Any Integer
- @param right_limit :: Any Integer
- @return :: Returns a random integer in the range [left_limit, right_limit]
    - `random_int(1, 10) -> [1, 10]`
    - `random_int(10, 1) -> [1, 10]` same as above.
    - `random_int(A, B)` Always returns A when A == B
- Flat uniform distribution.


`Fortuna.random_range(start: int, stop: int = 0, step: int = 1) -> int`

Essentially the same as Random.randrange()
- @param start :: Required starting point.
    - `random_range(0) -> [0]`
    - `random_range(10) -> [0, 10)` from 0 to 9. Same as `Fortuna.random_index(N)`
    - `random_range(-10) -> [-10, 0)` from -10 to -1. Same as `Fortuna.random_index(-N)`
- @param stop :: Zero by default. Optional range bound. With at least two arguments, the order of the first two does not matter.
    - `random_range(0, 0) -> [0]`
    - `random_range(0, 10) -> [0, 10)` from 0 to 9.
    - `random_range(10, 0) -> [0, 10)` same as above.
- @param step :: One by default. Optional step size.
    - `random_range(0, 0, 0) -> [0]`
    - `random_range(0, 10, 2) -> [0, 10) by 2` even numbers from 0 to 8.
    - The sign of the step parameter controls the phase of the output. Negative stepping will flip the inclusive rule.
    - `random_range(0, 10, -1) -> (0, 10]` starts at 10 and ranges down to 1.
    - `random_range(10, 0, -1) -> (0, 10]` same as above.
    - `random_range(10, 10, 0) -> [10]` step size or range size of zero always returns the first parameter.
- @return :: Returns a random integer in the range [A, B) by increments of C.
- Flat uniform distribution.


`Fortuna.d(sides: int) -> int`

Represents a single roll of a given size die.
- @param sides :: Represents the size or number of sides, most commonly six.
- @return :: Returns a random integer in the range [1, sides].
- Flat uniform distribution.


`Fortuna.dice(rolls: int, sides: int) -> int`

Represents the sum total of multiple rolls of the same size die.
- @param rolls :: Represents the number of times to roll the die.
- @param sides :: Represents the die size or number of sides, most commonly six.
- @return :: Returns a random integer in range [X, Y] where X = rolls and Y = rolls * sides.
- Geometric distribution based on the number and size of the dice rolled.
- Complexity scales primarily with the number of rolls, not the size of the dice.


`Fortuna.plus_or_minus(number: int) -> int`
- @param number :: input to determine the output distribution range.
- @return :: Returns a random integer in range [-number, number].
- Flat uniform distribution.


`Fortuna.plus_or_minus_linear(number: int) -> int`
- @param number :: input to determine the output distribution range.
- @return :: Returns a random integer in range [-number, number].
- Linear geometric, 45 degree triangle distribution centered on zero.


`Fortuna.plus_or_minus_gauss(number: int) -> int`
- @param number :: input to determine the output distribution range.
- @return :: Returns a random integer in range [-number, number].
- Stretched gaussian distribution centered on zero.


`Fortuna.binomial_variate(number_of_trials: int, probability: float) -> int`
- Based on the idea of flipping a coin and counting how many heads come up after some number of flips.
- @param number_of_trials :: how many times to flip a coin.
- @param probability :: how likely heads will be flipped. 0.5 is a fair coin. 1.0 is a double-headed coin.
- @return :: count of how many heads came up.


`Fortuna.negative_binomial_variate(trial_successes: int, probability: float) -> int`
- Based on the idea of flipping a coin as long as it takes to succeed.
- @param trial_successes :: the required number of heads flipped to succeed.
- @param probability :: how likely heads will be flipped. 0.50 is a fair coin.
- @return :: the count of how many tails came up before the required number of heads.


`Fortuna.geometric_variate(probability: float) -> int`
- Same as random_negative_binomial(1, probability). 


`Fortuna.poisson_variate(mean: float) -> int`
- @param mean :: sets the average output of the function.
- @return :: random integer, poisson distribution centered on the mean.


### Random Index, ZeroCool Specification
ZeroCool Methods are used to generate random Sequence indices.

ZeroCool methods must have the following properties:
- Any distribution model is acceptable such that...
- The method or function must take exactly one Integer parameter N.
- The method returns a random int in range `[0, N)` for positive values of N.
- The method returns a random int in range `[N, 0)` for negative values of N.
- This symmetry matches how python can index a list from the back for negative values or the front for positive values of N.


```python
from Fortuna import random_index


some_list = [i for i in range(100)] # [0..99]

print(some_list[random_index(10)])  # prints one of the first 10 items of some_list, [0, 9]
print(some_list[random_index(-10)])  # prints one of the last 10 items of some_list, [90, 99]
```
### ZeroCool Methods
- `Fortuna.random_index(size: int) -> int` Flat uniform distribution
- `Fortuna.front_gauss(size: int) -> int` Gamma Distribution: Front Peak
- `Fortuna.middle_gauss(size: int) -> int` Stretched Gaussian Distribution: Median Peak
- `Fortuna.back_gauss(size: int) -> int` Gamma Distribution: Back Peak
- `Fortuna.quantum_gauss(size: int) -> int` Quantum Gaussian: Three-way Monty
- `Fortuna.front_poisson(size: int) -> int` Poisson Distribution: Front 1/3 Peak
- `Fortuna.middle_poisson(size: int) -> int` Poisson Distribution: Middle Peak
- `Fortuna.back_poisson(size: int) -> int` Poisson Distribution: Back 1/3 Peak
- `Fortuna.quantum_poisson(size: int) -> int` Quantum Poisson: Three-way Monty
- `Fortuna.front_geometric(size: int) -> int` Linear Geometric: 45 Degree Front Peak
- `Fortuna.middle_geometric(size: int) -> int` Linear Geometric: 45 Degree Middle Peak
- `Fortuna.back_geometric(size: int) -> int` Linear Geometric: 45 Degree Back Peak
- `Fortuna.quantum_geometric(size: int) -> int` Quantum Geometric: Three-way Monty
- `Fortuna.quantum_monty(size: int) -> int` Quantum Monty: Nine-way Monty

```python
from Fortuna import front_gauss, middle_gauss, back_gauss, quantum_gauss


some_list = [i for i in range(100)]

# Each of the following prints one of the first 10 items of some_list with the appropriate distribution
print(some_list[front_gauss(10)])
print(some_list[middle_gauss(10)])
print(some_list[back_gauss(10)])
print(some_list[quantum_gauss(10)])

# Each of the following prints one of the last 10 items of some_list with the appropriate distribution
print(some_list[front_gauss(-10)])  
print(some_list[middle_gauss(-10)])  
print(some_list[back_gauss(-10)])  
print(some_list[quantum_gauss(-10)])
```

### Random Float Functions
`Fortuna.canonical() -> float`
- @return :: random float in range [0.0, 1.0), flat uniform.

`Fortuna.random_float(a: Float, b: Float) -> Float`
- @param a :: Float input
- @param b :: Float input
- @return :: random Float in range `[a, b)`, flat uniform distribution.

`Fortuna.triangular(low: Float, high: Float, mode: Float) -> Float`
- @param low :: Float, minimum output
- @param high :: Float, maximum output
- @param mode :: Float, most common output, mode must be in range `[low, high]`
- @return :: random Float in range `[low, high]` with a linear distribution about the mode.

`Fortuna.normal_variate(mean: Float, std_dev: Float) -> Float`
- @param mean :: Float, sets the average output of the function.
- @param std_dev :: Float, standard deviation. Specifies spread of data from the mean.

`Fortuna.lognormal_variate(log_mean: Float, log_deviation: Float) -> Float`
- @param log_mean :: Float, sets the log of the mean of the function.
- @param log_deviation :: Float, log of the standard deviation. Specifies spread of data from the mean.

`Fortuna.exponential_variate(lambda_rate: Float) -> Float`
- Produces random non-negative floating-point values, distributed according to probability density function.
- @param lambda_rate :: Float, λ constant rate of a random event per unit of time/distance.
- @return :: Float, the time/distance until the next random event. For example, this distribution describes the time between the clicks of a Geiger counter or the distance between point mutations in a DNA strand.

`Fortuna.gamma_variate(shape: Float, scale: Float) -> Float`
- Generalization of the exponential distribution.
- Produces random positive floating-point values, distributed according to probability density function.    
- @param shape :: Float, α the number of independent exponentially distributed random variables.
- @param scale :: Float, β the scale factor or the mean of each of the distributed random variables.
- @return :: Float, the sum of α independent exponentially distributed random variables, each of which has a mean of β.

`Fortuna.weibull_variate(shape: Float, scale: Float) -> Float`
- Generalization of the exponential distribution.
- Similar to the gamma distribution but uses a closed form distribution function.
- Popular in reliability and survival analysis.

`Fortuna.extreme_value_variate(location: Float, scale: Float) -> Float`
- Based on Extreme Value Theory. 
- Used for statistical models of the magnitude of earthquakes and volcanoes.

`Fortuna.chi_squared_variate(degrees_of_freedom: Float) -> Float`
- Used with the Chi Squared Test and Null Hypotheses to test if sample data fits an expected distribution.

`Fortuna.cauchy_variate(location: Float, scale: Float) -> Float`
- @param location :: Float, specifies the location of the peak. The default value is 0.0.
- @param scale :: Float, represents the half-width at half-maximum. The default value is 1.0.
- @return :: Float, Continuous Distribution.

`Fortuna.fisher_f_variate(degrees_of_freedom_1: Float, degrees_of_freedom_2: Float) -> Float`
- F distributions often arise when comparing ratios of variances.

`Fortuna.student_t_variate(degrees_of_freedom: Float) -> Float`
- T distribution. Same as a normal distribution except it uses the sample standard deviation rather than the population standard deviation.
- As degrees_of_freedom goes to infinity it converges with the normal distribution.

`Fortuna.beta_variate(alpha: Float, beta: Float) -> Float`

`Fortuna.pareto_variate(alpha: Float) -> Float`

`Fortuna.vonmises_variate(mu: Float, kappa: Float) -> Float`


### Random Truth Functions
`Fortuna.percent_true(truth_factor: Float = 50.0) -> Boolean`
- Produces a distribution of boolean values.
- @param truth_factor :: Float, probability of True as a percentage. Default is 50 percent. Expected input range: `[0.0, 100.0]`, clamped.
- @return :: Produces True or False based on the truth_factor as a percent of true.

`Fortuna.bernoulli_variate(ratio_of_truth: Float) -> Boolean`
- Produces a Bernoulli distribution of boolean values.
- @param ratio_of_truth :: Float, the probability of True as a ratio. Expected input range: `[0.0, 1.0]`, clamped.
- @return :: True or False


### Shuffle Algorithm
`Fortuna.shuffle(array: List[Any]) -> None`
- Knuth B Shuffle Algorithm. Destructive, in-place shuffle.
- @param array :: List to be shuffled.
- @return :: None

`Fortuna.knuth_a(array: List[Any]) -> None`
- Knuth A Shuffle Algorithm. Destructive, in-place shuffle.
- @param array :: List to be shuffled.
- @return :: None

`Fortuna.fisher_yates(array: List[Any]) -> None`
- Fisher Yates Shuffle Algorithm. Destructive, in-place shuffle.
- @param array :: List to be shuffled.
- @return :: None


### Utilities
`Fortuna.sample(population: Sequence, k: int) -> List`
- Replacement for `random.sample`, approximately 2x performance.
- @param population :: Sequence of Any.
- @param k :: Represents the number of samples to be returned. Param k must be <= len(population).
- @return :: Returns list of k random samples from the population data without duplication.

`Fortuna.flatten(maybe_callable, *args, flat=True, **kwargs) -> flatten(maybe_callable(*args, **kwargs))`
- Recursively calls the input object and returns the result. The arguments are only passed in on the first evaluation.
- If the maybe_callable is not callable it is simply returned without error. 
- Conceptually this is somewhat like collapsing the wave function. Often used as the last step in lazy evaluation.
- @param maybe_callable :: Any Object that might be callable.
- @param flat :: Boolean, default is True. Optional, keyword only. Disables flattening if flat is set to False, conceptually turns flatten into the identity function.
- @param *args, **kwargs :: Optional arguments used to flatten the maybe_callable object.
- @return :: Recursively Flattened Object.

`Fortuna.smart_clamp(target: int, lo: int, hi: int) -> int`
- Used to clamp the target in range `[lo, hi]` by saturating the bounds.
- Essentially the same as median for exactly three integers.
- @return :: Returns the middle value, input order does not matter (unlike std::clamp).

`Fortuna.float_clamp(target: float, lo: float, hi: float) -> float`
- Used to clamp the target in range `[lo, hi]` by saturating the bounds.
- Essentially the same as median for exactly three floats.
- @return :: Returns the middle value, input order does not matter (unlike std::clamp).

`Fortuna.distribution_range(func: Callable, lo: int, hi: int) -> Callable`
Higher-order function for producing integer distribution ranges based on a ZeroCool function.
If given a function like random_below, this function will produce random values
with the same distribution but in the range lo to hi, rather than from zero to N-1.
Essentially, this turns a function like random_below(B+1) into random_int(A, B).

- @param func: ZeroCool random distribution, F(N) -> `[0, N-1]`
- @param lo: minimum limit
- @param hi: maximum limit
- @return: Callable() -> int
    - @return: random value in range `[lo, hi]`

`Fortuna.max_uint() -> int`
Maximum unsigned integer. Should be 18446744073709551615.

`Fortuna.max_int() -> int`
Maximum integer. Should be 9223372036854775807.

`Fortuna.min_int() -> int`
Minimum integer. Should be -9223372036854775807.

`Fortuna.max_float() -> float`
Maximum floating point. Should be 1.7976931348623157e+308.

`Fortuna.min_float() -> float`
Minimum floating point. Should be -1.7976931348623157e+308.

`Fortuna.min_above() -> float`
Minimum float above zero. Should be 5e-324.

`Fortuna.min_below() -> float`
Minimum float below zero. Should be -5e-324.

## Fortuna Development Log

##### Fortuna 5.2.1
- Bug fix (TruffleShuffle)

##### Fortuna 5.2.0
- Adds `QuantumMonty.cycle` method
  - Supports FlexCat

##### Fortuna 5.1.4
- Documentation Update
- Updates Installation Script
  - Darwin now uses "-std=c++20"
  - Linux now uses "-std=c++17"

##### Fortuna 5.1.3
- Storm 3.8.0 update
- No longer requires Python.h

##### Fortuna 5.1.2
- Storm 3.7.1 update

- ##### Fortuna 5.1.1
- Storm 3.7.0 update

##### Fortuna 5.1.0
- Storm 3.6.4 update

##### Fortuna 5.0.7
- Installer patch

##### Fortuna 5.0.6
- Storm 3.6.3 update

##### Fortuna 5.0.5
- Documentation Update

##### Fortuna 5.0.4
- Performance Tuning

##### Fortuna 5.0.3
- Test Update

##### Fortuna 5.0.2
- Performance Tuning

##### Fortuna 5.0.1
- Bug Fixes

##### Fortuna 5.0.0
- Adds MSVC support

##### Fortuna 4.4.4
- Installation bug fix

##### Fortuna 4.4.3
- Storm 3.6.0 update
  - Removes Storm::Engine::engine
  - Fixes type bug in Storm::Meters::max_uint
- Performance tests now use Python 3.10
  - Incidental ~25% performance boost
- Removes MonkeyScope as a requirement
  - MonkeyScope should be installed separately

##### Fortuna 4.4.2
- Storm 3.5.8 update
  - Adds float_clamp
  - Adds max_uint

##### Fortuna 4.4.1
- Updates documentation
- Fixes typos

##### Fortuna 4.4.0
- Storm 3.5.7 update
- Adds seeding: Storm::Engine::seed

##### Fortuna 4.3.5
- Performance update `sample`

##### Fortuna 4.3.4
- Added `sample`

##### Fortuna 4.3.3
- TruffleShuffle update

##### Fortuna 4.3.2
- Fixes installer for Google Colab

##### Fortuna 4.3.1
- Fixes installer for Linux

##### Fortuna 4.3.0
- Updates Storm to 3.5.5
- Adds minor documentation
- Updates tests
- Installer now requires C++20 compiler

##### Fortuna 4.2.3
- Updates Storm to 3.5.4

##### Fortuna 4.2.2
- Updates Storm to 3.5.3

##### Fortuna 4.2.1
- Updates Storm to 3.5.1

##### Fortuna 4.2.0
- Fixes a few docstrings, expands example code

##### Fortuna 4.1.9
- Updates documentation - installation notes, copyright date and other small tweaks

##### Fortuna 4.1.8
- Updates performance test output for Fortuna 4.1.x on Big Sur with Python 3.9.x

##### Fortuna 4.1.7
- Adds GitHub repo link to the project for PyPi
- Adds minor documentation & example file updates

##### Fortuna 4.1.6
- Fixes 'zero rolls' bug in 'dice()'

##### Fortuna 4.1.5
- Fixes minor bug

##### Fortuna 4.1.4
- Updates requirements.txt

##### Fortuna 4.1.3
- Small refactoring

##### Fortuna 4.1.2
- Updates tests

##### Fortuna 4.1.1
- Fixes some minor typos

##### Fortuna 4.1.0
- Adds distribution_range utility

##### Fortuna 4.0.0
- RNG merge, adds all features from the RNG library that were not already here

##### Fortuna 3.20.3
- Minor low level Storm update
- Minor test tweaks

##### Fortuna 3.20.2
- adds example: fortuna_extras/multi_threading.py

##### Fortuna 3.20.1
- fixes typos

##### Fortuna 3.20.0
- Updates Storm: 3.4.0: Storm is now Thread Safe
- Adds platform limit meters
- Deprecates MultiChoice

##### Fortuna 3.19.1
- fixes typos

##### Fortuna 3.19.0
- Storm 3.3.6 update

##### Fortuna 3.18.2
- Fixes typos

##### Fortuna 3.18.1
- Installer update

##### Fortuna 3.18.0
- Performance Enhancement
- Storm 3.3.4 update
- updated test output

##### Fortuna 3.17.13
- Fixes some typos

##### Fortuna 3.17.12
- Adds pyproject.toml file to ease the installation process

##### Fortuna 3.17.11
- Documentation Update

##### Fortuna 3.17.10
- Documentation Update

##### Fortuna 3.17.9
- Typo

##### Fortuna 3.17.8
- Typo

##### Fortuna 3.17.7
- Typo

##### Fortuna 3.17.6
- Documentation update

##### Fortuna 3.17.5
- Typos

##### Fortuna 3.17.4
- Reorganized

##### Fortuna 3.17.3
- Streamlining: dropped auxiliary packages.

##### Fortuna 3.17.2
- Documentation update

##### Fortuna 3.17.1
- Update for backwards compatibility for platforms that do not support std::clamp.

##### Fortuna 3.17.0, internal
- Installation issue detected on some platforms that lack std::clamp.

##### Fortuna 3.16.9
- Documentation Update

##### Fortuna 3.16.8
- TruffleShuffle update
- Adds truffle_shuffle()

##### Fortuna 3.16.7
- Documentation Update

##### Fortuna 3.16.6
- Adds distribution_range()

##### Fortuna 3.16.5
- Documentation Update

##### Fortuna 3.16.4
- Documentation Update

##### Fortuna 3.16.3
- Major TruffleShuffle performance upgrade

##### Fortuna 3.16.2 - Internal
- Testing

##### Fortuna 3.16.1
- Documentation Update

##### Fortuna 3.16.0
- Storm 3.3.2 Update

##### Fortuna 3.15.1
- Docs updated

##### Fortuna 3.15.0
- Type Hints Clarified via Typing Module

##### Fortuna 3.14.1
- Fixed another installer bug affecting gcc.

##### Fortuna 3.14.0
- Minor TruffleShuffle Update
- Fisher Yates, and Knuth A Shuffle Algorithms added for comparison with Fortuna.shuffle()
    - Some platforms may prefer one over another. Intel favors Knuth B (Fortuna.shuffle) by more than double.

##### Fortuna 3.13.0 - Internal
- Development & Testing Environment Updated to Python 3.8
    - Python3.8 brings a 10-20% performance boost over all.
- RandomValue API redesign. Dependency Injection is now handled at instantiation rather than call time.

##### Fortuna 3.12.2
- Installer update.
- Clarified the docs for MultiChoice.

##### Fortuna 3.12.1
- MultiChoice now accepts a default.

##### Fortuna 3.12.0
- MultiChoice added

##### Fortuna 3.10.2
- Doc string update for clarity.
- Test update
- MonkeyScope Update

##### Fortuna 3.10.1
- Documentation fix, RandomValue examples are now together.

##### Fortuna 3.10.0
- Fortuna now includes both RNG and Pyewacket.
- Documentation update.

##### Fortuna 3.9.11
- Installer Update, properly installs MonkeyScope as intended.

##### Fortuna 3.9.10
- Fixed Typos

##### Fortuna 3.9.9
- Docs Update

##### Fortuna 3.9.8
- Test Update

##### Fortuna 3.9.7
- Tests for RNG and Pyewacket are now included in `fortuna_extras` package.

##### Fortuna 3.9.6
- Documentation update.

##### Fortuna 3.9.5
- Storm 3.2.2 Update.

##### Fortuna 3.9.4
- Documentation update.

##### Fortuna 3.9.3
- MonkeyScope update, 10% test suite performance improvement.

##### Fortuna 3.9.2
- Documentation update.

##### Fortuna 3.9.1
- `flatten_with` has been renamed to `flatten`. This should be non-breaking, please report any bugs.

##### Fortuna 3.9.0 - Internal
- Added many doc strings.
- Corrected many typos in Docs.
- The `flatten` function has been fully replaced by `flatten_with`. 
    - All classes that support automatic flattening can now accept arbitrary arguments at call time.
    - `flatten_with` will be renamed to `flatten` in a future release.

##### Fortuna 3.8.9
- Fixed some typos.

##### Fortuna 3.8.8
- Fortuna now supports Python notebooks, python3.6 or higher required.

##### Fortuna 3.8.7
- Storm Update

##### Fortuna 3.8.6
- Attempting to make Fortuna compatible with Python Notebooks. 

##### Fortuna 3.8.5
- Installer Config Update

##### Fortuna 3.8.4
- Installer Config Update

##### Fortuna 3.8.3
- Storm Update 3.2.0

##### Fortuna 3.8.2
- More Typo Fix

##### Fortuna 3.8.1
- Typo Fix

##### Fortuna 3.8.0
- Major API Update, several utilities have been deprecated. See MonkeyScope for replacements.
    - distribution
    - distribution_timer
    - timer

##### Fortuna 3.7.7
- Documentation Update

##### Fortuna 3.7.6
- Install script update.

##### Fortuna 3.7.5 - internal
- Storm 3.1.1 Update
- Added triangular function.

##### Fortuna 3.7.4
- Fixed: missing header in the project manifest, this may have caused building from source to fail.

##### Fortuna 3.7.3
- Storm Update

##### Fortuna 3.7.2
- Storm Update

##### Fortuna 3.7.1
- Bug fixes

##### Fortuna 3.7.0 - internal
- flatten_with() is now the default flattening algorithm for all Fortuna classes.

##### Fortuna 3.6.5
- Documentation Update
- RandomValue: New flatten-with-arguments functionality.

##### Fortuna 3.6.4
- RandomValue added for testing

##### Fortuna 3.6.3
- Developer Update

##### Fortuna 3.6.2
- Installer Script Update

##### Fortuna 3.6.1
- Documentation Update

##### Fortuna 3.6.0
- Storm Update
- Test Update
- Bug fix for random_range(), negative stepping is now working as intended. This bug was introduced in 3.5.0.
- Removed Features
    - lazy_cat(): use QuantumMonty class instead.
    - flex_cat(): use FlexCat class instead.
    - truffle_shuffle(): use TruffleShuffle class instead.

##### Fortuna 3.5.3 - internal
- Features added for testing & development
    - ActiveChoice class
    - random_rotate() function

##### Fortuna 3.5.2
- Documentation Updates

##### Fortuna 3.5.1
- Test Update

##### Fortuna 3.5.0
- Storm Update
- Minor Bug Fix: Truffle Shuffle
- Deprecated Features
    - lazy_cat(): use QuantumMonty class instead.
    - flex_cat(): use FlexCat class instead.
    - truffle_shuffle(): use TruffleShuffle class instead.

##### Fortuna 3.4.9
- Test Update

##### Fortuna 3.4.8
- Storm Update

##### Fortuna 3.4.7
- Bug fix for analytic_continuation.

##### Fortuna 3.4.6
- Docs Update

##### Fortuna 3.4.5
- Docs Update
- Range Tests Added, see extras folder.

##### Fortuna 3.4.4
- ZeroCool Algorithm Bug Fixes
- Typos Fixed

##### Fortuna 3.4.3
- Docs Update

##### Fortuna 3.4.2
- Typos Fixed

##### Fortuna 3.4.1
- Major Bug Fix: random_index()

##### Fortuna 3.4.0 - internal
- ZeroCool Poisson Algorithm Family Updated

##### Fortuna 3.3.8 - internal
- Docs Update

##### Fortuna 3.3.7
- Fixed Performance Bug: ZeroCool Linear Algorithm Family

##### Fortuna 3.3.6
- Docs Update

##### Fortuna 3.3.5
- ABI Updates
- Bug Fixes

##### Fortuna 3.3.4
- Examples Update

##### Fortuna 3.3.3
- Test Suite Update

##### Fortuna 3.3.2 - internal
- Documentation Update

##### Fortuna 3.3.1 - internal
- Minor Bug Fix

##### Fortuna 3.3.0 - internal
- Added `plus_or_minus_gauss(N: int) -> int` random int in range [-N, N] Stretched Gaussian Distribution

##### Fortuna 3.2.3
- Small Typos Fixed

##### Fortuna 3.2.2
- Documentation update.

##### Fortuna 3.2.1
- Small Typo Fixed

##### Fortuna 3.2.0
- API updates:
    - QunatumMonty.uniform -> QunatumMonty.flat_uniform
    - QunatumMonty.front -> QunatumMonty.front_linear
    - QunatumMonty.middle -> QunatumMonty.middle_linear
    - QunatumMonty.back -> QunatumMonty.back_linear
    - QunatumMonty.quantum -> QunatumMonty.quantum_linear
    - randindex -> random_index
    - randbelow -> random_below
    - randrange -> random_range
    - randint   -> random_int

##### Fortuna 3.1.0
- `discrete()` has been removed, see Weighted Choice.
- `lazy_cat()` added.
- All ZeroCool methods have been raised to top level API, for use with lazy_cat()

##### Fortuna 3.0.1
- minor typos.

##### Fortuna 3.0.0
- Storm 2 Rebuild.

##### Fortuna 2.1.1
- Small bug fixes.
- Test updates.

##### Fortuna 2.1.0, Major Feature Update
- Fortuna now includes the best of RNG and Pyewacket.

##### Fortuna 2.0.3
- Bug fix.

##### Fortuna 2.0.2
- Clarified some documentation.

##### Fortuna 2.0.1
- Fixed some typos.

##### Fortuna 2.0.0b1-10
- Total rebuild. New RNG Storm Engine.

##### Fortuna 1.26.7.1
- README updated.

##### Fortuna 1.26.7
- Small bug fix.

##### Fortuna 1.26.6
- Updated README to reflect recent changes to the test script.

##### Fortuna 1.26.5
- Fixed small bug in test script.

##### Fortuna 1.26.4
- Updated documentation for clarity.
- Fixed a minor typo in the test script.

##### Fortuna 1.26.3
- Clean build.

##### Fortuna 1.26.2
- Fixed some minor typos.

##### Fortuna 1.26.1
- Release.

##### Fortuna 1.26.0 beta 2
- Moved README and LICENSE files into fortuna_extras folder.

##### Fortuna 1.26.0 beta 1
- Dynamic version scheme implemented.
- The Fortuna Extension now requires the fortuna_extras package, previously it was optional.

##### Fortuna 1.25.4
- Fixed some minor typos in the test script.

##### Fortuna 1.25.3
- Since version 1.24 Fortuna requires Python 3.7 or higher. This patch corrects an issue where the setup script incorrectly reported requiring Python 3.6 or higher.

##### Fortuna 1.25.2
- Updated test suite.
- Major performance update for TruffleShuffle.
- Minor performance update for QuantumMonty & FlexCat: cycle monty.

##### Fortuna 1.25.1
- Important bug fix for TruffleShuffle, QuantumMonty and FlexCat.

##### Fortuna 1.25
- Full 64bit support.
- The Distribution & Performance Tests have been redesigned.
- Bloat Control: Two experimental features have been removed.
    - RandomWalk
    - CatWalk
- Bloat Control: Several utility functions have been removed from the top level API. These function remain in the Fortuna namespace for now, but may change in the future without warning.
    - stretch_bell, internal only.
    - min_max, not used anymore.
    - analytic_continuation, internal only.
    - flatten, internal only.

##### Fortuna 1.24.3
- Low level refactoring, non-breaking patch.

##### Fortuna 1.24.2
- Setup config updated to improve installation.

##### Fortuna 1.24.1
- Low level patch to avoid potential ADL issue. All low level function calls are now qualified.

##### Fortuna 1.24
- Documentation updated for even more clarity.
- Bloat Control: Two utility functions that are no longer used in the module have been removed.
    - n_samples -> use a list comprehension instead. `[f(x) for _ in range(n)]`
    - bind -> use a lambda instead. `lambda: f(x)`

##### Fortuna 1.23.7
- Documentation updated for clarity.
- Minor bug fixes.
- TruffleShuffle has been redesigned slightly, it now uses a random rotate instead of swap.
- Custom `__repr__` methods have been added to each class.

##### Fortuna 1.23.6
- New method for QuantumMonty: quantum_not_monty - produces the upside down quantum_monty.
- New bias option for FlexCat: not_monty.

##### Fortuna 1.23.5.1
- Fixed some small typos.

##### Fortuna 1.23.5
- Documentation updated for clarity.
- All sequence wrappers can now accept generators as input.
- Six new functions added:
    - random_float() -> float in range [0.0..1.0) exclusive, uniform flat distribution.
    - percent_true_float(num: float) -> bool, Like percent_true but with floating point precision.
    - plus_or_minus_linear_down(num: int) -> int in range [-num..num], upside down pyramid.
    - plus_or_minus_curve_down(num: int) -> int in range [-num..num], upside down bell curve.
    - mostly_not_middle(num: int) -> int in range [0..num], upside down pyramid.
    - mostly_not_center(num: int) -> int in range [0..num], upside down bell curve.
- Two new methods for QuantumMonty:
    - mostly_not_middle
    - mostly_not_center
- Two new bias options for FlexCat, either can be used to define x and/or y-axis bias:
    - not_middle
    - not_center

##### Fortuna 1.23.4.2
- Fixed some minor typos in the README.md file.

##### Fortuna 1.23.4.1
- Fixed some minor typos in the test suite.

##### Fortuna 1.23.4
- Fortuna is now Production/Stable!
- Fortuna and Fortuna Pure now use the same test suite.

##### Fortuna 0.23.4, first release candidate.
- RandomCycle, BlockCycle and TruffleShuffle have been refactored and combined into one class: TruffleShuffle.
- QuantumMonty and FlexCat will now use the new TruffleShuffle for cycling.
- Minor refactoring across the module.

##### Fortuna 0.23.3, internal
- Function shuffle(arr: list) added.

##### Fortuna 0.23.2, internal
- Simplified the plus_or_minus_curve(num: int) function, output will now always be bounded to the range [-num..num].
- Function stretched_bell(num: int) added, this matches the previous behavior of an unbounded plus_or_minus_curve.

##### Fortuna 0.23.1, internal
- Small bug fixes and general clean up.

##### Fortuna 0.23.0
- The number of test cycles in the test suite has been reduced to 10,000 (down from 100,000). The performance of the pure python implementation and the c-extension are now directly comparable.
- Minor tweaks made to the examples in `.../fortuna_extras/fortuna_examples.py`

##### Fortuna 0.22.2, experimental features
- BlockCycle class added.
- RandomWalk class added.
- CatWalk class added.

##### Fortuna 0.22.1
- Fortuna classes no longer return lists of values, this behavior has been extracted to a free function called n_samples.

##### Fortuna 0.22.0, experimental features
- Function bind added.
- Function n_samples added.

##### Fortuna 0.21.3
- Flatten will no longer raise an error if passed a callable item that it can't call. It correctly returns such items in an uncalled state without error.
- Simplified `.../fortuna_extras/fortuna_examples.py` - removed unnecessary class structure.

##### Fortuna 0.21.2
- Fix some minor bugs.

##### Fortuna 0.21.1
- Fixed a bug in `.../fortuna_extras/fortuna_examples.py`

##### Fortuna 0.21.0
- Function flatten added.
- Flatten: The Fortuna classes will recursively unpack callable objects in the data set.

##### Fortuna 0.20.10
- Documentation updated.

##### Fortuna 0.20.9
- Minor bug fixes.

##### Fortuna 0.20.8, internal
- Testing cycle for potential new features.

##### Fortuna 0.20.7
- Documentation updated for clarity.

##### Fortuna 0.20.6
- Tests updated based on recent changes.

##### Fortuna 0.20.5, internal
- Documentation updated based on recent changes.

##### Fortuna 0.20.4, internal
- WeightedChoice (both types) can optionally return a list of samples rather than just one value, control the length of the list via the n_samples argument.

##### Fortuna 0.20.3, internal
- RandomCycle can optionally return a list of samples rather than just one value,
control the length of the list via the n_samples argument.

##### Fortuna 0.20.2, internal
- QuantumMonty can optionally return a list of samples rather than just one value,
control the length of the list via the n_samples argument.

##### Fortuna 0.20.1, internal
- FlexCat can optionally return a list of samples rather than just one value,
control the length of the list via the n_samples argument.

##### Fortuna 0.20.0, internal
- FlexCat now accepts a standard dict as input. The ordered(ness) of dict is now part of the standard in Python 3.7.1. Previously FlexCat required an OrderedDict, now it accepts either and treats them the same.

##### Fortuna 0.19.7
- Fixed bug in `.../fortuna_extras/fortuna_examples.py`.

##### Fortuna 0.19.6
- Updated documentation formatting.
- Small performance tweak for QuantumMonty and FlexCat.

##### Fortuna 0.19.5
- Minor documentation update.

##### Fortuna 0.19.4
- Minor update to all classes for better debugging.

##### Fortuna 0.19.3
- Updated plus_or_minus_curve to allow unbounded output.

##### Fortuna 0.19.2
- Internal development cycle.
- Minor update to FlexCat for better debugging.

##### Fortuna 0.19.1
- Internal development cycle.

##### Fortuna 0.19.0
- Updated documentation for clarity.
- MultiCat has been removed, it is replaced by FlexCat.
- Mostly has been removed, it is replaced by QuantumMonty.

##### Fortuna 0.18.7
- Fixed some more README typos.

##### Fortuna 0.18.6
- Fixed some README typos.

##### Fortuna 0.18.5
- Updated documentation.
- Fixed another minor test bug.

##### Fortuna 0.18.4
- Updated documentation to reflect recent changes.
- Fixed some small test bugs.
- Reduced default number of test cycles to 10,000 - down from 100,000.

##### Fortuna 0.18.3
- Fixed some minor README typos.

##### Fortuna 0.18.2
- Fixed a bug with Fortuna Pure.

##### Fortuna 0.18.1
- Fixed some minor typos.
- Added tests for `.../fortuna_extras/fortuna_pure.py`

##### Fortuna 0.18.0
- Introduced new test format, now includes average call time in nanoseconds.
- Reduced default number of test cycles to 100,000 - down from 1,000,000.
- Added pure Python implementation of Fortuna: `.../fortuna_extras/fortuna_pure.py`
- Promoted several low level functions to top level.
    - `zero_flat(num: int) -> int`
    - `zero_cool(num: int) -> int`
    - `zero_extreme(num: int) -> int`
    - `max_cool(num: int) -> int`
    - `max_extreme(num: int) -> int`
    - `analytic_continuation(func: staticmethod, num: int) -> int`
    - `min_max(num: int, lo: int, hi: int) -> int`

##### Fortuna 0.17.3
- Internal development cycle.

##### Fortuna 0.17.2
- User Requested: dice() and d() functions now support negative numbers as input.

##### Fortuna 0.17.1
- Fixed some minor typos.

##### Fortuna 0.17.0
- Added QuantumMonty to replace Mostly, same default behavior with more options.
- Mostly is depreciated and may be removed in a future release.
- Added FlexCat to replace MultiCat, same default behavior with more options.
- MultiCat is depreciated and may be removed in a future release.
- Expanded the Treasure Table example in `.../fortuna_extras/fortuna_examples.py`

##### Fortuna 0.16.2
- Minor refactoring for WeightedChoice.

##### Fortuna 0.16.1
- Redesigned fortuna_examples.py to feature a dynamic random magic item generator.
- Raised cumulative_weighted_choice function to top level.
- Added test for cumulative_weighted_choice as free function.
- Updated MultiCat documentation for clarity.

##### Fortuna 0.16.0
- Pushed distribution_timer to the .pyx layer.
- Changed default number of iterations of tests to 1 million, up form 1 hundred thousand.
- Reordered tests to better match documentation.
- Added Base Case Fortuna.fast_rand_below.
- Added Base Case Fortuna.fast_d.
- Added Base Case Fortuna.fast_dice.

##### Fortuna 0.15.10
- Internal Development Cycle

##### Fortuna 0.15.9
- Added Base Cases for random_value()
- Added Base Case for randint()

##### Fortuna 0.15.8
- Clarified MultiCat Test

##### Fortuna 0.15.7
- Fixed minor typos.

##### Fortuna 0.15.6
- Fixed minor typos.
- Simplified MultiCat example.

##### Fortuna 0.15.5
- Added MultiCat test.
- Fixed some minor typos in docs.

##### Fortuna 0.15.4
- Performance optimization for both WeightedChoice() variants.
- Cython update provides small performance enhancement across the board.
- Compilation now leverages Python3 all the way down.
- MultiCat pushed to the .pyx layer for better performance.

##### Fortuna 0.15.3
- Reworked the MultiCat example to include several randomizing strategies working in concert.
- Added Multi Dice 10d10 performance tests.
- Updated sudo code in documentation to be more pythonic.

##### Fortuna 0.15.2
- Fixed: Linux installation failure.
- Added: complete source files to the distribution (.cpp .hpp .pyx).

##### Fortuna 0.15.1
- Updated & simplified distribution_timer in `fortuna_tests.py`
- Readme updated, fixed some typos.
- Known issue preventing successful installation on some linux platforms.

##### Fortuna 0.15.0
- Performance tweaks.
- Readme updated, added some details.

##### Fortuna 0.14.1
- Readme updated, fixed some typos.

##### Fortuna 0.14.0
- Fixed a bug where the analytic continuation algorithm caused a rare issue during compilation on some platforms.

##### Fortuna 0.13.3
- Fixed Test Bug: percent sign was missing in output distributions.
- Readme updated: added update history, fixed some typos.

##### Fortuna 0.13.2
- Readme updated for even more clarity.

##### Fortuna 0.13.1
- Readme updated for clarity.

##### Fortuna 0.13.0
- Minor Bug Fixes.
- Readme updated for aesthetics.
- Added Tests: `.../fortuna_extras/fortuna_tests.py`

##### Fortuna 0.12.0
- Internal test for future update.

##### Fortuna 0.11.0
- Initial Release: Public Beta

##### Fortuna 0.10.0
- Module name changed from Dice to Fortuna

##### Dice 0.1.x - 0.9.x
- Experimental Phase


## Distribution and Performance Tests
Testbed:
- Hardware: M1 Ultra
- Software: MacOS 13.3, Python 3.11.1

```
MonkeyScope: Fortuna Quick Test
Fortuna Version: 5.1.2
Storm Version: 3.7.1

Smart Clamp: Pass
Float Clamp: Pass

Data:
some_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

Base Case
Output Analysis: Random.choice(some_list)
Typical Timing: 164 ± 6 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 4
 Maximum: 9
 Mean: 4.491
 Std Deviation: 2.888643845001191
Distribution of 100000 samples:
 0: 9.889%
 1: 9.852%
 2: 10.226%
 3: 9.986%
 4: 10.261%
 5: 9.781%
 6: 10.07%
 7: 10.042%
 8: 9.913%
 9: 9.98%

Output Analysis: random_value(some_list)
Typical Timing: 38 ± 2 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 5
 Maximum: 9
 Mean: 4.607
 Std Deviation: 2.9153130277982244
Distribution of 100000 samples:
 0: 10.033%
 1: 10.002%
 2: 9.978%
 3: 9.867%
 4: 9.777%
 5: 10.086%
 6: 9.917%
 7: 10.013%
 8: 10.172%
 9: 10.155%


Wide Distribution

Truffle = TruffleShuffle(some_list)
Output Analysis: Truffle()
Typical Timing: 218 ± 4 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 4
 Maximum: 9
 Mean: 4.423
 Std Deviation: 2.838684401114208
Distribution of 100000 samples:
 0: 10.022%
 1: 10.017%
 2: 9.979%
 3: 10.049%
 4: 9.842%
 5: 10.077%
 6: 9.932%
 7: 9.98%
 8: 10.049%
 9: 10.053%

truffle = truffle_shuffle(some_list)
Output Analysis: truffle()
Typical Timing: 95 ± 2 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 4
 Maximum: 9
 Mean: 4.404
 Std Deviation: 2.8458536299119257
Distribution of 100000 samples:
 0: 10.055%
 1: 9.932%
 2: 10.068%
 3: 10.164%
 4: 9.957%
 5: 9.924%
 6: 9.897%
 7: 9.973%
 8: 10.021%
 9: 10.009%


Single objects with many distribution possibilities

some_tuple = tuple(i for i in range(10))

monty = QuantumMonty(some_tuple)
Output Analysis: monty()
Typical Timing: 244 ± 5 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 5
 Maximum: 9
 Mean: 4.621
 Std Deviation: 2.8473613164588834
Distribution of 100000 samples:
 0: 10.746%
 1: 8.946%
 2: 8.872%
 3: 9.792%
 4: 11.491%
 5: 11.546%
 6: 9.528%
 7: 9.138%
 8: 8.905%
 9: 11.036%

rand_value = <Fortuna.RandomValue object at 0x102259940>
Output Analysis: rand_value()
Typical Timing: 170 ± 2 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 4
 Maximum: 9
 Mean: 4.453
 Std Deviation: 2.927517952355094
Distribution of 100000 samples:
 0: 10.009%
 1: 10.144%
 2: 10.021%
 3: 10.037%
 4: 10.113%
 5: 9.985%
 6: 9.951%
 7: 9.88%
 8: 9.915%
 9: 9.945%


Weighted Tables:

population = ('A', 'B', 'C', 'D')
cum_weights = (1, 3, 6, 10)
rel_weights = (1, 2, 3, 4)
cum_weighted_table = zip(cum_weights, population)
rel_weighted_table = zip(rel_weights, population)

Cumulative Base Case
Output Analysis: Random.choices(population, cum_weights=cum_weights)
Typical Timing: 550 ± 11 ns
Distribution of 100000 samples:
 A: 10.182%
 B: 19.882%
 C: 30.056%
 D: 39.88%

cum_weighted_choice = CumulativeWeightedChoice(cum_weighted_table)
Output Analysis: cum_weighted_choice()
Typical Timing: 178 ± 3 ns
Distribution of 100000 samples:
 A: 9.897%
 B: 20.05%
 C: 29.86%
 D: 40.193%

Output Analysis: cumulative_weighted_choice(tuple(zip(cum_weights, population)))
Typical Timing: 75 ± 1 ns
Distribution of 100000 samples:
 A: 9.975%
 B: 19.875%
 C: 30.033%
 D: 40.117%

Relative Base Case
Output Analysis: Random.choices(population, weights=rel_weights)
Typical Timing: 690 ± 14 ns
Distribution of 100000 samples:
 A: 9.932%
 B: 20.288%
 C: 30.191%
 D: 39.589%

rel_weighted_choice = RelativeWeightedChoice(rel_weighted_table)
Output Analysis: rel_weighted_choice()
Typical Timing: 178 ± 4 ns
Distribution of 100000 samples:
 A: 9.89%
 B: 19.927%
 C: 30.302%
 D: 39.881%


Random Matrix Values:

some_matrix = {'A': (1, 2, 3, 4), 'B': (10, 20, 30, 40), 'C': (100, 200, 300, 400)}

flex_cat = FlexCat(some_matrix)
Output Analysis: flex_cat()
Typical Timing: 393 ± 5 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 4
 Maximum: 400
 Mean: 40.777
 Std Deviation: 89.5261649195653
Distribution of 100000 samples:
 1: 13.776%
 2: 13.988%
 3: 13.872%
 4: 13.712%
 10: 8.328%
 20: 8.38%
 30: 8.29%
 40: 8.407%
 100: 2.791%
 200: 2.834%
 300: 2.819%
 400: 2.803%

Output Analysis: flex_cat("C")
Typical Timing: 278 ± 6 ns
Statistics of 1000 samples:
 Minimum: 100
 Median: 200
 Maximum: 400
 Mean: 249.3
 Std Deviation: 112.03598556741518
Distribution of 100000 samples:
 100: 24.976%
 200: 24.966%
 300: 25.076%
 400: 24.982%


Random Integers:

Base Case
Output Analysis: Random.randrange(10)
Typical Timing: 159 ± 5 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 4
 Maximum: 9
 Mean: 4.36
 Std Deviation: 2.8203464954424224
Distribution of 100000 samples:
 0: 9.972%
 1: 10.044%
 2: 10.104%
 3: 9.889%
 4: 9.935%
 5: 10.141%
 6: 10.088%
 7: 9.837%
 8: 10.063%
 9: 9.927%

Output Analysis: random_below(10)
Typical Timing: 39 ± 1 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 4
 Maximum: 9
 Mean: 4.386
 Std Deviation: 2.8836295391952342
Distribution of 100000 samples:
 0: 9.912%
 1: 9.992%
 2: 9.971%
 3: 10.226%
 4: 9.925%
 5: 9.906%
 6: 10.042%
 7: 9.996%
 8: 9.941%
 9: 10.089%

Output Analysis: random_index(10)
Typical Timing: 44 ± 7 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 4
 Maximum: 9
 Mean: 4.482
 Std Deviation: 2.8712227221028885
Distribution of 100000 samples:
 0: 9.947%
 1: 10.078%
 2: 10.159%
 3: 9.888%
 4: 9.936%
 5: 10.082%
 6: 10.058%
 7: 9.901%
 8: 9.872%
 9: 10.079%

Output Analysis: random_range(10)
Typical Timing: 46 ± 3 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 5
 Maximum: 9
 Mean: 4.685
 Std Deviation: 2.85375523108043
Distribution of 100000 samples:
 0: 9.964%
 1: 10.003%
 2: 10.085%
 3: 10.061%
 4: 9.837%
 5: 9.964%
 6: 10.077%
 7: 9.99%
 8: 9.904%
 9: 10.115%

Output Analysis: random_below(-10)
Typical Timing: 47 ± 3 ns
Statistics of 1000 samples:
 Minimum: -9
 Median: -5
 Maximum: 0
 Mean: -4.481
 Std Deviation: 2.8098993815676985
Distribution of 100000 samples:
 -9: 10.064%
 -8: 9.972%
 -7: 10.058%
 -6: 9.924%
 -5: 10.017%
 -4: 9.993%
 -3: 10.027%
 -2: 9.934%
 -1: 9.967%
 0: 10.044%

Output Analysis: random_index(-10)
Typical Timing: 47 ± 1 ns
Statistics of 1000 samples:
 Minimum: -10
 Median: -6
 Maximum: -1
 Mean: -5.616
 Std Deviation: 2.898092983833152
Distribution of 100000 samples:
 -10: 9.987%
 -9: 9.971%
 -8: 10.066%
 -7: 9.941%
 -6: 9.988%
 -5: 10.067%
 -4: 9.909%
 -3: 9.973%
 -2: 10.098%
 -1: 10.0%

Output Analysis: random_range(-10)
Typical Timing: 65 ± 12 ns
Statistics of 1000 samples:
 Minimum: -10
 Median: -5
 Maximum: -1
 Mean: -5.414
 Std Deviation: 2.8884159927107014
Distribution of 100000 samples:
 -10: 10.125%
 -9: 9.982%
 -8: 10.017%
 -7: 10.087%
 -6: 9.887%
 -5: 9.936%
 -4: 9.908%
 -3: 10.145%
 -2: 9.766%
 -1: 10.147%

Base Case
Output Analysis: Random.randrange(1, 10)
Typical Timing: 203 ± 9 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 5
 Maximum: 9
 Mean: 5.18
 Std Deviation: 2.540088985065691
Distribution of 100000 samples:
 1: 11.125%
 2: 11.089%
 3: 11.142%
 4: 10.882%
 5: 11.286%
 6: 11.115%
 7: 11.092%
 8: 11.051%
 9: 11.218%

Output Analysis: random_range(1, 10)
Typical Timing: 49 ± 3 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 5
 Maximum: 9
 Mean: 5.039
 Std Deviation: 2.535726505147767
Distribution of 100000 samples:
 1: 11.199%
 2: 11.107%
 3: 10.951%
 4: 11.209%
 5: 11.148%
 6: 11.083%
 7: 10.951%
 8: 11.18%
 9: 11.172%

Output Analysis: random_range(10, 1)
Typical Timing: 48 ± 3 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 5
 Maximum: 9
 Mean: 5.031
 Std Deviation: 2.623150761950201
Distribution of 100000 samples:
 1: 11.023%
 2: 11.219%
 3: 11.086%
 4: 11.152%
 5: 11.079%
 6: 11.107%
 7: 11.177%
 8: 11.05%
 9: 11.107%

Base Case
Output Analysis: Random.randint(-5, 5)
Typical Timing: 220 ± 6 ns
Statistics of 1000 samples:
 Minimum: -5
 Median: 0
 Maximum: 5
 Mean: 0.02
 Std Deviation: 3.1886937400396054
Distribution of 100000 samples:
 -5: 9.15%
 -4: 9.054%
 -3: 9.037%
 -2: 9.029%
 -1: 9.223%
 0: 9.066%
 1: 9.073%
 2: 9.035%
 3: 9.233%
 4: 9.058%
 5: 9.042%

Output Analysis: random_int(-5, 5)
Typical Timing: 35 ± 1 ns
Statistics of 1000 samples:
 Minimum: -5
 Median: 0
 Maximum: 5
 Mean: 0.012
 Std Deviation: 3.1134465708519152
Distribution of 100000 samples:
 -5: 8.942%
 -4: 9.134%
 -3: 9.192%
 -2: 9.179%
 -1: 9.084%
 0: 9.173%
 1: 9.006%
 2: 9.034%
 3: 9.112%
 4: 9.055%
 5: 9.089%

Base Case
Output Analysis: Random.randrange(1, 20, 2)
Typical Timing: 220 ± 4 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 11
 Maximum: 19
 Mean: 10.186
 Std Deviation: 5.871275489693519
Distribution of 100000 samples:
 1: 10.09%
 3: 10.048%
 5: 9.948%
 7: 9.913%
 9: 9.944%
 11: 10.047%
 13: 10.0%
 15: 9.984%
 17: 10.134%
 19: 9.892%

Output Analysis: random_range(1, 20, 2)
Typical Timing: 44 ± 2 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 9
 Maximum: 19
 Mean: 10.054
 Std Deviation: 5.71574612397662
Distribution of 100000 samples:
 1: 9.97%
 3: 10.002%
 5: 9.982%
 7: 10.005%
 9: 10.212%
 11: 9.845%
 13: 9.951%
 15: 9.95%
 17: 9.99%
 19: 10.093%

Output Analysis: random_range(1, 20, -2)
Typical Timing: 47 ± 3 ns
Statistics of 1000 samples:
 Minimum: 2
 Median: 10
 Maximum: 20
 Mean: 10.882
 Std Deviation: 5.576483943595029
Distribution of 100000 samples:
 2: 9.869%
 4: 9.982%
 6: 10.228%
 8: 9.958%
 10: 10.173%
 12: 9.988%
 14: 10.092%
 16: 9.93%
 18: 9.786%
 20: 9.994%

Output Analysis: random_range(20, 1, -2)
Typical Timing: 44 ± 1 ns
Statistics of 1000 samples:
 Minimum: 2
 Median: 10
 Maximum: 20
 Mean: 10.862
 Std Deviation: 5.692570716412872
Distribution of 100000 samples:
 2: 9.948%
 4: 10.082%
 6: 10.065%
 8: 9.915%
 10: 9.884%
 12: 10.139%
 14: 10.002%
 16: 10.068%
 18: 9.991%
 20: 9.906%

Output Analysis: d(10)
Typical Timing: 34 ± 2 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 5
 Maximum: 10
 Mean: 5.361
 Std Deviation: 2.7871934714776168
Distribution of 100000 samples:
 1: 10.05%
 2: 9.853%
 3: 9.925%
 4: 10.017%
 5: 9.803%
 6: 10.109%
 7: 10.25%
 8: 10.022%
 9: 10.006%
 10: 9.965%

Output Analysis: dice(3, 6)
Typical Timing: 63 ± 2 ns
Statistics of 1000 samples:
 Minimum: 3
 Median: 10
 Maximum: 18
 Mean: 10.492
 Std Deviation: 2.95002349798076
Distribution of 100000 samples:
 3: 0.439%
 4: 1.394%
 5: 2.738%
 6: 4.658%
 7: 6.774%
 8: 9.546%
 9: 11.656%
 10: 12.661%
 11: 12.433%
 12: 11.671%
 13: 9.687%
 14: 7.023%
 15: 4.691%
 16: 2.818%
 17: 1.325%
 18: 0.486%

Output Analysis: ability_dice(4)
Typical Timing: 131 ± 4 ns
Statistics of 1000 samples:
 Minimum: 3
 Median: 12
 Maximum: 18
 Mean: 12.239
 Std Deviation: 2.904878193198007
Distribution of 100000 samples:
 3: 0.074%
 4: 0.341%
 5: 0.766%
 6: 1.633%
 7: 2.935%
 8: 4.72%
 9: 6.903%
 10: 9.367%
 11: 11.491%
 12: 13.004%
 13: 13.211%
 14: 12.332%
 15: 10.136%
 16: 7.258%
 17: 4.235%
 18: 1.594%

Output Analysis: plus_or_minus(5)
Typical Timing: 32 ± 2 ns
Statistics of 1000 samples:
 Minimum: -5
 Median: 0
 Maximum: 5
 Mean: 0.048
 Std Deviation: 3.1729739620368402
Distribution of 100000 samples:
 -5: 9.161%
 -4: 9.14%
 -3: 9.012%
 -2: 9.173%
 -1: 8.87%
 0: 9.064%
 1: 9.161%
 2: 9.2%
 3: 9.151%
 4: 9.014%
 5: 9.054%

Output Analysis: plus_or_minus_linear(5)
Typical Timing: 45 ± 2 ns
Statistics of 1000 samples:
 Minimum: -5
 Median: 0
 Maximum: 5
 Mean: -0.009
 Std Deviation: 2.4873894158547243
Distribution of 100000 samples:
 -5: 2.781%
 -4: 5.673%
 -3: 8.405%
 -2: 11.1%
 -1: 13.847%
 0: 16.669%
 1: 13.865%
 2: 11.004%
 3: 8.224%
 4: 5.546%
 5: 2.886%

Output Analysis: plus_or_minus_gauss(5)
Typical Timing: 54 ± 3 ns
Statistics of 1000 samples:
 Minimum: -5
 Median: 0
 Maximum: 5
 Mean: -0.043
 Std Deviation: 1.6098890467180471
Distribution of 100000 samples:
 -5: 0.195%
 -4: 1.15%
 -3: 4.418%
 -2: 11.541%
 -1: 20.292%
 0: 24.659%
 1: 20.553%
 2: 11.374%
 3: 4.432%
 4: 1.193%
 5: 0.193%


Random Floats:

Base Case
Output Analysis: Random.random()
Typical Timing: 20 ± 1 ns
Statistics of 1000 samples:
 Minimum: 0.000142782747727499
 Median: (0.47611225355861486, 0.478104618492992)
 Maximum: 0.9997673550591981
 Mean: 0.4846712316389709
 Std Deviation: 0.29445228449838595
round distribution of 100000:
 0: 50.027%
 1: 49.973%

Output Analysis: canonical()
Typical Timing: 24 ± 1 ns
Statistics of 1000 samples:
 Minimum: 0.00011940616671560987
 Median: (0.5336037809343693, 0.5338013616706963)
 Maximum: 0.9998526038434692
 Mean: 0.5071817671541653
 Std Deviation: 0.2881289353266108
round distribution of 100000:
 0: 49.91%
 1: 50.09%

Output Analysis: random_float(0.0, 10.0)
Typical Timing: 25 ± 1 ns
Statistics of 1000 samples:
 Minimum: 0.005097646931662764
 Median: (5.134058844316928, 5.140958185286907)
 Maximum: 9.998064260046263
 Mean: 5.118819952257218
 Std Deviation: 2.9183293613236745
floor distribution of 100000:
 0: 10.133%
 1: 9.991%
 2: 9.801%
 3: 10.026%
 4: 10.087%
 5: 9.832%
 6: 10.049%
 7: 10.109%
 8: 9.924%
 9: 10.048%

Base Case
Output Analysis: Random.triangular(0.0, 10.0, 5.0)
Typical Timing: 138 ± 5 ns
Statistics of 1000 samples:
 Minimum: 0.11029752947732814
 Median: (4.855753095470426, 4.858159193216716)
 Maximum: 9.826447264177135
 Mean: 4.9134451464177245
 Std Deviation: 2.0665159445730845
round distribution of 100000:
 0: 0.46%
 1: 3.965%
 2: 7.838%
 3: 11.963%
 4: 16.094%
 5: 19.087%
 6: 16.09%
 7: 12.19%
 8: 7.823%
 9: 3.994%
 10: 0.496%

Output Analysis: triangular(0.0, 10.0, 5.0)
Typical Timing: 33 ± 1 ns
Statistics of 1000 samples:
 Minimum: 0.39567829487457745
 Median: (4.980009273126231, 4.989989589620912)
 Maximum: 9.71813997918804
 Mean: 4.996797187556883
 Std Deviation: 2.0982307231113797
round distribution of 100000:
 0: 0.491%
 1: 3.95%
 2: 8.077%
 3: 11.944%
 4: 16.187%
 5: 18.926%
 6: 15.953%
 7: 11.962%
 8: 8.012%
 9: 4.007%
 10: 0.491%


Random Booleans:

Output Analysis: percent_true(33.33)
Typical Timing: 25 ± 3 ns
Statistics of 1000 samples:
 Minimum: False
 Median: False
 Maximum: True
 Mean: 0.316
 Std Deviation: 0.4651455260027343
Distribution of 100000 samples:
 False: 66.55%
 True: 33.45%


Shuffle Performance:

some_small_list = [i for i in range(10)]
some_med_list = [i for i in range(100)]
some_large_list = [i for i in range(1000)]

Base Case:
Random.shuffle()  # fisher_yates in python
Typical Timing: 1388 ± 25 ns
Typical Timing: 13793 ± 1472 ns
Typical Timing: 135680 ± 1085 ns

Fortuna.shuffle()  # knuth_b in cython
Typical Timing: 266 ± 10 ns
Typical Timing: 2363 ± 11 ns
Typical Timing: 22837 ± 337 ns

Fortuna.knuth_a()  # knuth_a in cython
Typical Timing: 476 ± 11 ns
Typical Timing: 4296 ± 52 ns
Typical Timing: 49211 ± 973 ns

Fortuna.fisher_yates()  # fisher_yates in cython
Typical Timing: 550 ± 8 ns
Typical Timing: 4695 ± 338 ns
Typical Timing: 48856 ± 761 ns

smart_clamp(3, 2, 1) # should be 2:  2
Typical Timing: 50 ± 8 ns
float_clamp(3.0, 2.0, 1.0) # should be 2.0:  2.0
Typical Timing: 38 ± 3 ns


-------------------------------------------------------------------------
Total Test Time: 1.599 seconds
```


## Legal Information
Fortuna is licensed under a Creative Commons Attribution-NonCommercial 3.0 Unported License. 
See online version of this license here: <http://creativecommons.org/licenses/by-nc/3.0/>

Other licensing options are available, please contact the author for details: [Robert Sharp](mailto:webmaster@sharpdesigndigital.com)
