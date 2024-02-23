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
    - `log_normal_variate(Float, Float) -> Float`
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

`Fortuna.log_normal_variate(log_mean: Float, log_deviation: Float) -> Float`
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

##### Fortuna 5.3.1
- Adds several float tests

##### Fortuna 5.3.0
- Storm Update v3.9.0
- `lognormal_variate` -> `log_normal_variate`

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
Fortuna Version: 5.3.1
Storm Version: 3.9.0

Smart Clamp: Pass
Float Clamp: Pass

Data:
some_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

Base Case
Output Analysis: Random.choice(some_list)
Typical Timing: 199 ± 13 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 5
 Maximum: 9
 Mean: 4.617
 Std Deviation: 2.8485830557358556
Distribution of 100000 samples:
 0: 10.143%
 1: 9.881%
 2: 9.898%
 3: 10.0%
 4: 10.239%
 5: 9.821%
 6: 9.813%
 7: 10.017%
 8: 10.054%
 9: 10.134%

Output Analysis: random_value(some_list)
Typical Timing: 38 ± 5 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 5
 Maximum: 9
 Mean: 4.526
 Std Deviation: 2.908914881151696
Distribution of 100000 samples:
 0: 10.071%
 1: 10.008%
 2: 9.977%
 3: 10.033%
 4: 10.028%
 5: 9.874%
 6: 10.098%
 7: 9.988%
 8: 10.013%
 9: 9.91%


Wide Distribution

Truffle = TruffleShuffle(some_list)
Output Analysis: Truffle()
Typical Timing: 208 ± 11 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 4
 Maximum: 9
 Mean: 4.444
 Std Deviation: 2.8953837823762236
Distribution of 100000 samples:
 0: 10.055%
 1: 9.95%
 2: 9.933%
 3: 10.02%
 4: 9.996%
 5: 9.964%
 6: 9.912%
 7: 9.933%
 8: 10.142%
 9: 10.095%

truffle = truffle_shuffle(some_list)
Output Analysis: truffle()
Typical Timing: 90 ± 8 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 5
 Maximum: 9
 Mean: 4.606
 Std Deviation: 2.9115702363572207
Distribution of 100000 samples:
 0: 9.977%
 1: 10.037%
 2: 9.974%
 3: 9.99%
 4: 10.031%
 5: 9.991%
 6: 9.997%
 7: 9.976%
 8: 9.951%
 9: 10.076%


Single objects with many distribution possibilities

some_tuple = tuple(i for i in range(10))

monty = QuantumMonty(some_tuple)
Output Analysis: monty()
Typical Timing: 221 ± 7 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 5
 Maximum: 9
 Mean: 4.553
 Std Deviation: 2.7966072323463678
Distribution of 100000 samples:
 0: 10.716%
 1: 8.917%
 2: 9.091%
 3: 9.875%
 4: 11.518%
 5: 11.467%
 6: 9.579%
 7: 9.089%
 8: 8.96%
 9: 10.788%

rand_value = <Fortuna.RandomValue object at 0x100ad87c0>
Output Analysis: rand_value()
Typical Timing: 168 ± 5 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 4
 Maximum: 9
 Mean: 4.449
 Std Deviation: 2.850881710370763
Distribution of 100000 samples:
 0: 9.895%
 1: 9.961%
 2: 10.129%
 3: 9.969%
 4: 9.953%
 5: 10.113%
 6: 9.925%
 7: 10.144%
 8: 9.954%
 9: 9.957%


Weighted Tables:

population = ('A', 'B', 'C', 'D')
cum_weights = (1, 3, 6, 10)
rel_weights = (1, 2, 3, 4)
cum_weighted_table = zip(cum_weights, population)
rel_weighted_table = zip(rel_weights, population)

Cumulative Base Case
Output Analysis: Random.choices(population, cum_weights=cum_weights)
Typical Timing: 553 ± 16 ns
Distribution of 100000 samples:
 A: 10.059%
 B: 19.972%
 C: 30.134%
 D: 39.835%

cum_weighted_choice = CumulativeWeightedChoice(cum_weighted_table)
Output Analysis: cum_weighted_choice()
Typical Timing: 168 ± 3 ns
Distribution of 100000 samples:
 A: 10.104%
 B: 20.138%
 C: 29.646%
 D: 40.112%

Output Analysis: cumulative_weighted_choice(tuple(zip(cum_weights, population)))
Typical Timing: 76 ± 3 ns
Distribution of 100000 samples:
 A: 9.961%
 B: 20.049%
 C: 30.001%
 D: 39.989%

Relative Base Case
Output Analysis: Random.choices(population, weights=rel_weights)
Typical Timing: 697 ± 9 ns
Distribution of 100000 samples:
 A: 10.074%
 B: 19.965%
 C: 29.677%
 D: 40.284%

rel_weighted_choice = RelativeWeightedChoice(rel_weighted_table)
Output Analysis: rel_weighted_choice()
Typical Timing: 169 ± 4 ns
Distribution of 100000 samples:
 A: 9.827%
 B: 20.053%
 C: 30.065%
 D: 40.055%


Random Matrix Values:

some_matrix = {'A': (1, 2, 3, 4), 'B': (10, 20, 30, 40), 'C': (100, 200, 300, 400)}

flex_cat = FlexCat(some_matrix)
Output Analysis: flex_cat()
Typical Timing: 371 ± 17 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 4
 Maximum: 400
 Mean: 40.468
 Std Deviation: 90.31593405343237
Distribution of 100000 samples:
 1: 13.854%
 2: 13.867%
 3: 13.871%
 4: 13.877%
 10: 8.372%
 20: 8.331%
 30: 8.349%
 40: 8.366%
 100: 2.76%
 200: 2.791%
 300: 2.769%
 400: 2.793%

Output Analysis: flex_cat("C")
Typical Timing: 238 ± 8 ns
Statistics of 1000 samples:
 Minimum: 100
 Median: 300
 Maximum: 400
 Mean: 250.4
 Std Deviation: 111.50009987561569
Distribution of 100000 samples:
 100: 25.034%
 200: 24.883%
 300: 24.964%
 400: 25.119%


Random Integers:

Base Case
Output Analysis: Random.randrange(10)
Typical Timing: 158 ± 4 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 4
 Maximum: 9
 Mean: 4.362
 Std Deviation: 2.9071304421039326
Distribution of 100000 samples:
 0: 9.878%
 1: 10.034%
 2: 10.163%
 3: 9.844%
 4: 10.051%
 5: 10.018%
 6: 9.956%
 7: 10.012%
 8: 10.021%
 9: 10.023%

Output Analysis: random_below(10)
Typical Timing: 35 ± 2 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 5
 Maximum: 9
 Mean: 4.575
 Std Deviation: 2.904963651031423
Distribution of 100000 samples:
 0: 10.002%
 1: 10.022%
 2: 9.853%
 3: 10.004%
 4: 9.978%
 5: 10.02%
 6: 9.997%
 7: 10.169%
 8: 9.922%
 9: 10.033%

Output Analysis: random_index(10)
Typical Timing: 35 ± 2 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 5
 Maximum: 9
 Mean: 4.541
 Std Deviation: 2.9378478432263897
Distribution of 100000 samples:
 0: 10.109%
 1: 9.859%
 2: 10.279%
 3: 10.018%
 4: 10.009%
 5: 10.016%
 6: 9.882%
 7: 9.859%
 8: 9.913%
 9: 10.056%

Output Analysis: random_range(10)
Typical Timing: 40 ± 1 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 5
 Maximum: 9
 Mean: 4.565
 Std Deviation: 2.8687985298736134
Distribution of 100000 samples:
 0: 10.233%
 1: 9.998%
 2: 9.998%
 3: 10.149%
 4: 9.957%
 5: 9.946%
 6: 10.007%
 7: 9.779%
 8: 9.96%
 9: 9.973%

Output Analysis: random_below(-10)
Typical Timing: 41 ± 1 ns
Statistics of 1000 samples:
 Minimum: -9
 Median: -5
 Maximum: 0
 Mean: -4.626
 Std Deviation: 2.9248382311982106
Distribution of 100000 samples:
 -9: 9.77%
 -8: 9.985%
 -7: 9.996%
 -6: 9.935%
 -5: 10.142%
 -4: 9.968%
 -3: 10.106%
 -2: 10.163%
 -1: 9.923%
 0: 10.012%

Output Analysis: random_index(-10)
Typical Timing: 43 ± 1 ns
Statistics of 1000 samples:
 Minimum: -10
 Median: -5
 Maximum: -1
 Mean: -5.418
 Std Deviation: 2.85507047678817
Distribution of 100000 samples:
 -10: 9.915%
 -9: 10.063%
 -8: 9.953%
 -7: 9.978%
 -6: 9.916%
 -5: 10.262%
 -4: 9.979%
 -3: 10.06%
 -2: 10.029%
 -1: 9.845%

Output Analysis: random_range(-10)
Typical Timing: 51 ± 1 ns
Statistics of 1000 samples:
 Minimum: -10
 Median: (-6, -5)
 Maximum: -1
 Mean: -5.573
 Std Deviation: 2.928693949228606
Distribution of 100000 samples:
 -10: 9.982%
 -9: 9.965%
 -8: 9.989%
 -7: 10.071%
 -6: 9.999%
 -5: 9.923%
 -4: 10.005%
 -3: 10.188%
 -2: 9.965%
 -1: 9.913%

Base Case
Output Analysis: Random.randrange(1, 10)
Typical Timing: 191 ± 3 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 5
 Maximum: 9
 Mean: 4.885
 Std Deviation: 2.57534607526977
Distribution of 100000 samples:
 1: 11.21%
 2: 11.19%
 3: 11.169%
 4: 10.872%
 5: 11.205%
 6: 10.984%
 7: 10.975%
 8: 11.098%
 9: 11.297%

Output Analysis: random_range(1, 10)
Typical Timing: 44 ± 3 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 5
 Maximum: 9
 Mean: 5.005
 Std Deviation: 2.5949390568390442
Distribution of 100000 samples:
 1: 11.163%
 2: 11.099%
 3: 10.91%
 4: 11.14%
 5: 11.133%
 6: 11.256%
 7: 11.071%
 8: 11.177%
 9: 11.051%

Output Analysis: random_range(10, 1)
Typical Timing: 51 ± 9 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 5
 Maximum: 9
 Mean: 4.883
 Std Deviation: 2.6480791761809774
Distribution of 100000 samples:
 1: 11.093%
 2: 11.252%
 3: 11.17%
 4: 11.007%
 5: 11.137%
 6: 11.303%
 7: 10.979%
 8: 10.891%
 9: 11.168%

Base Case
Output Analysis: Random.randint(-5, 5)
Typical Timing: 215 ± 7 ns
Statistics of 1000 samples:
 Minimum: -5
 Median: 0
 Maximum: 5
 Mean: 0.048
 Std Deviation: 3.222123225154196
Distribution of 100000 samples:
 -5: 9.018%
 -4: 9.109%
 -3: 9.109%
 -2: 9.145%
 -1: 8.996%
 0: 8.973%
 1: 9.015%
 2: 9.191%
 3: 9.1%
 4: 9.149%
 5: 9.195%

Output Analysis: random_int(-5, 5)
Typical Timing: 30 ± 2 ns
Statistics of 1000 samples:
 Minimum: -5
 Median: 0
 Maximum: 5
 Mean: -0.061
 Std Deviation: 3.155191631935251
Distribution of 100000 samples:
 -5: 9.254%
 -4: 8.961%
 -3: 9.162%
 -2: 8.953%
 -1: 9.116%
 0: 9.146%
 1: 9.172%
 2: 8.938%
 3: 9.105%
 4: 9.083%
 5: 9.11%

Base Case
Output Analysis: Random.randrange(1, 20, 2)
Typical Timing: 224 ± 8 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 9
 Maximum: 19
 Mean: 10.034
 Std Deviation: 5.786910430647111
Distribution of 100000 samples:
 1: 10.052%
 3: 9.963%
 5: 9.914%
 7: 9.995%
 9: 9.902%
 11: 9.934%
 13: 10.048%
 15: 10.092%
 17: 10.102%
 19: 9.998%

Output Analysis: random_range(1, 20, 2)
Typical Timing: 41 ± 1 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 11
 Maximum: 19
 Mean: 10.1
 Std Deviation: 5.679282899649766
Distribution of 100000 samples:
 1: 9.907%
 3: 10.122%
 5: 9.922%
 7: 9.969%
 9: 10.234%
 11: 10.06%
 13: 9.977%
 15: 9.901%
 17: 9.849%
 19: 10.059%

Output Analysis: random_range(1, 20, -2)
Typical Timing: 41 ± 2 ns
Statistics of 1000 samples:
 Minimum: 2
 Median: 10
 Maximum: 20
 Mean: 10.778
 Std Deviation: 5.848839622089575
Distribution of 100000 samples:
 2: 9.89%
 4: 10.07%
 6: 9.981%
 8: 9.993%
 10: 9.956%
 12: 10.028%
 14: 10.14%
 16: 10.045%
 18: 9.857%
 20: 10.04%

Output Analysis: random_range(20, 1, -2)
Typical Timing: 46 ± 7 ns
Statistics of 1000 samples:
 Minimum: 2
 Median: (10, 12)
 Maximum: 20
 Mean: 10.986
 Std Deviation: 5.748813169068278
Distribution of 100000 samples:
 2: 9.981%
 4: 9.97%
 6: 9.926%
 8: 9.961%
 10: 10.024%
 12: 10.134%
 14: 9.927%
 16: 10.08%
 18: 10.073%
 20: 9.924%

Output Analysis: d(10)
Typical Timing: 29 ± 2 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 5
 Maximum: 10
 Mean: 5.413
 Std Deviation: 2.901870405764505
Distribution of 100000 samples:
 1: 9.907%
 2: 10.095%
 3: 9.944%
 4: 10.017%
 5: 10.0%
 6: 9.842%
 7: 10.197%
 8: 10.035%
 9: 9.994%
 10: 9.969%

Output Analysis: dice(3, 6)
Typical Timing: 48 ± 1 ns
Statistics of 1000 samples:
 Minimum: 3
 Median: 10
 Maximum: 18
 Mean: 10.426
 Std Deviation: 3.007918145756558
Distribution of 100000 samples:
 3: 0.445%
 4: 1.442%
 5: 2.735%
 6: 4.803%
 7: 6.915%
 8: 9.635%
 9: 11.403%
 10: 12.675%
 11: 12.629%
 12: 11.498%
 13: 9.709%
 14: 6.901%
 15: 4.563%
 16: 2.8%
 17: 1.392%
 18: 0.455%

Output Analysis: ability_dice(4)
Typical Timing: 106 ± 4 ns
Statistics of 1000 samples:
 Minimum: 3
 Median: 12
 Maximum: 18
 Mean: 12.21
 Std Deviation: 2.9014338383492944
Distribution of 100000 samples:
 3: 0.08%
 4: 0.319%
 5: 0.827%
 6: 1.665%
 7: 2.877%
 8: 4.827%
 9: 6.994%
 10: 9.313%
 11: 11.413%
 12: 12.887%
 13: 13.245%
 14: 12.342%
 15: 10.094%
 16: 7.399%
 17: 4.153%
 18: 1.565%

Output Analysis: plus_or_minus(5)
Typical Timing: 28 ± 1 ns
Statistics of 1000 samples:
 Minimum: -5
 Median: 0
 Maximum: 5
 Mean: -0.001
 Std Deviation: 3.1810561325003555
Distribution of 100000 samples:
 -5: 8.976%
 -4: 8.973%
 -3: 9.133%
 -2: 9.075%
 -1: 9.034%
 0: 9.161%
 1: 9.139%
 2: 9.112%
 3: 9.04%
 4: 9.172%
 5: 9.185%

Output Analysis: plus_or_minus_linear(5)
Typical Timing: 36 ± 1 ns
Statistics of 1000 samples:
 Minimum: -5
 Median: 0
 Maximum: 5
 Mean: 0.016
 Std Deviation: 2.4367358662115355
Distribution of 100000 samples:
 -5: 2.851%
 -4: 5.654%
 -3: 8.284%
 -2: 11.117%
 -1: 13.908%
 0: 16.669%
 1: 13.744%
 2: 11.298%
 3: 8.334%
 4: 5.367%
 5: 2.774%

Output Analysis: plus_or_minus_gauss(5)
Typical Timing: 46 ± 1 ns
Statistics of 1000 samples:
 Minimum: -4
 Median: 0
 Maximum: 5
 Mean: -0.031
 Std Deviation: 1.6138908400643595
Distribution of 100000 samples:
 -5: 0.197%
 -4: 1.181%
 -3: 4.466%
 -2: 11.411%
 -1: 20.302%
 0: 24.685%
 1: 20.453%
 2: 11.494%
 3: 4.388%
 4: 1.206%
 5: 0.217%


Random Floats:

Base Case
Output Analysis: Random.random()
Typical Timing: 20 ± 1 ns
Statistics of 1000 samples:
 Minimum: 0.0024967235946034005
 Median: (0.5022009271968713, 0.5023940805169211)
 Maximum: 0.9992728319511441
 Mean: 0.5054544074117795
 Std Deviation: 0.292310987289518
round distribution of 100000:
 0: 49.831%
 1: 50.169%

Output Analysis: canonical()
Typical Timing: 21 ± 1 ns
Statistics of 1000 samples:
 Minimum: 0.00023518635736289353
 Median: (0.4810660341754359, 0.4824691452966555)
 Maximum: 0.99976358610798
 Mean: 0.4949628458738559
 Std Deviation: 0.29007541697181755
round distribution of 100000:
 0: 50.003%
 1: 49.997%

Base Case
Output Analysis: Random.uniform(0.0, 10.0)
Typical Timing: 67 ± 1 ns
Statistics of 1000 samples:
 Minimum: 0.03124349629037293
 Median: (4.869843991605648, 4.879452953993772)
 Maximum: 9.991204910138983
 Mean: 4.922665195894069
 Std Deviation: 2.792393604661177
floor distribution of 100000:
 0: 10.099%
 1: 9.948%
 2: 10.19%
 3: 10.043%
 4: 9.862%
 5: 10.032%
 6: 9.894%
 7: 10.089%
 8: 10.005%
 9: 9.838%

Output Analysis: random_float(0.0, 10.0)
Typical Timing: 23 ± 1 ns
Statistics of 1000 samples:
 Minimum: 0.0021607846477844617
 Median: (5.165998805251534, 5.166234250243706)
 Maximum: 9.980361774247179
 Mean: 5.053615660809863
 Std Deviation: 2.857464526866407
floor distribution of 100000:
 0: 9.965%
 1: 10.074%
 2: 10.031%
 3: 9.961%
 4: 9.836%
 5: 10.013%
 6: 10.071%
 7: 10.04%
 8: 10.033%
 9: 9.976%

Base Case
Output Analysis: Random.triangular(0.0, 10.0, 5.0)
Typical Timing: 135 ± 3 ns
Statistics of 1000 samples:
 Minimum: 0.34667286360505006
 Median: (5.005118651988952, 5.012553151817545)
 Maximum: 9.795369886997287
 Mean: 4.966539645151894
 Std Deviation: 2.080261213261674
round distribution of 100000:
 0: 0.524%
 1: 4.007%
 2: 8.199%
 3: 12.105%
 4: 15.977%
 5: 18.989%
 6: 15.827%
 7: 11.999%
 8: 7.986%
 9: 3.901%
 10: 0.486%

Output Analysis: triangular(0.0, 10.0, 5.0)
Typical Timing: 32 ± 2 ns
Statistics of 1000 samples:
 Minimum: 0.1737509575769492
 Median: (4.967785057458952, 4.971211592684284)
 Maximum: 9.66343916069151
 Mean: 4.971482884722586
 Std Deviation: 2.0299847497955428
round distribution of 100000:
 0: 0.5%
 1: 3.979%
 2: 7.934%
 3: 11.932%
 4: 16.024%
 5: 19.104%
 6: 16.048%
 7: 12.008%
 8: 7.973%
 9: 4.023%
 10: 0.475%

Output Analysis: beta_variate(1.0, 1.0)
Typical Timing: 44 ± 2 ns
Statistics of 1000 samples:
 Minimum: 6.110198629053744e-05
 Median: (0.5028008682894913, 0.5035969740559323)
 Maximum: 0.9994713791804665
 Mean: 0.49738555982750493
 Std Deviation: 0.290511581884979
round distribution of 100000:
 0: 49.764%
 1: 50.236%

Output Analysis: pareto_variate(1.0)
Typical Timing: 35 ± 2 ns
Statistics of 1000 samples:
 Minimum: 1.0000886844802732
 Median: (1.9802436146432247, 1.9844650863313313)
 Maximum: 2241.614223328484
 Mean: 9.215397444614728
 Std Deviation: 81.03992447018125
round distribution of 100000:
 1: 33.401%
 2: 26.824%
 3: 11.35%
 4: 6.45%
 5: 3.896%
 6: 2.77%
 7: 2.058%
 8: 1.457%
 9: 1.21%
 10: 1.025%
 11: 0.84%
 12: 0.709%
 13: 0.604%
 14: 0.496%
 15: 0.475%
 16: 0.404%
 17: 0.358%
 18: 0.322%
 19: 0.294%
 20: 0.266%
 21: 0.205%
 22: 0.214%
 23: 0.189%
 24: 0.151%
 25: 0.167%
 26: 0.159%
 27: 0.128%
 28: 0.136%
 29: 0.116%
 30: 0.12%
 31: 0.119%
 32: 0.089%
 33: 0.077%
 34: 0.075%
 35: 0.077%
 36: 0.068%
 37: 0.073%
 38: 0.058%
 39: 0.049%
 40: 0.054%
 41: 0.057%
 42: 0.062%
 43: 0.062%
 44: 0.051%
 45: 0.045%
 46: 0.054%
 47: 0.046%
 48: 0.051%
 49: 0.048%
 50: 0.041%
 51: 0.04%
 52: 0.033%
 53: 0.032%
 54: 0.033%
 55: 0.026%
 56: 0.035%
 57: 0.029%
 58: 0.024%
 59: 0.03%
 60: 0.027%
 61: 0.034%
 62: 0.033%
 63: 0.028%
 64: 0.021%
 65: 0.016%
 66: 0.019%
 67: 0.029%
 68: 0.019%
 69: 0.026%
 70: 0.023%
 71: 0.017%
 72: 0.018%
 73: 0.023%
 74: 0.01%
 75: 0.02%
 76: 0.017%
 77: 0.016%
 78: 0.014%
 79: 0.013%
 80: 0.01%
 81: 0.013%
 82: 0.012%
 83: 0.016%
 84: 0.015%
 85: 0.019%
 86: 0.011%
 87: 0.013%
 88: 0.016%
 89: 0.014%
 90: 0.011%
 91: 0.01%
 92: 0.01%
 93: 0.015%
 94: 0.009%
 95: 0.011%
 96: 0.013%
 97: 0.009%
 98: 0.01%
 99: 0.01%
 100: 0.008%
 101: 0.012%
 102: 0.006%
 103: 0.005%
 104: 0.012%
 105: 0.006%
 106: 0.01%
 107: 0.006%
 108: 0.006%
 109: 0.007%
 110: 0.005%
 111: 0.012%
 112: 0.009%
 113: 0.006%
 114: 0.005%
 115: 0.009%
 116: 0.008%
 117: 0.007%
 118: 0.009%
 119: 0.006%
 120: 0.007%
 121: 0.007%
 122: 0.006%
 123: 0.008%
 124: 0.004%
 125: 0.009%
 126: 0.004%
 127: 0.012%
 128: 0.006%
 129: 0.007%
 130: 0.009%
 131: 0.003%
 132: 0.008%
 133: 0.008%
 134: 0.002%
 135: 0.002%
 136: 0.006%
 137: 0.005%
 138: 0.004%
 139: 0.003%
 140: 0.005%
 141: 0.005%
 142: 0.003%
 143: 0.012%
 144: 0.002%
 145: 0.007%
 146: 0.004%
 147: 0.007%
 148: 0.008%
 150: 0.004%
 151: 0.011%
 152: 0.004%
 153: 0.004%
 154: 0.005%
 155: 0.004%
 156: 0.005%
 157: 0.002%
 158: 0.002%
 159: 0.002%
 160: 0.004%
 161: 0.004%
 162: 0.002%
 163: 0.004%
 164: 0.003%
 165: 0.005%
 166: 0.004%
 167: 0.006%
 168: 0.003%
 169: 0.002%
 170: 0.004%
 171: 0.004%
 172: 0.005%
 173: 0.002%
 174: 0.005%
 175: 0.005%
 176: 0.001%
 177: 0.003%
 178: 0.004%
 179: 0.004%
 180: 0.002%
 181: 0.003%
 182: 0.003%
 183: 0.007%
 184: 0.004%
 185: 0.004%
 186: 0.001%
 187: 0.005%
 188: 0.003%
 189: 0.003%
 190: 0.004%
 191: 0.001%
 192: 0.001%
 193: 0.003%
 194: 0.001%
 196: 0.004%
 197: 0.004%
 198: 0.003%
 199: 0.001%
 200: 0.002%
 202: 0.003%
 203: 0.002%
 204: 0.003%
 205: 0.006%
 206: 0.002%
 207: 0.001%
 209: 0.002%
 210: 0.003%
 211: 0.003%
 212: 0.001%
 213: 0.002%
 214: 0.006%
 215: 0.002%
 216: 0.001%
 217: 0.003%
 218: 0.001%
 219: 0.004%
 220: 0.002%
 221: 0.001%
 222: 0.003%
 223: 0.001%
 224: 0.001%
 225: 0.003%
 226: 0.004%
 227: 0.002%
 228: 0.004%
 230: 0.001%
 231: 0.001%
 232: 0.001%
 233: 0.003%
 234: 0.006%
 235: 0.002%
 236: 0.004%
 237: 0.002%
 238: 0.001%
 239: 0.001%
 240: 0.002%
 241: 0.001%
 244: 0.004%
 245: 0.001%
 246: 0.001%
 248: 0.004%
 250: 0.002%
 251: 0.002%
 252: 0.004%
 253: 0.001%
 254: 0.002%
 255: 0.001%
 257: 0.005%
 258: 0.001%
 260: 0.003%
 261: 0.001%
 262: 0.002%
 263: 0.002%
 264: 0.001%
 265: 0.002%
 267: 0.001%
 268: 0.001%
 270: 0.001%
 271: 0.002%
 272: 0.002%
 273: 0.002%
 275: 0.002%
 276: 0.001%
 278: 0.001%
 279: 0.001%
 280: 0.003%
 281: 0.002%
 282: 0.001%
 283: 0.005%
 284: 0.002%
 289: 0.003%
 291: 0.002%
 292: 0.001%
 296: 0.002%
 297: 0.002%
 298: 0.002%
 300: 0.001%
 302: 0.002%
 303: 0.001%
 304: 0.001%
 305: 0.003%
 306: 0.002%
 307: 0.001%
 308: 0.001%
 309: 0.001%
 312: 0.001%
 313: 0.003%
 314: 0.001%
 317: 0.001%
 318: 0.002%
 319: 0.002%
 323: 0.002%
 324: 0.003%
 330: 0.001%
 331: 0.001%
 333: 0.001%
 334: 0.001%
 335: 0.002%
 337: 0.001%
 338: 0.001%
 339: 0.001%
 340: 0.003%
 341: 0.001%
 342: 0.002%
 343: 0.001%
 345: 0.001%
 347: 0.001%
 350: 0.001%
 352: 0.001%
 353: 0.001%
 355: 0.001%
 357: 0.004%
 361: 0.002%
 362: 0.002%
 364: 0.001%
 366: 0.002%
 367: 0.001%
 368: 0.001%
 369: 0.001%
 372: 0.001%
 374: 0.001%
 376: 0.001%
 378: 0.001%
 379: 0.001%
 382: 0.001%
 383: 0.001%
 384: 0.002%
 385: 0.001%
 389: 0.001%
 390: 0.001%
 391: 0.001%
 392: 0.001%
 394: 0.001%
 396: 0.001%
 402: 0.002%
 403: 0.001%
 407: 0.001%
 409: 0.002%
 412: 0.001%
 413: 0.001%
 414: 0.001%
 417: 0.001%
 423: 0.001%
 424: 0.001%
 426: 0.002%
 429: 0.001%
 430: 0.002%
 432: 0.002%
 434: 0.001%
 436: 0.001%
 437: 0.001%
 438: 0.001%
 443: 0.002%
 444: 0.001%
 448: 0.001%
 449: 0.001%
 452: 0.001%
 461: 0.001%
 463: 0.002%
 466: 0.001%
 468: 0.001%
 470: 0.001%
 472: 0.001%
 478: 0.002%
 481: 0.001%
 485: 0.001%
 486: 0.001%
 488: 0.001%
 492: 0.002%
 493: 0.001%
 494: 0.001%
 505: 0.001%
 506: 0.002%
 507: 0.001%
 510: 0.001%
 512: 0.001%
 514: 0.001%
 517: 0.001%
 522: 0.002%
 524: 0.001%
 525: 0.001%
 531: 0.001%
 532: 0.001%
 535: 0.001%
 538: 0.001%
 552: 0.001%
 553: 0.001%
 557: 0.001%
 558: 0.001%
 561: 0.001%
 564: 0.001%
 565: 0.001%
 574: 0.001%
 579: 0.001%
 584: 0.001%
 587: 0.001%
 590: 0.001%
 605: 0.001%
 609: 0.001%
 617: 0.001%
 619: 0.002%
 620: 0.001%
 625: 0.001%
 631: 0.001%
 632: 0.001%
 634: 0.001%
 635: 0.001%
 639: 0.001%
 640: 0.002%
 643: 0.001%
 651: 0.001%
 663: 0.001%
 664: 0.001%
 666: 0.003%
 678: 0.001%
 681: 0.001%
 683: 0.001%
 696: 0.001%
 703: 0.001%
 705: 0.001%
 706: 0.001%
 713: 0.001%
 714: 0.001%
 715: 0.001%
 716: 0.002%
 720: 0.001%
 722: 0.001%
 723: 0.002%
 724: 0.001%
 732: 0.001%
 737: 0.002%
 739: 0.001%
 742: 0.001%
 744: 0.001%
 746: 0.001%
 755: 0.001%
 765: 0.001%
 769: 0.001%
 781: 0.001%
 790: 0.001%
 793: 0.001%
 803: 0.001%
 817: 0.001%
 823: 0.001%
 827: 0.001%
 828: 0.001%
 835: 0.001%
 837: 0.001%
 845: 0.001%
 846: 0.001%
 849: 0.001%
 856: 0.001%
 857: 0.001%
 871: 0.001%
 883: 0.001%
 897: 0.001%
 899: 0.001%
 916: 0.001%
 929: 0.001%
 940: 0.001%
 955: 0.001%
 962: 0.001%
 971: 0.001%
 983: 0.001%
 987: 0.002%
 995: 0.001%
 1008: 0.001%
 1029: 0.001%
 1035: 0.001%
 1051: 0.001%
 1069: 0.001%
 1080: 0.001%
 1083: 0.001%
 1121: 0.002%
 1142: 0.001%
 1150: 0.001%
 1158: 0.001%
 1170: 0.001%
 1193: 0.001%
 1199: 0.001%
 1217: 0.002%
 1218: 0.001%
 1227: 0.001%
 1232: 0.001%
 1234: 0.001%
 1246: 0.001%
 1247: 0.001%
 1272: 0.001%
 1281: 0.001%
 1302: 0.001%
 1307: 0.001%
 1342: 0.001%
 1373: 0.001%
 1381: 0.001%
 1400: 0.001%
 1410: 0.001%
 1413: 0.002%
 1497: 0.001%
 1501: 0.001%
 1608: 0.001%
 1611: 0.002%
 1667: 0.001%
 1692: 0.001%
 1724: 0.001%
 1725: 0.001%
 1742: 0.001%
 1769: 0.001%
 1805: 0.001%
 1809: 0.001%
 1848: 0.001%
 1867: 0.001%
 1877: 0.001%
 1881: 0.001%
 1899: 0.001%
 1920: 0.001%
 2031: 0.001%
 2166: 0.001%
 2213: 0.001%
 2242: 0.001%
 2255: 0.001%
 2327: 0.001%
 2381: 0.001%
 2457: 0.001%
 2486: 0.001%
 2505: 0.001%
 2690: 0.001%
 2905: 0.001%
 2996: 0.001%
 3675: 0.001%
 4115: 0.001%
 4212: 0.001%
 4301: 0.001%
 4652: 0.001%
 4917: 0.001%
 5272: 0.001%
 5558: 0.001%
 6173: 0.001%
 6254: 0.001%
 6584: 0.001%
 7976: 0.001%
 8932: 0.001%
 10088: 0.001%
 10308: 0.001%
 11868: 0.001%
 12683: 0.001%
 17052: 0.001%
 20835: 0.001%
 22528: 0.001%
 24069: 0.001%
 24847: 0.001%
 27187: 0.001%
 32199: 0.001%
 34953: 0.001%
 59885: 0.001%
 104101: 0.001%
 146598: 0.001%
 495853: 0.001%

Base Case
Output Analysis: Random.vonmisesvariate(0.0, 1.0)
Typical Timing: 344 ± 6 ns
Statistics of 1000 samples:
 Minimum: 0.0006999430758640235
 Median: (2.842504937793423, 2.863654486197534)
 Maximum: 6.278910536115165
 Mean: 3.1020146681552703
 Std Deviation: 2.2619871112052694
round distribution of 100000:
 0: 16.513%
 1: 21.666%
 2: 8.775%
 3: 4.81%
 4: 6.933%
 5: 17.176%
 6: 24.127%

Output Analysis: vonmises_variate(0.0, 1.0)
Typical Timing: 80 ± 2 ns
Statistics of 1000 samples:
 Minimum: -3.1388232377408953
 Median: (-0.02716647373829684, -0.021459933485825904)
 Maximum: 3.1103670754825625
 Mean: 0.028990601827155286
 Std Deviation: 1.252632267847967
round distribution of 100000:
 -3: 3.164%
 -2: 8.647%
 -1: 21.896%
 0: 32.608%
 1: 21.835%
 2: 8.696%
 3: 3.154%

Output Analysis: bernoulli_variate(0.5)
Typical Timing: 23 ± 3 ns
Statistics of 1000 samples:
 Minimum: False
 Median: True
 Maximum: True
 Mean: 0.512
 Std Deviation: 0.5001060948499889
round distribution of 100000:
 0: 49.944%
 1: 50.056%

Output Analysis: binomial_variate(3, 0.5)
Typical Timing: 84 ± 2 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 1
 Maximum: 3
 Mean: 1.513
 Std Deviation: 0.854728940402489
round distribution of 100000:
 0: 12.599%
 1: 37.456%
 2: 37.334%
 3: 12.611%

Output Analysis: negative_binomial_variate(3, 0.5)
Typical Timing: 55 ± 1 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 3
 Maximum: 16
 Mean: 3.058
 Std Deviation: 2.583662383383578
round distribution of 100000:
 0: 12.434%
 1: 18.619%
 2: 19.013%
 3: 15.616%
 4: 11.782%
 5: 8.061%
 6: 5.496%
 7: 3.448%
 8: 2.207%
 9: 1.305%
 10: 0.841%
 11: 0.465%
 12: 0.302%
 13: 0.168%
 14: 0.104%
 15: 0.061%
 16: 0.037%
 17: 0.013%
 18: 0.012%
 19: 0.008%
 20: 0.005%
 22: 0.001%
 23: 0.001%
 24: 0.001%

Output Analysis: geometric_variate(0.5)
Typical Timing: 36 ± 1 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 1
 Maximum: 9
 Mean: 0.982
 Std Deviation: 1.3746146971299142
round distribution of 100000:
 0: 49.959%
 1: 25.065%
 2: 12.46%
 3: 6.31%
 4: 3.018%
 5: 1.638%
 6: 0.797%
 7: 0.372%
 8: 0.195%
 9: 0.094%
 10: 0.05%
 11: 0.023%
 12: 0.007%
 13: 0.008%
 14: 0.004%

Output Analysis: poisson_variate(0.5)
Typical Timing: 39 ± 2 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 0
 Maximum: 4
 Mean: 0.503
 Std Deviation: 0.7017716747514704
round distribution of 100000:
 0: 60.669%
 1: 30.399%
 2: 7.538%
 3: 1.232%
 4: 0.149%
 5: 0.012%
 6: 0.001%

Base Case
Output Analysis: Random.expovariate(2.0)
Typical Timing: 107 ± 2 ns
Statistics of 1000 samples:
 Minimum: 0.0002645269141955085
 Median: (0.33197586503519494, 0.3331882113766054)
 Maximum: 2.9108880336721787
 Mean: 0.47512778066740935
 Std Deviation: 0.4745089693871472
round distribution of 100000:
 0: 62.969%
 1: 31.887%
 2: 4.418%
 3: 0.633%
 4: 0.078%
 5: 0.014%
 6: 0.001%

Output Analysis: exponential_variate(2.0)
Typical Timing: 28 ± 1 ns
Statistics of 1000 samples:
 Minimum: 0.00022502870880941313
 Median: (0.3656490870024802, 0.36626470846646686)
 Maximum: 3.7418919899069825
 Mean: 0.5003498447170944
 Std Deviation: 0.48352038756063526
round distribution of 100000:
 0: 63.263%
 1: 31.815%
 2: 4.245%
 3: 0.584%
 4: 0.076%
 5: 0.014%
 6: 0.003%

Base Case
Output Analysis: Random.gammavariate(1.0, 1.0)
Typical Timing: 157 ± 3 ns
Statistics of 1000 samples:
 Minimum: 0.0006477763097548772
 Median: (0.6235487488411592, 0.6253194169274288)
 Maximum: 7.88466060763495
 Mean: 0.972151161286103
 Std Deviation: 0.9713694023470834
round distribution of 100000:
 0: 39.389%
 1: 38.179%
 2: 14.158%
 3: 5.222%
 4: 1.93%
 5: 0.709%
 6: 0.263%
 7: 0.099%
 8: 0.032%
 9: 0.011%
 10: 0.006%
 12: 0.002%

Output Analysis: gamma_variate(1.0, 1.0)
Typical Timing: 31 ± 2 ns
Statistics of 1000 samples:
 Minimum: 0.0003966154520776516
 Median: (0.6669213158522161, 0.6681547951505862)
 Maximum: 7.385331510142255
 Mean: 0.9563253323134594
 Std Deviation: 0.9515550138441319
round distribution of 100000:
 0: 39.573%
 1: 38.215%
 2: 14.051%
 3: 5.137%
 4: 1.882%
 5: 0.74%
 6: 0.251%
 7: 0.094%
 8: 0.039%
 9: 0.013%
 10: 0.003%
 11: 0.001%
 12: 0.001%

Base Case
Output Analysis: Random.weibullvariate(1.0, 1.0)
Typical Timing: 143 ± 3 ns
Statistics of 1000 samples:
 Minimum: 0.0007270605581450485
 Median: (0.6855213781270427, 0.6867364925924392)
 Maximum: 7.795115564942976
 Mean: 1.0204145439020273
 Std Deviation: 1.0348219512469918
round distribution of 100000:
 0: 39.454%
 1: 38.398%
 2: 14.006%
 3: 5.289%
 4: 1.811%
 5: 0.672%
 6: 0.211%
 7: 0.105%
 8: 0.037%
 9: 0.009%
 10: 0.006%
 11: 0.002%

Output Analysis: weibull_variate(1.0, 1.0)
Typical Timing: 49 ± 2 ns
Statistics of 1000 samples:
 Minimum: 0.0011563316455022133
 Median: (0.7109925277405156, 0.7118443829297991)
 Maximum: 6.978473950093454
 Mean: 0.9939410136582606
 Std Deviation: 1.0036749307038422
round distribution of 100000:
 0: 39.458%
 1: 38.279%
 2: 14.079%
 3: 5.226%
 4: 1.916%
 5: 0.663%
 6: 0.238%
 7: 0.093%
 8: 0.025%
 9: 0.013%
 10: 0.003%
 11: 0.006%
 12: 0.001%

Base Case
Output Analysis: Random.normalvariate(0.0, 1.0)
Typical Timing: 243 ± 6 ns
Statistics of 1000 samples:
 Minimum: -3.6644902110441593
 Median: (-0.021447664348523132, -0.02144185125449127)
 Maximum: 2.9583240621954463
 Mean: -0.0001013066563716923
 Std Deviation: 0.9782049414205509
round distribution of 100000:
 -5: 0.001%
 -4: 0.024%
 -3: 0.575%
 -2: 5.984%
 -1: 24.127%
 0: 38.24%
 1: 24.322%
 2: 6.125%
 3: 0.577%
 4: 0.025%

Output Analysis: normal_variate(0.0, 1.0)
Typical Timing: 42 ± 2 ns
Statistics of 1000 samples:
 Minimum: -3.617369498502793
 Median: (0.008058319699125882, 0.010756245745365765)
 Maximum: 3.513829560747222
 Mean: 0.04184375076945356
 Std Deviation: 0.9989496440127368
round distribution of 100000:
 -4: 0.027%
 -3: 0.579%
 -2: 6.116%
 -1: 24.223%
 0: 38.254%
 1: 24.01%
 2: 6.148%
 3: 0.624%
 4: 0.019%

Base Case
Output Analysis: Random.lognormvariate(0.0, 1.0)
Typical Timing: 300 ± 9 ns
Statistics of 1000 samples:
 Minimum: 0.056621816205159575
 Median: (1.0381663676662773, 1.038545920727633)
 Maximum: 25.382535809370342
 Mean: 1.7867416357441026
 Std Deviation: 2.332224081863103
round distribution of 100000:
 0: 24.155%
 1: 41.357%
 2: 16.452%
 3: 7.531%
 4: 3.851%
 5: 2.226%
 6: 1.329%
 7: 0.881%
 8: 0.593%
 9: 0.416%
 10: 0.266%
 11: 0.203%
 12: 0.155%
 13: 0.107%
 14: 0.077%
 15: 0.065%
 16: 0.048%
 17: 0.051%
 18: 0.038%
 19: 0.025%
 20: 0.022%
 21: 0.021%
 22: 0.018%
 23: 0.016%
 24: 0.01%
 25: 0.011%
 26: 0.014%
 27: 0.011%
 28: 0.002%
 29: 0.003%
 30: 0.004%
 31: 0.003%
 32: 0.001%
 33: 0.006%
 34: 0.002%
 35: 0.001%
 36: 0.002%
 37: 0.002%
 38: 0.002%
 39: 0.001%
 40: 0.002%
 41: 0.001%
 42: 0.002%
 43: 0.001%
 45: 0.003%
 46: 0.001%
 47: 0.001%
 48: 0.003%
 50: 0.001%
 51: 0.001%
 53: 0.001%
 57: 0.001%
 60: 0.001%
 61: 0.001%
 70: 0.001%
 136: 0.001%

Output Analysis: log_normal_variate(0.0, 1.0)
Typical Timing: 65 ± 3 ns
Statistics of 1000 samples:
 Minimum: 0.04477606257096241
 Median: (0.9876580917327729, 0.9891818846913288)
 Maximum: 21.483788903119503
 Mean: 1.5851044786197972
 Std Deviation: 1.9505579181844885
round distribution of 100000:
 0: 24.464%
 1: 41.351%
 2: 16.296%
 3: 7.376%
 4: 3.861%
 5: 2.262%
 6: 1.301%
 7: 0.862%
 8: 0.556%
 9: 0.424%
 10: 0.303%
 11: 0.214%
 12: 0.137%
 13: 0.12%
 14: 0.103%
 15: 0.075%
 16: 0.051%
 17: 0.05%
 18: 0.023%
 19: 0.032%
 20: 0.017%
 21: 0.017%
 22: 0.016%
 23: 0.009%
 24: 0.009%
 25: 0.008%
 26: 0.009%
 27: 0.007%
 28: 0.003%
 29: 0.006%
 30: 0.006%
 31: 0.003%
 32: 0.005%
 33: 0.001%
 34: 0.004%
 35: 0.004%
 36: 0.001%
 37: 0.001%
 38: 0.001%
 39: 0.001%
 40: 0.001%
 41: 0.002%
 43: 0.001%
 46: 0.003%
 55: 0.001%
 65: 0.001%
 73: 0.001%
 104: 0.001%

Output Analysis: extreme_value_variate(0.0, 2.0)
Typical Timing: 42 ± 3 ns
Statistics of 1000 samples:
 Minimum: -3.667030775371436
 Median: (0.685895478863013, 0.7084904759077995)
 Maximum: 11.866534382070324
 Mean: 1.0388660670136125
 Std Deviation: 2.428964940441852
round distribution of 100000:
 -5: 0.009%
 -4: 0.335%
 -3: 2.763%
 -2: 9.037%
 -1: 15.586%
 0: 18.268%
 1: 16.457%
 2: 12.682%
 3: 9.011%
 4: 5.922%
 5: 3.755%
 6: 2.388%
 7: 1.472%
 8: 0.943%
 9: 0.525%
 10: 0.338%
 11: 0.207%
 12: 0.126%
 13: 0.058%
 14: 0.048%
 15: 0.018%
 16: 0.022%
 17: 0.007%
 18: 0.008%
 19: 0.006%
 20: 0.001%
 21: 0.003%
 22: 0.001%
 23: 0.001%
 24: 0.002%
 26: 0.001%

Output Analysis: chi_squared_variate(5.0)
Typical Timing: 65 ± 3 ns
Statistics of 1000 samples:
 Minimum: 0.22780729205520434
 Median: (4.207914823841418, 4.210056404247643)
 Maximum: 22.74007531235598
 Mean: 4.89562998552275
 Std Deviation: 3.1738100027490326
round distribution of 100000:
 0: 0.854%
 1: 7.964%
 2: 13.451%
 3: 15.438%
 4: 14.222%
 5: 12.196%
 6: 9.73%
 7: 7.427%
 8: 5.676%
 9: 4.069%
 10: 2.805%
 11: 1.949%
 12: 1.416%
 13: 0.931%
 14: 0.619%
 15: 0.418%
 16: 0.313%
 17: 0.176%
 18: 0.12%
 19: 0.064%
 20: 0.062%
 21: 0.038%
 22: 0.022%
 23: 0.017%
 24: 0.012%
 25: 0.005%
 26: 0.003%
 27: 0.002%
 28: 0.001%

Output Analysis: cauchy_variate(0.0, 2.0)
Typical Timing: 33 ± 3 ns
Statistics of 1000 samples:
 Minimum: -1958.377577487674
 Median: (-0.1491365712219053, -0.14825496063331284)
 Maximum: 11149.019893616087
 Mean: 10.409352700604638
 Std Deviation: 364.2031647352339
round distribution of 100000:
 -403377: 0.001%
 -57979: 0.001%
 -48950: 0.001%
 -23182: 0.001%
 -10561: 0.001%
 -10119: 0.001%
 -9572: 0.001%
 -8789: 0.001%
 -8319: 0.001%
 -5457: 0.001%
 -5212: 0.001%
 -4799: 0.001%
 -4432: 0.001%
 -4218: 0.001%
 -3869: 0.001%
 -3860: 0.001%
 -3757: 0.001%
 -3455: 0.001%
 -3277: 0.001%
 -3084: 0.001%
 -2779: 0.001%
 -2722: 0.001%
 -2224: 0.001%
 -2211: 0.001%
 -2095: 0.001%
 -2088: 0.001%
 -2063: 0.001%
 -1958: 0.001%
 -1914: 0.001%
 -1866: 0.001%
 -1816: 0.001%
 -1800: 0.001%
 -1766: 0.001%
 -1662: 0.001%
 -1656: 0.001%
 -1630: 0.001%
 -1541: 0.001%
 -1520: 0.001%
 -1479: 0.001%
 -1473: 0.001%
 -1469: 0.001%
 -1445: 0.001%
 -1440: 0.001%
 -1436: 0.001%
 -1398: 0.001%
 -1367: 0.001%
 -1316: 0.001%
 -1250: 0.001%
 -1236: 0.001%
 -1208: 0.001%
 -1189: 0.001%
 -1184: 0.001%
 -1169: 0.001%
 -1147: 0.001%
 -1124: 0.001%
 -1122: 0.001%
 -1088: 0.001%
 -1060: 0.002%
 -1059: 0.001%
 -1041: 0.001%
 -1006: 0.001%
 -1001: 0.001%
 -946: 0.001%
 -938: 0.001%
 -937: 0.001%
 -900: 0.001%
 -898: 0.001%
 -892: 0.001%
 -887: 0.001%
 -883: 0.001%
 -877: 0.001%
 -858: 0.001%
 -840: 0.001%
 -834: 0.001%
 -812: 0.001%
 -811: 0.001%
 -791: 0.001%
 -779: 0.001%
 -774: 0.001%
 -756: 0.002%
 -751: 0.001%
 -747: 0.001%
 -730: 0.001%
 -700: 0.001%
 -694: 0.001%
 -686: 0.001%
 -684: 0.001%
 -680: 0.001%
 -678: 0.001%
 -675: 0.001%
 -673: 0.001%
 -672: 0.001%
 -656: 0.001%
 -649: 0.001%
 -646: 0.001%
 -628: 0.001%
 -620: 0.001%
 -618: 0.001%
 -611: 0.001%
 -605: 0.001%
 -586: 0.001%
 -585: 0.001%
 -584: 0.002%
 -581: 0.001%
 -580: 0.001%
 -561: 0.001%
 -557: 0.001%
 -552: 0.002%
 -550: 0.001%
 -543: 0.001%
 -530: 0.001%
 -528: 0.001%
 -517: 0.001%
 -514: 0.001%
 -512: 0.001%
 -508: 0.001%
 -505: 0.001%
 -504: 0.001%
 -499: 0.001%
 -492: 0.002%
 -486: 0.001%
 -484: 0.001%
 -482: 0.001%
 -476: 0.001%
 -467: 0.001%
 -466: 0.001%
 -463: 0.001%
 -461: 0.001%
 -456: 0.001%
 -454: 0.002%
 -442: 0.002%
 -440: 0.001%
 -438: 0.001%
 -435: 0.002%
 -434: 0.001%
 -427: 0.002%
 -426: 0.001%
 -425: 0.002%
 -424: 0.001%
 -423: 0.001%
 -421: 0.001%
 -412: 0.001%
 -406: 0.001%
 -402: 0.001%
 -400: 0.001%
 -387: 0.001%
 -384: 0.001%
 -381: 0.001%
 -379: 0.001%
 -375: 0.001%
 -374: 0.002%
 -372: 0.001%
 -370: 0.002%
 -368: 0.001%
 -363: 0.002%
 -360: 0.003%
 -357: 0.001%
 -354: 0.002%
 -348: 0.001%
 -344: 0.001%
 -343: 0.001%
 -339: 0.001%
 -338: 0.001%
 -337: 0.001%
 -334: 0.001%
 -333: 0.001%
 -331: 0.001%
 -326: 0.002%
 -322: 0.001%
 -320: 0.003%
 -319: 0.001%
 -317: 0.001%
 -314: 0.001%
 -313: 0.002%
 -311: 0.001%
 -309: 0.003%
 -305: 0.001%
 -302: 0.001%
 -296: 0.001%
 -295: 0.001%
 -294: 0.001%
 -293: 0.001%
 -290: 0.001%
 -288: 0.001%
 -283: 0.001%
 -281: 0.001%
 -277: 0.001%
 -276: 0.001%
 -275: 0.001%
 -273: 0.002%
 -272: 0.001%
 -270: 0.003%
 -267: 0.001%
 -266: 0.001%
 -264: 0.001%
 -262: 0.001%
 -261: 0.003%
 -257: 0.002%
 -255: 0.003%
 -254: 0.001%
 -253: 0.001%
 -251: 0.002%
 -249: 0.001%
 -247: 0.002%
 -246: 0.002%
 -244: 0.001%
 -243: 0.004%
 -242: 0.001%
 -240: 0.001%
 -239: 0.002%
 -238: 0.001%
 -237: 0.001%
 -235: 0.002%
 -234: 0.001%
 -233: 0.001%
 -232: 0.001%
 -231: 0.001%
 -230: 0.001%
 -229: 0.002%
 -228: 0.002%
 -224: 0.002%
 -223: 0.002%
 -222: 0.002%
 -221: 0.002%
 -218: 0.002%
 -217: 0.001%
 -216: 0.003%
 -215: 0.001%
 -214: 0.001%
 -213: 0.001%
 -212: 0.001%
 -211: 0.001%
 -210: 0.001%
 -209: 0.002%
 -208: 0.003%
 -207: 0.002%
 -205: 0.004%
 -203: 0.002%
 -202: 0.001%
 -201: 0.004%
 -199: 0.001%
 -198: 0.002%
 -197: 0.003%
 -196: 0.001%
 -195: 0.001%
 -194: 0.001%
 -193: 0.001%
 -192: 0.002%
 -191: 0.002%
 -190: 0.002%
 -188: 0.002%
 -186: 0.001%
 -185: 0.004%
 -184: 0.003%
 -183: 0.001%
 -182: 0.002%
 -181: 0.002%
 -180: 0.001%
 -179: 0.003%
 -177: 0.001%
 -176: 0.005%
 -175: 0.003%
 -173: 0.003%
 -172: 0.001%
 -171: 0.002%
 -170: 0.002%
 -169: 0.004%
 -168: 0.001%
 -167: 0.003%
 -166: 0.001%
 -164: 0.003%
 -163: 0.004%
 -162: 0.003%
 -161: 0.003%
 -160: 0.003%
 -159: 0.004%
 -158: 0.005%
 -157: 0.003%
 -156: 0.006%
 -155: 0.001%
 -154: 0.002%
 -153: 0.006%
 -152: 0.003%
 -151: 0.001%
 -150: 0.003%
 -149: 0.002%
 -148: 0.003%
 -147: 0.002%
 -146: 0.001%
 -145: 0.004%
 -144: 0.001%
 -143: 0.008%
 -142: 0.006%
 -141: 0.004%
 -140: 0.002%
 -139: 0.005%
 -138: 0.002%
 -137: 0.006%
 -136: 0.001%
 -135: 0.003%
 -134: 0.001%
 -133: 0.004%
 -132: 0.005%
 -131: 0.004%
 -130: 0.002%
 -129: 0.001%
 -128: 0.006%
 -127: 0.008%
 -126: 0.006%
 -125: 0.004%
 -124: 0.003%
 -123: 0.003%
 -122: 0.002%
 -121: 0.004%
 -120: 0.004%
 -119: 0.008%
 -118: 0.004%
 -117: 0.003%
 -116: 0.009%
 -115: 0.006%
 -114: 0.008%
 -113: 0.001%
 -112: 0.003%
 -111: 0.001%
 -110: 0.003%
 -109: 0.008%
 -108: 0.007%
 -107: 0.003%
 -106: 0.006%
 -105: 0.007%
 -104: 0.006%
 -103: 0.006%
 -102: 0.009%
 -101: 0.006%
 -100: 0.005%
 -99: 0.004%
 -98: 0.005%
 -97: 0.008%
 -96: 0.007%
 -95: 0.008%
 -94: 0.008%
 -93: 0.003%
 -92: 0.006%
 -91: 0.006%
 -90: 0.004%
 -89: 0.009%
 -88: 0.011%
 -87: 0.006%
 -86: 0.009%
 -85: 0.009%
 -84: 0.009%
 -83: 0.009%
 -82: 0.006%
 -81: 0.007%
 -80: 0.009%
 -79: 0.009%
 -78: 0.012%
 -77: 0.009%
 -76: 0.013%
 -75: 0.015%
 -74: 0.008%
 -73: 0.007%
 -72: 0.01%
 -71: 0.017%
 -70: 0.017%
 -69: 0.012%
 -68: 0.012%
 -67: 0.018%
 -66: 0.014%
 -65: 0.013%
 -64: 0.017%
 -63: 0.016%
 -62: 0.018%
 -61: 0.01%
 -60: 0.02%
 -59: 0.022%
 -58: 0.021%
 -57: 0.021%
 -56: 0.023%
 -55: 0.028%
 -54: 0.023%
 -53: 0.024%
 -52: 0.02%
 -51: 0.021%
 -50: 0.027%
 -49: 0.029%
 -48: 0.023%
 -47: 0.026%
 -46: 0.033%
 -45: 0.03%
 -44: 0.032%
 -43: 0.033%
 -42: 0.039%
 -41: 0.036%
 -40: 0.044%
 -39: 0.039%
 -38: 0.039%
 -37: 0.043%
 -36: 0.054%
 -35: 0.053%
 -34: 0.054%
 -33: 0.072%
 -32: 0.072%
 -31: 0.068%
 -30: 0.069%
 -29: 0.075%
 -28: 0.078%
 -27: 0.074%
 -26: 0.087%
 -25: 0.097%
 -24: 0.129%
 -23: 0.114%
 -22: 0.128%
 -21: 0.112%
 -20: 0.146%
 -19: 0.181%
 -18: 0.209%
 -17: 0.231%
 -16: 0.268%
 -15: 0.282%
 -14: 0.326%
 -13: 0.375%
 -12: 0.44%
 -11: 0.541%
 -10: 0.594%
 -9: 0.726%
 -8: 0.871%
 -7: 1.254%
 -6: 1.543%
 -5: 2.185%
 -4: 3.197%
 -3: 4.992%
 -2: 7.934%
 -1: 12.676%
 0: 15.698%
 1: 12.771%
 2: 8.099%
 3: 4.973%
 4: 3.133%
 5: 2.16%
 6: 1.588%
 7: 1.24%
 8: 0.977%
 9: 0.792%
 10: 0.602%
 11: 0.528%
 12: 0.447%
 13: 0.37%
 14: 0.283%
 15: 0.276%
 16: 0.243%
 17: 0.218%
 18: 0.198%
 19: 0.174%
 20: 0.169%
 21: 0.112%
 22: 0.115%
 23: 0.109%
 24: 0.116%
 25: 0.085%
 26: 0.093%
 27: 0.086%
 28: 0.086%
 29: 0.081%
 30: 0.082%
 31: 0.075%
 32: 0.057%
 33: 0.067%
 34: 0.049%
 35: 0.064%
 36: 0.05%
 37: 0.043%
 38: 0.027%
 39: 0.03%
 40: 0.035%
 41: 0.043%
 42: 0.047%
 43: 0.034%
 44: 0.038%
 45: 0.027%
 46: 0.03%
 47: 0.026%
 48: 0.034%
 49: 0.026%
 50: 0.027%
 51: 0.028%
 52: 0.026%
 53: 0.028%
 54: 0.03%
 55: 0.021%
 56: 0.028%
 57: 0.019%
 58: 0.009%
 59: 0.018%
 60: 0.014%
 61: 0.013%
 62: 0.013%
 63: 0.011%
 64: 0.019%
 65: 0.017%
 66: 0.018%
 67: 0.014%
 68: 0.015%
 69: 0.016%
 70: 0.012%
 71: 0.012%
 72: 0.016%
 73: 0.011%
 74: 0.017%
 75: 0.017%
 76: 0.014%
 77: 0.011%
 78: 0.007%
 79: 0.012%
 80: 0.008%
 81: 0.01%
 82: 0.005%
 83: 0.009%
 84: 0.007%
 85: 0.009%
 86: 0.014%
 87: 0.005%
 88: 0.006%
 89: 0.01%
 90: 0.01%
 91: 0.008%
 92: 0.008%
 93: 0.005%
 94: 0.008%
 95: 0.006%
 96: 0.006%
 97: 0.008%
 98: 0.006%
 99: 0.006%
 100: 0.007%
 101: 0.003%
 102: 0.002%
 103: 0.004%
 104: 0.006%
 105: 0.008%
 106: 0.01%
 107: 0.008%
 108: 0.01%
 109: 0.005%
 110: 0.006%
 111: 0.007%
 112: 0.003%
 113: 0.006%
 114: 0.001%
 115: 0.004%
 116: 0.004%
 117: 0.006%
 118: 0.002%
 119: 0.004%
 120: 0.002%
 121: 0.004%
 122: 0.003%
 123: 0.006%
 124: 0.002%
 125: 0.001%
 126: 0.002%
 127: 0.003%
 128: 0.003%
 129: 0.011%
 130: 0.002%
 131: 0.001%
 132: 0.002%
 133: 0.003%
 134: 0.005%
 135: 0.001%
 136: 0.002%
 137: 0.001%
 139: 0.003%
 140: 0.001%
 141: 0.004%
 142: 0.003%
 143: 0.002%
 144: 0.003%
 145: 0.001%
 146: 0.003%
 147: 0.002%
 148: 0.003%
 149: 0.005%
 150: 0.003%
 151: 0.002%
 152: 0.003%
 153: 0.004%
 154: 0.002%
 155: 0.001%
 156: 0.004%
 157: 0.003%
 158: 0.004%
 159: 0.003%
 160: 0.004%
 161: 0.003%
 162: 0.001%
 163: 0.001%
 164: 0.002%
 165: 0.005%
 166: 0.001%
 167: 0.003%
 168: 0.002%
 169: 0.003%
 170: 0.003%
 171: 0.002%
 173: 0.002%
 174: 0.003%
 175: 0.002%
 176: 0.002%
 177: 0.003%
 178: 0.003%
 179: 0.001%
 180: 0.002%
 181: 0.001%
 182: 0.003%
 183: 0.001%
 184: 0.001%
 185: 0.002%
 186: 0.003%
 187: 0.001%
 188: 0.002%
 189: 0.001%
 191: 0.004%
 192: 0.002%
 195: 0.001%
 197: 0.001%
 198: 0.002%
 199: 0.003%
 200: 0.001%
 201: 0.005%
 202: 0.002%
 204: 0.001%
 205: 0.002%
 206: 0.003%
 208: 0.002%
 209: 0.002%
 210: 0.001%
 211: 0.001%
 212: 0.004%
 214: 0.002%
 215: 0.003%
 216: 0.002%
 217: 0.002%
 219: 0.002%
 222: 0.001%
 223: 0.001%
 224: 0.003%
 225: 0.002%
 226: 0.002%
 227: 0.002%
 229: 0.002%
 231: 0.002%
 233: 0.001%
 234: 0.001%
 235: 0.001%
 236: 0.002%
 238: 0.002%
 239: 0.001%
 240: 0.001%
 241: 0.001%
 242: 0.002%
 243: 0.001%
 244: 0.003%
 247: 0.001%
 248: 0.003%
 250: 0.001%
 252: 0.002%
 254: 0.002%
 257: 0.002%
 258: 0.001%
 260: 0.001%
 266: 0.002%
 268: 0.001%
 269: 0.002%
 270: 0.001%
 271: 0.002%
 272: 0.002%
 273: 0.001%
 275: 0.001%
 276: 0.001%
 278: 0.001%
 279: 0.001%
 282: 0.003%
 284: 0.001%
 291: 0.001%
 293: 0.002%
 297: 0.001%
 298: 0.001%
 299: 0.001%
 300: 0.001%
 302: 0.003%
 306: 0.001%
 307: 0.001%
 312: 0.001%
 314: 0.003%
 316: 0.002%
 319: 0.001%
 320: 0.002%
 322: 0.001%
 323: 0.002%
 324: 0.001%
 326: 0.001%
 327: 0.001%
 328: 0.001%
 329: 0.001%
 331: 0.001%
 332: 0.001%
 335: 0.002%
 337: 0.001%
 338: 0.002%
 340: 0.001%
 341: 0.001%
 343: 0.001%
 349: 0.001%
 352: 0.001%
 354: 0.001%
 356: 0.001%
 357: 0.001%
 362: 0.001%
 364: 0.001%
 370: 0.001%
 371: 0.002%
 372: 0.002%
 373: 0.001%
 380: 0.001%
 383: 0.001%
 389: 0.001%
 390: 0.002%
 391: 0.001%
 393: 0.001%
 394: 0.001%
 397: 0.001%
 399: 0.001%
 400: 0.001%
 401: 0.001%
 404: 0.001%
 408: 0.001%
 410: 0.001%
 412: 0.001%
 413: 0.002%
 414: 0.001%
 417: 0.001%
 420: 0.001%
 422: 0.001%
 425: 0.002%
 431: 0.001%
 433: 0.001%
 436: 0.001%
 437: 0.001%
 438: 0.001%
 441: 0.001%
 446: 0.001%
 453: 0.001%
 456: 0.001%
 458: 0.002%
 462: 0.002%
 463: 0.001%
 471: 0.001%
 472: 0.001%
 475: 0.001%
 477: 0.001%
 483: 0.001%
 494: 0.001%
 498: 0.001%
 500: 0.001%
 509: 0.001%
 510: 0.001%
 513: 0.001%
 517: 0.001%
 521: 0.001%
 523: 0.001%
 526: 0.001%
 541: 0.001%
 542: 0.001%
 556: 0.001%
 569: 0.001%
 572: 0.001%
 584: 0.001%
 590: 0.001%
 612: 0.001%
 616: 0.001%
 618: 0.001%
 619: 0.002%
 625: 0.001%
 627: 0.001%
 628: 0.001%
 644: 0.001%
 655: 0.001%
 657: 0.001%
 659: 0.001%
 664: 0.001%
 672: 0.001%
 696: 0.001%
 721: 0.001%
 724: 0.001%
 743: 0.001%
 754: 0.001%
 762: 0.001%
 785: 0.001%
 795: 0.001%
 806: 0.001%
 853: 0.001%
 855: 0.001%
 867: 0.001%
 886: 0.001%
 889: 0.001%
 905: 0.001%
 923: 0.001%
 925: 0.001%
 927: 0.001%
 930: 0.001%
 939: 0.001%
 942: 0.001%
 944: 0.001%
 981: 0.001%
 998: 0.001%
 1001: 0.001%
 1045: 0.001%
 1056: 0.001%
 1095: 0.001%
 1104: 0.001%
 1184: 0.001%
 1218: 0.001%
 1230: 0.001%
 1237: 0.001%
 1262: 0.001%
 1297: 0.001%
 1303: 0.001%
 1314: 0.001%
 1356: 0.001%
 1360: 0.001%
 1367: 0.001%
 1390: 0.001%
 1444: 0.001%
 1446: 0.001%
 1472: 0.001%
 1480: 0.001%
 1601: 0.001%
 1605: 0.001%
 1637: 0.001%
 1747: 0.001%
 1823: 0.001%
 1842: 0.001%
 1883: 0.001%
 1898: 0.001%
 1919: 0.001%
 1943: 0.001%
 2183: 0.001%
 2307: 0.001%
 2395: 0.001%
 2507: 0.001%
 2672: 0.001%
 2678: 0.001%
 2697: 0.001%
 2718: 0.001%
 2723: 0.001%
 2793: 0.001%
 2794: 0.001%
 3029: 0.001%
 3063: 0.001%
 3249: 0.001%
 3278: 0.001%
 3404: 0.001%
 3411: 0.001%
 3438: 0.001%
 3979: 0.001%
 4083: 0.001%
 4561: 0.001%
 6017: 0.001%
 6192: 0.001%
 6373: 0.001%
 7274: 0.001%
 8173: 0.001%
 8295: 0.001%
 11149: 0.001%
 11867: 0.001%
 12133: 0.001%
 12625: 0.001%
 20884: 0.001%
 33440: 0.001%
 40854: 0.001%
 1133006: 0.001%

Output Analysis: fisher_f_variate(2.0, 3.0)
Typical Timing: 81 ± 2 ns
Statistics of 1000 samples:
 Minimum: 0.00014161197428414548
 Median: (0.8329370671199432, 0.8342505030212336)
 Maximum: 520.7257752008326
 Mean: 2.9355295833473205
 Std Deviation: 17.571303995557635
round distribution of 100000:
 0: 34.985%
 1: 29.91%
 2: 12.237%
 3: 6.369%
 4: 3.949%
 5: 2.608%
 6: 1.788%
 7: 1.259%
 8: 1.001%
 9: 0.762%
 10: 0.653%
 11: 0.526%
 12: 0.446%
 13: 0.367%
 14: 0.284%
 15: 0.269%
 16: 0.228%
 17: 0.174%
 18: 0.149%
 19: 0.158%
 20: 0.11%
 21: 0.113%
 22: 0.092%
 23: 0.09%
 24: 0.089%
 25: 0.092%
 26: 0.081%
 27: 0.053%
 28: 0.065%
 29: 0.051%
 30: 0.046%
 31: 0.054%
 32: 0.042%
 33: 0.04%
 34: 0.039%
 35: 0.044%
 36: 0.028%
 37: 0.027%
 38: 0.03%
 39: 0.023%
 40: 0.018%
 41: 0.029%
 42: 0.021%
 43: 0.021%
 44: 0.026%
 45: 0.02%
 46: 0.018%
 47: 0.014%
 48: 0.015%
 49: 0.017%
 50: 0.017%
 51: 0.012%
 52: 0.012%
 53: 0.016%
 54: 0.007%
 55: 0.011%
 56: 0.008%
 57: 0.011%
 58: 0.013%
 59: 0.006%
 60: 0.006%
 61: 0.011%
 62: 0.005%
 63: 0.007%
 64: 0.007%
 65: 0.002%
 66: 0.004%
 67: 0.008%
 68: 0.009%
 69: 0.007%
 70: 0.002%
 71: 0.01%
 72: 0.003%
 73: 0.008%
 74: 0.004%
 75: 0.01%
 76: 0.002%
 77: 0.004%
 78: 0.005%
 79: 0.005%
 80: 0.005%
 81: 0.003%
 82: 0.008%
 83: 0.003%
 84: 0.002%
 85: 0.004%
 86: 0.003%
 87: 0.003%
 88: 0.004%
 89: 0.003%
 90: 0.005%
 91: 0.003%
 92: 0.002%
 93: 0.003%
 94: 0.001%
 95: 0.005%
 96: 0.002%
 97: 0.004%
 98: 0.003%
 99: 0.002%
 100: 0.004%
 101: 0.001%
 102: 0.003%
 103: 0.001%
 105: 0.004%
 106: 0.004%
 107: 0.002%
 108: 0.003%
 109: 0.001%
 110: 0.001%
 112: 0.005%
 113: 0.002%
 114: 0.003%
 115: 0.001%
 116: 0.005%
 118: 0.002%
 119: 0.002%
 120: 0.001%
 122: 0.002%
 123: 0.003%
 124: 0.001%
 125: 0.001%
 126: 0.002%
 127: 0.001%
 128: 0.003%
 129: 0.001%
 130: 0.001%
 131: 0.001%
 133: 0.002%
 134: 0.002%
 135: 0.001%
 136: 0.001%
 138: 0.002%
 140: 0.002%
 142: 0.004%
 144: 0.001%
 145: 0.002%
 147: 0.001%
 148: 0.001%
 149: 0.003%
 150: 0.002%
 153: 0.001%
 154: 0.001%
 157: 0.002%
 159: 0.001%
 160: 0.001%
 161: 0.002%
 162: 0.001%
 163: 0.001%
 164: 0.001%
 166: 0.002%
 168: 0.001%
 169: 0.001%
 172: 0.002%
 173: 0.001%
 175: 0.001%
 178: 0.002%
 182: 0.002%
 184: 0.002%
 186: 0.001%
 191: 0.001%
 193: 0.002%
 196: 0.001%
 197: 0.001%
 198: 0.001%
 199: 0.001%
 200: 0.001%
 202: 0.001%
 203: 0.001%
 206: 0.001%
 207: 0.001%
 214: 0.002%
 218: 0.001%
 221: 0.001%
 225: 0.001%
 228: 0.001%
 229: 0.001%
 233: 0.001%
 239: 0.002%
 240: 0.001%
 244: 0.001%
 248: 0.001%
 255: 0.001%
 258: 0.001%
 267: 0.001%
 268: 0.002%
 278: 0.001%
 281: 0.001%
 290: 0.001%
 291: 0.001%
 295: 0.001%
 308: 0.001%
 332: 0.001%
 340: 0.001%
 350: 0.001%
 364: 0.001%
 376: 0.001%
 383: 0.001%
 388: 0.001%
 397: 0.001%
 411: 0.001%
 466: 0.001%
 481: 0.001%
 484: 0.001%
 521: 0.001%
 600: 0.001%
 634: 0.001%
 736: 0.001%
 770: 0.001%
 788: 0.001%
 1134: 0.001%
 2014: 0.001%
 6696: 0.001%
 11991: 0.001%
 13090: 0.001%

Output Analysis: student_t_variate(5.0)
Typical Timing: 86 ± 3 ns
Statistics of 1000 samples:
 Minimum: -8.112937193099484
 Median: (-0.015165576832629058, -0.011616800659494358)
 Maximum: 5.144077418064832
 Mean: -0.025794137380621935
 Std Deviation: 1.2822587401813301
round distribution of 100000:
 -23: 0.001%
 -17: 0.001%
 -15: 0.001%
 -11: 0.001%
 -10: 0.001%
 -9: 0.003%
 -8: 0.019%
 -7: 0.034%
 -6: 0.057%
 -5: 0.185%
 -4: 0.543%
 -3: 1.803%
 -2: 6.922%
 -1: 22.078%
 0: 36.146%
 1: 22.601%
 2: 6.919%
 3: 1.814%
 4: 0.56%
 5: 0.191%
 6: 0.064%
 7: 0.025%
 8: 0.013%
 9: 0.005%
 10: 0.008%
 11: 0.002%
 12: 0.002%
 13: 0.001%


Random Booleans:

Output Analysis: percent_true(33.33)
Typical Timing: 21 ± 1 ns
Statistics of 1000 samples:
 Minimum: False
 Median: False
 Maximum: True
 Mean: 0.332
 Std Deviation: 0.4711666350644939
Distribution of 100000 samples:
 False: 66.582%
 True: 33.418%


Shuffle Performance:

some_small_list = [i for i in range(10)]
some_med_list = [i for i in range(100)]
some_large_list = [i for i in range(1000)]

Base Case:
Random.shuffle()  # fisher_yates in python
Typical Timing: 1438 ± 28 ns
Typical Timing: 12442 ± 73 ns
Typical Timing: 136738 ± 1256 ns

Fortuna.shuffle()  # knuth_b in cython
Typical Timing: 209 ± 7 ns
Typical Timing: 1900 ± 19 ns
Typical Timing: 17996 ± 127 ns

Fortuna.knuth_a()  # knuth_a in cython
Typical Timing: 443 ± 8 ns
Typical Timing: 3546 ± 46 ns
Typical Timing: 40845 ± 184 ns

Fortuna.fisher_yates()  # fisher_yates in cython
Typical Timing: 472 ± 8 ns
Typical Timing: 3639 ± 50 ns
Typical Timing: 41554 ± 429 ns

smart_clamp(3, 2, 1) # should be 2:  2
Typical Timing: 44 ± 3 ns
float_clamp(3.0, 2.0, 1.0) # should be 2.0:  2.0
Typical Timing: 39 ± 3 ns


-------------------------------------------------------------------------
Total Test Time: 3.563 seconds
```


## Legal Information
Fortuna is licensed under a Creative Commons Attribution-NonCommercial 3.0 Unported License. 
See online version of this license here: <http://creativecommons.org/licenses/by-nc/3.0/>

Other licensing options are available, please contact the author for details: [Robert Sharp](mailto:webmaster@sharpdesigndigital.com)
