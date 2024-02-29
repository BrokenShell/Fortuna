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

##### Fortuna 5.4.2
- Storm 3.9.2 update

##### Fortuna 5.4.1
- Bug fixes

##### Fortuna 5.4.0
- Adds DistributionRange
- Changes signature of distribution_range, use DistributionRange for previous behavior

##### Fortuna 5.3.2
- FlexCat now handles (cycle, cycle) more intuitively

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
Fortuna Version: 5.4.2
Storm Version: 3.9.2

Smart Clamp: Pass
Float Clamp: Pass

Data:
some_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

Base Case
Output Analysis: Random.choice(some_list)
Typical Timing: 284 ± 27 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 5
 Maximum: 9
 Mean: 4.684
 Std Deviation: 2.888682829333897
Distribution of 100000 samples:
 0: 9.958%
 1: 10.116%
 2: 10.046%
 3: 9.859%
 4: 9.979%
 5: 9.888%
 6: 10.071%
 7: 10.11%
 8: 10.019%
 9: 9.954%

Output Analysis: random_value(some_list)
Typical Timing: 39 ± 5 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 5
 Maximum: 9
 Mean: 4.588
 Std Deviation: 2.8541903234371744
Distribution of 100000 samples:
 0: 9.893%
 1: 10.064%
 2: 10.052%
 3: 10.0%
 4: 10.063%
 5: 10.004%
 6: 10.024%
 7: 9.854%
 8: 9.947%
 9: 10.099%


Wide Distribution

Truffle = TruffleShuffle(some_list)
Output Analysis: Truffle()
Typical Timing: 205 ± 7 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: (4, 5)
 Maximum: 9
 Mean: 4.506
 Std Deviation: 2.8768455363888137
Distribution of 100000 samples:
 0: 9.906%
 1: 10.044%
 2: 10.103%
 3: 9.907%
 4: 10.127%
 5: 10.012%
 6: 10.074%
 7: 9.94%
 8: 9.907%
 9: 9.98%

truffle = truffle_shuffle(some_list)
Output Analysis: truffle()
Typical Timing: 86 ± 6 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 5
 Maximum: 9
 Mean: 4.539
 Std Deviation: 2.8765871712419484
Distribution of 100000 samples:
 0: 10.031%
 1: 9.907%
 2: 9.969%
 3: 10.061%
 4: 10.028%
 5: 10.098%
 6: 10.004%
 7: 9.939%
 8: 10.044%
 9: 9.919%


Single objects with many distribution possibilities

some_tuple = tuple(i for i in range(10))

monty = QuantumMonty(some_tuple)
Output Analysis: monty()
Typical Timing: 223 ± 8 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 5
 Maximum: 9
 Mean: 4.615
 Std Deviation: 2.8766386721397685
Distribution of 100000 samples:
 0: 10.835%
 1: 8.959%
 2: 8.978%
 3: 9.662%
 4: 11.543%
 5: 11.364%
 6: 9.723%
 7: 9.158%
 8: 8.951%
 9: 10.827%

rand_value = <Fortuna.RandomValue object at 0x102bda980>
Output Analysis: rand_value()
Typical Timing: 174 ± 11 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 5
 Maximum: 9
 Mean: 4.541
 Std Deviation: 2.8942521824636662
Distribution of 100000 samples:
 0: 10.137%
 1: 9.879%
 2: 9.967%
 3: 9.886%
 4: 9.901%
 5: 9.982%
 6: 9.962%
 7: 9.936%
 8: 10.203%
 9: 10.147%


Weighted Tables:

population = ('A', 'B', 'C', 'D')
cum_weights = (1, 3, 6, 10)
rel_weights = (1, 2, 3, 4)
cum_weighted_table = zip(cum_weights, population)
rel_weighted_table = zip(rel_weights, population)

Cumulative Base Case
Output Analysis: Random.choices(population, cum_weights=cum_weights)
Typical Timing: 556 ± 21 ns
Distribution of 100000 samples:
 A: 9.907%
 B: 20.097%
 C: 30.332%
 D: 39.664%

cum_weighted_choice = CumulativeWeightedChoice(cum_weighted_table)
Output Analysis: cum_weighted_choice()
Typical Timing: 173 ± 8 ns
Distribution of 100000 samples:
 A: 9.865%
 B: 19.925%
 C: 30.007%
 D: 40.203%

Output Analysis: cumulative_weighted_choice(tuple(zip(cum_weights, population)))
Typical Timing: 80 ± 5 ns
Distribution of 100000 samples:
 A: 9.88%
 B: 19.909%
 C: 30.05%
 D: 40.161%

Relative Base Case
Output Analysis: Random.choices(population, weights=rel_weights)
Typical Timing: 709 ± 14 ns
Distribution of 100000 samples:
 A: 9.771%
 B: 20.083%
 C: 29.982%
 D: 40.164%

rel_weighted_choice = RelativeWeightedChoice(rel_weighted_table)
Output Analysis: rel_weighted_choice()
Typical Timing: 170 ± 6 ns
Distribution of 100000 samples:
 A: 10.116%
 B: 19.949%
 C: 29.959%
 D: 39.976%


Random Matrix Values:

some_matrix = {'A': (1, 2, 3, 4), 'B': (10, 20, 30, 40), 'C': (100, 200, 300, 400)}

flex_cat = FlexCat(some_matrix)
Output Analysis: flex_cat()
Typical Timing: 375 ± 11 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 4
 Maximum: 400
 Mean: 36.551
 Std Deviation: 82.99499725024737
Distribution of 100000 samples:
 1: 13.854%
 2: 13.86%
 3: 13.954%
 4: 13.766%
 10: 8.45%
 20: 8.296%
 30: 8.293%
 40: 8.385%
 100: 2.793%
 200: 2.785%
 300: 2.759%
 400: 2.805%

Output Analysis: flex_cat("C")
Typical Timing: 248 ± 8 ns
Statistics of 1000 samples:
 Minimum: 100
 Median: 200
 Maximum: 400
 Mean: 248.4
 Std Deviation: 112.20530303880486
Distribution of 100000 samples:
 100: 25.127%
 200: 24.824%
 300: 24.98%
 400: 25.069%


Random Integers:

Base Case
Output Analysis: Random.randrange(10)
Typical Timing: 161 ± 6 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 5
 Maximum: 9
 Mean: 4.605
 Std Deviation: 2.8122737924824963
Distribution of 100000 samples:
 0: 10.18%
 1: 10.022%
 2: 9.794%
 3: 9.932%
 4: 9.937%
 5: 10.135%
 6: 9.898%
 7: 10.169%
 8: 9.983%
 9: 9.95%

Output Analysis: random_below(10)
Typical Timing: 36 ± 3 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 5
 Maximum: 9
 Mean: 4.555
 Std Deviation: 2.8090685050147615
Distribution of 100000 samples:
 0: 9.832%
 1: 10.173%
 2: 9.799%
 3: 9.952%
 4: 9.928%
 5: 9.983%
 6: 10.19%
 7: 10.232%
 8: 9.848%
 9: 10.063%

Output Analysis: random_index(10)
Typical Timing: 33 ± 1 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 5
 Maximum: 9
 Mean: 4.424
 Std Deviation: 2.9032141933816478
Distribution of 100000 samples:
 0: 10.057%
 1: 9.952%
 2: 9.999%
 3: 10.19%
 4: 9.786%
 5: 10.079%
 6: 10.18%
 7: 9.795%
 8: 10.091%
 9: 9.871%

Output Analysis: random_range(10)
Typical Timing: 41 ± 2 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 5
 Maximum: 9
 Mean: 4.593
 Std Deviation: 2.854732999861896
Distribution of 100000 samples:
 0: 10.124%
 1: 9.994%
 2: 10.092%
 3: 9.867%
 4: 9.831%
 5: 10.043%
 6: 9.934%
 7: 9.83%
 8: 10.233%
 9: 10.052%

Output Analysis: random_below(-10)
Typical Timing: 42 ± 2 ns
Statistics of 1000 samples:
 Minimum: -9
 Median: -5
 Maximum: 0
 Mean: -4.487
 Std Deviation: 2.930942070635553
Distribution of 100000 samples:
 -9: 10.123%
 -8: 10.075%
 -7: 9.978%
 -6: 10.006%
 -5: 9.95%
 -4: 9.9%
 -3: 9.952%
 -2: 9.966%
 -1: 10.038%
 0: 10.012%

Output Analysis: random_index(-10)
Typical Timing: 48 ± 6 ns
Statistics of 1000 samples:
 Minimum: -10
 Median: -5
 Maximum: -1
 Mean: -5.399
 Std Deviation: 2.886196308141414
Distribution of 100000 samples:
 -10: 10.118%
 -9: 10.101%
 -8: 9.999%
 -7: 10.041%
 -6: 9.876%
 -5: 9.916%
 -4: 10.077%
 -3: 9.944%
 -2: 9.959%
 -1: 9.969%

Output Analysis: random_range(-10)
Typical Timing: 53 ± 2 ns
Statistics of 1000 samples:
 Minimum: -10
 Median: -5
 Maximum: -1
 Mean: -5.565
 Std Deviation: 2.8600620543888473
Distribution of 100000 samples:
 -10: 10.007%
 -9: 10.094%
 -8: 9.892%
 -7: 9.988%
 -6: 9.828%
 -5: 10.033%
 -4: 10.165%
 -3: 10.06%
 -2: 9.915%
 -1: 10.018%

Base Case
Output Analysis: Random.randrange(1, 10)
Typical Timing: 196 ± 7 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 5
 Maximum: 9
 Mean: 5.038
 Std Deviation: 2.5937006926943753
Distribution of 100000 samples:
 1: 11.052%
 2: 11.119%
 3: 11.115%
 4: 11.136%
 5: 11.036%
 6: 11.319%
 7: 11.123%
 8: 11.061%
 9: 11.039%

Output Analysis: random_range(1, 10)
Typical Timing: 43 ± 2 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 5
 Maximum: 9
 Mean: 5.004
 Std Deviation: 2.5819857959815833
Distribution of 100000 samples:
 1: 11.09%
 2: 11.198%
 3: 10.98%
 4: 11.094%
 5: 11.104%
 6: 11.131%
 7: 11.145%
 8: 11.077%
 9: 11.181%

Output Analysis: random_range(10, 1)
Typical Timing: 43 ± 2 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 5
 Maximum: 9
 Mean: 4.938
 Std Deviation: 2.5816314262149858
Distribution of 100000 samples:
 1: 11.327%
 2: 10.976%
 3: 11.212%
 4: 11.07%
 5: 10.919%
 6: 11.204%
 7: 11.032%
 8: 11.17%
 9: 11.09%

Base Case
Output Analysis: Random.randint(-5, 5)
Typical Timing: 214 ± 7 ns
Statistics of 1000 samples:
 Minimum: -5
 Median: 0
 Maximum: 5
 Mean: -0.002
 Std Deviation: 3.1893836658778083
Distribution of 100000 samples:
 -5: 9.092%
 -4: 9.188%
 -3: 8.879%
 -2: 9.082%
 -1: 9.092%
 0: 9.002%
 1: 9.119%
 2: 9.036%
 3: 9.235%
 4: 9.198%
 5: 9.077%

Output Analysis: random_int(-5, 5)
Typical Timing: 29 ± 1 ns
Statistics of 1000 samples:
 Minimum: -5
 Median: 0
 Maximum: 5
 Mean: -0.079
 Std Deviation: 3.183849226313315
Distribution of 100000 samples:
 -5: 9.021%
 -4: 9.111%
 -3: 9.091%
 -2: 9.036%
 -1: 9.103%
 0: 9.22%
 1: 8.972%
 2: 9.104%
 3: 9.087%
 4: 9.205%
 5: 9.05%

Base Case
Output Analysis: Random.randrange(1, 20, 2)
Typical Timing: 225 ± 8 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 9
 Maximum: 19
 Mean: 9.908
 Std Deviation: 5.833829751507115
Distribution of 100000 samples:
 1: 10.07%
 3: 10.015%
 5: 9.966%
 7: 10.094%
 9: 9.962%
 11: 10.047%
 13: 9.988%
 15: 10.006%
 17: 9.993%
 19: 9.859%

Output Analysis: random_range(1, 20, 2)
Typical Timing: 41 ± 1 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 9
 Maximum: 19
 Mean: 9.84
 Std Deviation: 5.730553135539294
Distribution of 100000 samples:
 1: 10.03%
 3: 10.03%
 5: 10.108%
 7: 9.913%
 9: 9.934%
 11: 9.984%
 13: 10.113%
 15: 9.768%
 17: 10.182%
 19: 9.938%

Output Analysis: random_range(1, 20, -2)
Typical Timing: 49 ± 10 ns
Statistics of 1000 samples:
 Minimum: 2
 Median: 10
 Maximum: 20
 Mean: 10.842
 Std Deviation: 5.6807840398405665
Distribution of 100000 samples:
 2: 9.96%
 4: 10.077%
 6: 10.178%
 8: 10.119%
 10: 10.058%
 12: 9.917%
 14: 9.942%
 16: 9.933%
 18: 9.804%
 20: 10.012%

Output Analysis: random_range(20, 1, -2)
Typical Timing: 41 ± 2 ns
Statistics of 1000 samples:
 Minimum: 2
 Median: 12
 Maximum: 20
 Mean: 10.918
 Std Deviation: 5.821612076321057
Distribution of 100000 samples:
 2: 10.075%
 4: 10.027%
 6: 9.992%
 8: 9.906%
 10: 9.932%
 12: 10.116%
 14: 10.029%
 16: 9.857%
 18: 10.077%
 20: 9.989%

Output Analysis: d(10)
Typical Timing: 32 ± 5 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 5
 Maximum: 10
 Mean: 5.552
 Std Deviation: 2.9233271869296193
Distribution of 100000 samples:
 1: 10.117%
 2: 10.108%
 3: 9.886%
 4: 9.857%
 5: 9.893%
 6: 9.838%
 7: 9.982%
 8: 10.3%
 9: 10.032%
 10: 9.987%

Output Analysis: dice(3, 6)
Typical Timing: 49 ± 3 ns
Statistics of 1000 samples:
 Minimum: 3
 Median: 11
 Maximum: 18
 Mean: 10.496
 Std Deviation: 2.9857827949967994
Distribution of 100000 samples:
 3: 0.45%
 4: 1.332%
 5: 2.901%
 6: 4.737%
 7: 6.987%
 8: 9.651%
 9: 11.56%
 10: 12.323%
 11: 12.392%
 12: 11.692%
 13: 9.782%
 14: 6.917%
 15: 4.604%
 16: 2.777%
 17: 1.451%
 18: 0.444%

Output Analysis: ability_dice(4)
Typical Timing: 106 ± 4 ns
Statistics of 1000 samples:
 Minimum: 3
 Median: 13
 Maximum: 18
 Mean: 12.307
 Std Deviation: 2.9091603967836175
Distribution of 100000 samples:
 3: 0.085%
 4: 0.298%
 5: 0.759%
 6: 1.575%
 7: 3.025%
 8: 4.717%
 9: 7.137%
 10: 9.366%
 11: 11.33%
 12: 12.949%
 13: 13.375%
 14: 12.393%
 15: 10.072%
 16: 7.136%
 17: 4.192%
 18: 1.591%

Output Analysis: plus_or_minus(5)
Typical Timing: 29 ± 2 ns
Statistics of 1000 samples:
 Minimum: -5
 Median: 0
 Maximum: 5
 Mean: -0.073
 Std Deviation: 3.1874489534470714
Distribution of 100000 samples:
 -5: 9.199%
 -4: 9.074%
 -3: 9.038%
 -2: 9.145%
 -1: 8.957%
 0: 9.112%
 1: 9.125%
 2: 9.085%
 3: 9.118%
 4: 9.058%
 5: 9.089%

Output Analysis: plus_or_minus_linear(5)
Typical Timing: 35 ± 1 ns
Statistics of 1000 samples:
 Minimum: -5
 Median: 0
 Maximum: 5
 Mean: -0.084
 Std Deviation: 2.3943008743006122
Distribution of 100000 samples:
 -5: 2.763%
 -4: 5.415%
 -3: 8.306%
 -2: 11.192%
 -1: 14.142%
 0: 16.813%
 1: 13.715%
 2: 11.037%
 3: 8.321%
 4: 5.582%
 5: 2.714%

Output Analysis: plus_or_minus_gauss(5)
Typical Timing: 46 ± 1 ns
Statistics of 1000 samples:
 Minimum: -5
 Median: 0
 Maximum: 4
 Mean: 0.062
 Std Deviation: 1.566080652012727
Distribution of 100000 samples:
 -5: 0.199%
 -4: 1.176%
 -3: 4.423%
 -2: 11.538%
 -1: 20.568%
 0: 24.56%
 1: 20.309%
 2: 11.491%
 3: 4.42%
 4: 1.125%
 5: 0.191%


Random Floats:

Base Case
Output Analysis: Random.random()
Typical Timing: 20 ± 2 ns
Statistics of 1000 samples:
 Minimum: 0.0010850668945411313
 Median: (0.5017894658439653, 0.5018511012964421)
 Maximum: 0.9989388191612222
 Mean: 0.5117654860783649
 Std Deviation: 0.2908881540749093
round distribution of 100000:
 0: 50.079%
 1: 49.921%

Output Analysis: canonical()
Typical Timing: 23 ± 2 ns
Statistics of 1000 samples:
 Minimum: 0.000730669799940836
 Median: (0.4771261526027141, 0.47868022772188584)
 Maximum: 0.9960661710448413
 Mean: 0.48207006242879785
 Std Deviation: 0.2866735325708603
round distribution of 100000:
 0: 49.83%
 1: 50.17%

Base Case
Output Analysis: Random.uniform(0.0, 10.0)
Typical Timing: 69 ± 4 ns
Statistics of 1000 samples:
 Minimum: 0.009929659872088825
 Median: (5.137657155191108, 5.13988752053843)
 Maximum: 9.995822736208828
 Mean: 5.109606887047073
 Std Deviation: 2.943811292387183
floor distribution of 100000:
 0: 9.972%
 1: 10.016%
 2: 10.135%
 3: 9.826%
 4: 9.855%
 5: 10.022%
 6: 10.035%
 7: 10.05%
 8: 10.084%
 9: 10.005%

Output Analysis: random_float(0.0, 10.0)
Typical Timing: 24 ± 1 ns
Statistics of 1000 samples:
 Minimum: 0.01665012462268345
 Median: (5.185344353305517, 5.204913868927886)
 Maximum: 9.995633553009927
 Mean: 5.111207613634294
 Std Deviation: 2.888147019244586
floor distribution of 100000:
 0: 10.071%
 1: 10.022%
 2: 9.875%
 3: 9.963%
 4: 9.986%
 5: 9.949%
 6: 10.024%
 7: 10.135%
 8: 10.027%
 9: 9.948%

Base Case
Output Analysis: Random.triangular(0.0, 10.0, 5.0)
Typical Timing: 133 ± 3 ns
Statistics of 1000 samples:
 Minimum: 0.08770813033420916
 Median: (5.033738737313602, 5.0366783134178785)
 Maximum: 9.780413996033921
 Mean: 4.972436349273304
 Std Deviation: 2.078660697189387
round distribution of 100000:
 0: 0.463%
 1: 3.946%
 2: 7.924%
 3: 12.015%
 4: 15.945%
 5: 19.058%
 6: 15.856%
 7: 12.205%
 8: 8.039%
 9: 4.046%
 10: 0.503%

Output Analysis: triangular(0.0, 10.0, 5.0)
Typical Timing: 35 ± 4 ns
Statistics of 1000 samples:
 Minimum: 0.2523754064475986
 Median: (5.025648377520446, 5.027082610354445)
 Maximum: 9.919426861610116
 Mean: 5.073605455643737
 Std Deviation: 2.08816984103464
round distribution of 100000:
 0: 0.507%
 1: 4.019%
 2: 8.06%
 3: 11.923%
 4: 16.102%
 5: 18.969%
 6: 16.065%
 7: 11.909%
 8: 7.993%
 9: 3.94%
 10: 0.513%

Output Analysis: beta_variate(1.0, 1.0)
Typical Timing: 48 ± 5 ns
Statistics of 1000 samples:
 Minimum: 0.003409346914595433
 Median: (0.48245339633125134, 0.48791954546968813)
 Maximum: 0.9992162212968309
 Mean: 0.4902891597244461
 Std Deviation: 0.2927884126635654
round distribution of 100000:
 0: 49.935%
 1: 50.065%

Output Analysis: pareto_variate(1.0)
Typical Timing: 34 ± 1 ns
Statistics of 1000 samples:
 Minimum: 1.0039904235523627
 Median: (2.0667334500142696, 2.0726740302924234)
 Maximum: 1089.4871728574135
 Mean: 8.115480918439978
 Std Deviation: 44.87845270074786
round distribution of 100000:
 1: 33.294%
 2: 26.614%
 3: 11.488%
 4: 6.331%
 5: 4.014%
 6: 2.791%
 7: 2.122%
 8: 1.544%
 9: 1.256%
 10: 1.016%
 11: 0.872%
 12: 0.704%
 13: 0.634%
 14: 0.49%
 15: 0.444%
 16: 0.404%
 17: 0.301%
 18: 0.289%
 19: 0.286%
 20: 0.262%
 21: 0.224%
 22: 0.21%
 23: 0.178%
 24: 0.187%
 25: 0.182%
 26: 0.144%
 27: 0.133%
 28: 0.121%
 29: 0.118%
 30: 0.104%
 31: 0.118%
 32: 0.101%
 33: 0.08%
 34: 0.082%
 35: 0.093%
 36: 0.07%
 37: 0.066%
 38: 0.071%
 39: 0.055%
 40: 0.062%
 41: 0.074%
 42: 0.042%
 43: 0.058%
 44: 0.056%
 45: 0.047%
 46: 0.052%
 47: 0.043%
 48: 0.042%
 49: 0.028%
 50: 0.039%
 51: 0.034%
 52: 0.042%
 53: 0.036%
 54: 0.042%
 55: 0.025%
 56: 0.04%
 57: 0.027%
 58: 0.022%
 59: 0.031%
 60: 0.031%
 61: 0.024%
 62: 0.025%
 63: 0.015%
 64: 0.025%
 65: 0.019%
 66: 0.017%
 67: 0.021%
 68: 0.018%
 69: 0.018%
 70: 0.027%
 71: 0.02%
 72: 0.019%
 73: 0.013%
 74: 0.016%
 75: 0.014%
 76: 0.015%
 77: 0.014%
 78: 0.016%
 79: 0.014%
 80: 0.017%
 81: 0.019%
 82: 0.013%
 83: 0.012%
 84: 0.013%
 85: 0.013%
 86: 0.014%
 87: 0.013%
 88: 0.017%
 89: 0.013%
 90: 0.012%
 91: 0.007%
 92: 0.009%
 93: 0.012%
 94: 0.009%
 95: 0.01%
 96: 0.016%
 97: 0.012%
 98: 0.007%
 99: 0.013%
 100: 0.009%
 101: 0.008%
 102: 0.006%
 103: 0.004%
 104: 0.009%
 105: 0.011%
 106: 0.006%
 107: 0.005%
 108: 0.01%
 109: 0.01%
 110: 0.013%
 111: 0.005%
 112: 0.007%
 113: 0.005%
 114: 0.01%
 115: 0.008%
 116: 0.007%
 117: 0.009%
 118: 0.006%
 119: 0.006%
 120: 0.007%
 121: 0.003%
 122: 0.005%
 123: 0.01%
 124: 0.006%
 125: 0.007%
 126: 0.006%
 127: 0.005%
 128: 0.003%
 129: 0.007%
 130: 0.006%
 131: 0.006%
 132: 0.005%
 133: 0.004%
 134: 0.007%
 135: 0.005%
 136: 0.005%
 137: 0.008%
 138: 0.014%
 139: 0.007%
 140: 0.008%
 141: 0.002%
 142: 0.004%
 143: 0.005%
 144: 0.004%
 145: 0.006%
 147: 0.008%
 148: 0.006%
 149: 0.007%
 150: 0.007%
 151: 0.005%
 152: 0.002%
 153: 0.003%
 154: 0.004%
 155: 0.006%
 156: 0.003%
 157: 0.006%
 158: 0.003%
 159: 0.005%
 160: 0.002%
 161: 0.005%
 162: 0.004%
 163: 0.006%
 164: 0.001%
 165: 0.003%
 166: 0.002%
 167: 0.002%
 168: 0.005%
 169: 0.006%
 170: 0.002%
 171: 0.006%
 172: 0.004%
 174: 0.007%
 175: 0.005%
 176: 0.002%
 177: 0.004%
 178: 0.004%
 180: 0.003%
 181: 0.003%
 182: 0.005%
 183: 0.001%
 184: 0.004%
 185: 0.004%
 187: 0.004%
 188: 0.004%
 189: 0.003%
 190: 0.002%
 191: 0.002%
 192: 0.004%
 193: 0.003%
 196: 0.001%
 197: 0.001%
 198: 0.004%
 199: 0.004%
 200: 0.005%
 201: 0.002%
 202: 0.002%
 204: 0.004%
 205: 0.003%
 206: 0.001%
 207: 0.002%
 208: 0.004%
 209: 0.001%
 210: 0.003%
 211: 0.003%
 212: 0.001%
 214: 0.006%
 215: 0.003%
 216: 0.002%
 217: 0.005%
 218: 0.002%
 219: 0.001%
 221: 0.004%
 222: 0.002%
 223: 0.008%
 224: 0.002%
 225: 0.001%
 226: 0.003%
 227: 0.003%
 228: 0.002%
 229: 0.001%
 230: 0.001%
 231: 0.004%
 232: 0.002%
 233: 0.003%
 234: 0.001%
 235: 0.005%
 236: 0.001%
 238: 0.001%
 239: 0.001%
 241: 0.001%
 242: 0.004%
 243: 0.001%
 244: 0.001%
 245: 0.001%
 246: 0.005%
 247: 0.001%
 248: 0.002%
 249: 0.004%
 251: 0.005%
 252: 0.004%
 253: 0.002%
 255: 0.001%
 256: 0.003%
 257: 0.003%
 258: 0.004%
 259: 0.003%
 260: 0.004%
 261: 0.001%
 262: 0.001%
 263: 0.003%
 264: 0.002%
 265: 0.002%
 266: 0.001%
 267: 0.001%
 268: 0.002%
 269: 0.002%
 270: 0.002%
 271: 0.003%
 272: 0.001%
 277: 0.002%
 278: 0.001%
 279: 0.005%
 281: 0.002%
 283: 0.002%
 285: 0.003%
 288: 0.002%
 289: 0.001%
 292: 0.004%
 294: 0.002%
 295: 0.002%
 296: 0.001%
 298: 0.001%
 300: 0.001%
 301: 0.001%
 302: 0.001%
 304: 0.001%
 307: 0.002%
 309: 0.001%
 310: 0.001%
 311: 0.002%
 313: 0.001%
 314: 0.002%
 315: 0.001%
 316: 0.001%
 319: 0.001%
 320: 0.002%
 324: 0.001%
 327: 0.001%
 328: 0.001%
 329: 0.003%
 331: 0.003%
 332: 0.001%
 335: 0.001%
 336: 0.001%
 339: 0.003%
 340: 0.002%
 345: 0.001%
 346: 0.001%
 347: 0.001%
 351: 0.002%
 353: 0.001%
 355: 0.001%
 358: 0.001%
 359: 0.001%
 361: 0.002%
 362: 0.001%
 363: 0.001%
 364: 0.001%
 365: 0.002%
 366: 0.001%
 368: 0.002%
 369: 0.001%
 370: 0.001%
 371: 0.002%
 382: 0.001%
 384: 0.001%
 387: 0.001%
 389: 0.002%
 391: 0.001%
 392: 0.001%
 393: 0.001%
 394: 0.001%
 395: 0.001%
 396: 0.001%
 397: 0.001%
 398: 0.003%
 400: 0.001%
 405: 0.001%
 406: 0.002%
 408: 0.001%
 411: 0.002%
 413: 0.001%
 420: 0.001%
 423: 0.001%
 425: 0.001%
 426: 0.001%
 430: 0.001%
 431: 0.002%
 432: 0.001%
 438: 0.002%
 440: 0.001%
 441: 0.001%
 443: 0.001%
 444: 0.001%
 445: 0.001%
 446: 0.001%
 450: 0.001%
 451: 0.001%
 452: 0.001%
 454: 0.001%
 462: 0.001%
 465: 0.001%
 466: 0.001%
 468: 0.001%
 470: 0.001%
 475: 0.001%
 476: 0.001%
 477: 0.001%
 478: 0.002%
 483: 0.001%
 486: 0.001%
 487: 0.001%
 492: 0.001%
 495: 0.002%
 499: 0.001%
 500: 0.001%
 509: 0.002%
 514: 0.001%
 520: 0.001%
 527: 0.003%
 528: 0.001%
 530: 0.002%
 536: 0.001%
 538: 0.001%
 547: 0.002%
 553: 0.001%
 555: 0.001%
 557: 0.001%
 560: 0.001%
 561: 0.001%
 562: 0.001%
 564: 0.001%
 565: 0.001%
 566: 0.001%
 570: 0.001%
 573: 0.001%
 574: 0.001%
 579: 0.001%
 581: 0.001%
 582: 0.001%
 586: 0.002%
 589: 0.001%
 590: 0.001%
 591: 0.001%
 593: 0.001%
 595: 0.001%
 596: 0.001%
 599: 0.001%
 605: 0.002%
 606: 0.001%
 608: 0.001%
 609: 0.001%
 615: 0.001%
 616: 0.001%
 620: 0.002%
 623: 0.001%
 628: 0.001%
 630: 0.001%
 637: 0.001%
 649: 0.001%
 650: 0.001%
 653: 0.001%
 659: 0.002%
 671: 0.001%
 679: 0.001%
 680: 0.002%
 685: 0.001%
 690: 0.001%
 691: 0.001%
 701: 0.001%
 716: 0.001%
 721: 0.001%
 724: 0.001%
 730: 0.001%
 732: 0.001%
 738: 0.001%
 743: 0.001%
 746: 0.001%
 748: 0.001%
 750: 0.001%
 752: 0.001%
 760: 0.001%
 762: 0.001%
 770: 0.001%
 793: 0.002%
 807: 0.001%
 811: 0.001%
 827: 0.001%
 829: 0.001%
 831: 0.001%
 835: 0.001%
 845: 0.001%
 848: 0.001%
 854: 0.001%
 860: 0.001%
 867: 0.001%
 880: 0.002%
 882: 0.001%
 884: 0.001%
 889: 0.001%
 933: 0.001%
 942: 0.001%
 948: 0.001%
 953: 0.001%
 957: 0.001%
 958: 0.001%
 963: 0.001%
 971: 0.001%
 1010: 0.001%
 1020: 0.001%
 1022: 0.001%
 1029: 0.001%
 1037: 0.001%
 1044: 0.001%
 1046: 0.001%
 1047: 0.001%
 1048: 0.001%
 1062: 0.001%
 1071: 0.001%
 1085: 0.001%
 1087: 0.001%
 1089: 0.001%
 1095: 0.001%
 1101: 0.001%
 1105: 0.001%
 1107: 0.001%
 1131: 0.001%
 1149: 0.001%
 1150: 0.001%
 1156: 0.001%
 1193: 0.001%
 1229: 0.001%
 1282: 0.002%
 1289: 0.001%
 1318: 0.001%
 1334: 0.002%
 1372: 0.001%
 1378: 0.001%
 1386: 0.001%
 1390: 0.001%
 1424: 0.001%
 1429: 0.001%
 1433: 0.001%
 1436: 0.001%
 1438: 0.001%
 1444: 0.001%
 1460: 0.001%
 1463: 0.001%
 1469: 0.001%
 1499: 0.001%
 1509: 0.001%
 1512: 0.001%
 1539: 0.001%
 1619: 0.001%
 1629: 0.001%
 1631: 0.001%
 1647: 0.001%
 1699: 0.001%
 1709: 0.001%
 1721: 0.001%
 1746: 0.001%
 1785: 0.001%
 1801: 0.001%
 1814: 0.001%
 1822: 0.001%
 1854: 0.001%
 1895: 0.001%
 1944: 0.001%
 1977: 0.001%
 1989: 0.001%
 2010: 0.001%
 2016: 0.001%
 2238: 0.001%
 2245: 0.001%
 2385: 0.001%
 2398: 0.001%
 2460: 0.001%
 2535: 0.001%
 2537: 0.001%
 2542: 0.001%
 2582: 0.001%
 2651: 0.001%
 2705: 0.001%
 2751: 0.001%
 2770: 0.001%
 2851: 0.001%
 2883: 0.001%
 3069: 0.001%
 3252: 0.001%
 3582: 0.001%
 3583: 0.001%
 3603: 0.001%
 3634: 0.001%
 3719: 0.001%
 4184: 0.001%
 4304: 0.001%
 4598: 0.001%
 4763: 0.001%
 4850: 0.001%
 5166: 0.001%
 5183: 0.001%
 5275: 0.001%
 5558: 0.001%
 5600: 0.001%
 5753: 0.001%
 5862: 0.001%
 6123: 0.001%
 6147: 0.001%
 6235: 0.001%
 7127: 0.001%
 7253: 0.001%
 7417: 0.001%
 7694: 0.001%
 7807: 0.001%
 9022: 0.001%
 9598: 0.001%
 10766: 0.001%
 12439: 0.001%
 12786: 0.001%
 13363: 0.001%
 16403: 0.001%
 17448: 0.001%
 19103: 0.001%
 24537: 0.001%
 40435: 0.001%
 41159: 0.001%
 82917: 0.001%

Base Case
Output Analysis: Random.vonmisesvariate(0.0, 1.0)
Typical Timing: 351 ± 13 ns
Statistics of 1000 samples:
 Minimum: 0.00551252560619565
 Median: (3.3307667288754734, 3.347503989628216)
 Maximum: 6.271221888912979
 Mean: 3.1744294814142355
 Std Deviation: 2.2864565635075977
round distribution of 100000:
 0: 16.684%
 1: 21.754%
 2: 8.647%
 3: 4.763%
 4: 6.815%
 5: 16.919%
 6: 24.418%

Output Analysis: vonmises_variate(0.0, 1.0)
Typical Timing: 86 ± 6 ns
Statistics of 1000 samples:
 Minimum: 0.001972440791996057
 Median: (3.6105229768023652, 3.6237568997737117)
 Maximum: 6.282248214021083
 Mean: 3.247098664448697
 Std Deviation: 2.247236720952072
round distribution of 100000:
 0: 16.65%
 1: 21.513%
 2: 8.538%
 3: 4.87%
 4: 7.007%
 5: 17.158%
 6: 24.264%

Output Analysis: bernoulli_variate(0.5)
Typical Timing: 21 ± 1 ns
Statistics of 1000 samples:
 Minimum: False
 Median: True
 Maximum: True
 Mean: 0.511
 Std Deviation: 0.5001291124591021
round distribution of 100000:
 0: 49.996%
 1: 50.004%

Output Analysis: binomial_variate(3, 0.5)
Typical Timing: 88 ± 4 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 1
 Maximum: 3
 Mean: 1.508
 Std Deviation: 0.8559606700477941
round distribution of 100000:
 0: 12.507%
 1: 37.393%
 2: 37.676%
 3: 12.424%

Output Analysis: negative_binomial_variate(3, 0.5)
Typical Timing: 59 ± 4 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 3
 Maximum: 18
 Mean: 3.124
 Std Deviation: 2.5688953313093985
round distribution of 100000:
 0: 12.435%
 1: 18.699%
 2: 18.805%
 3: 15.475%
 4: 11.64%
 5: 8.431%
 6: 5.541%
 7: 3.557%
 8: 2.122%
 9: 1.322%
 10: 0.817%
 11: 0.466%
 12: 0.283%
 13: 0.17%
 14: 0.111%
 15: 0.057%
 16: 0.036%
 17: 0.013%
 18: 0.006%
 19: 0.003%
 20: 0.006%
 21: 0.002%
 22: 0.001%
 23: 0.001%
 24: 0.001%

Output Analysis: geometric_variate(0.5)
Typical Timing: 39 ± 2 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 1
 Maximum: 14
 Mean: 1.037
 Std Deviation: 1.4586839132446614
round distribution of 100000:
 0: 50.261%
 1: 24.922%
 2: 12.371%
 3: 6.242%
 4: 3.077%
 5: 1.617%
 6: 0.76%
 7: 0.375%
 8: 0.196%
 9: 0.098%
 10: 0.037%
 11: 0.019%
 12: 0.01%
 13: 0.009%
 14: 0.002%
 15: 0.002%
 16: 0.001%
 17: 0.001%

Output Analysis: poisson_variate(0.5)
Typical Timing: 38 ± 1 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 0
 Maximum: 3
 Mean: 0.489
 Std Deviation: 0.6973990001178417
round distribution of 100000:
 0: 60.7%
 1: 30.286%
 2: 7.611%
 3: 1.213%
 4: 0.174%
 5: 0.014%
 6: 0.002%

Base Case
Output Analysis: Random.expovariate(2.0)
Typical Timing: 117 ± 13 ns
Statistics of 1000 samples:
 Minimum: 0.0006802151829591538
 Median: (0.33936678821125754, 0.339696765230503)
 Maximum: 4.08440369276551
 Mean: 0.5001046210556279
 Std Deviation: 0.5059074352208294
round distribution of 100000:
 0: 63.16%
 1: 31.755%
 2: 4.375%
 3: 0.628%
 4: 0.075%
 5: 0.006%
 6: 0.001%

Output Analysis: exponential_variate(2.0)
Typical Timing: 30 ± 2 ns
Statistics of 1000 samples:
 Minimum: 0.0006132325505117699
 Median: (0.3479766517283053, 0.35015299013326073)
 Maximum: 3.908207163732649
 Mean: 0.4804002169667088
 Std Deviation: 0.47168459363767273
round distribution of 100000:
 0: 63.163%
 1: 31.93%
 2: 4.211%
 3: 0.604%
 4: 0.083%
 5: 0.009%

Base Case
Output Analysis: Random.gammavariate(1.0, 1.0)
Typical Timing: 158 ± 5 ns
Statistics of 1000 samples:
 Minimum: 0.0002992350042626808
 Median: (0.6963069073183992, 0.6982590355832315)
 Maximum: 6.832947195133163
 Mean: 1.0132289807118353
 Std Deviation: 1.031394116927719
round distribution of 100000:
 0: 39.12%
 1: 38.423%
 2: 14.258%
 3: 5.143%
 4: 1.97%
 5: 0.684%
 6: 0.243%
 7: 0.101%
 8: 0.041%
 9: 0.009%
 10: 0.006%
 11: 0.001%
 12: 0.001%

Output Analysis: gamma_variate(1.0, 1.0)
Typical Timing: 32 ± 3 ns
Statistics of 1000 samples:
 Minimum: 7.65978646399855e-06
 Median: (0.6454285037226131, 0.6472033992817574)
 Maximum: 7.135779804047727
 Mean: 0.965867325780569
 Std Deviation: 0.996313817491875
round distribution of 100000:
 0: 39.67%
 1: 38.079%
 2: 13.913%
 3: 5.351%
 4: 1.89%
 5: 0.685%
 6: 0.252%
 7: 0.106%
 8: 0.039%
 9: 0.007%
 10: 0.006%
 12: 0.001%
 15: 0.001%

Base Case
Output Analysis: Random.weibullvariate(1.0, 1.0)
Typical Timing: 146 ± 5 ns
Statistics of 1000 samples:
 Minimum: 0.0005478984230414248
 Median: (0.6763259114663343, 0.6765154977594444)
 Maximum: 7.9121435757277245
 Mean: 0.9901148746702192
 Std Deviation: 0.9850888526054471
round distribution of 100000:
 0: 39.47%
 1: 38.234%
 2: 14.082%
 3: 5.175%
 4: 1.937%
 5: 0.688%
 6: 0.264%
 7: 0.1%
 8: 0.034%
 9: 0.01%
 10: 0.003%
 11: 0.003%

Output Analysis: weibull_variate(1.0, 1.0)
Typical Timing: 56 ± 1 ns
Statistics of 1000 samples:
 Minimum: 0.0036061453641992552
 Median: (0.7079390283349783, 0.7083196042535354)
 Maximum: 8.130824562482685
 Mean: 1.0366270792836338
 Std Deviation: 1.0519697094518854
round distribution of 100000:
 0: 39.287%
 1: 38.372%
 2: 14.055%
 3: 5.166%
 4: 1.966%
 5: 0.721%
 6: 0.268%
 7: 0.113%
 8: 0.034%
 9: 0.013%
 10: 0.002%
 11: 0.002%
 12: 0.001%

Base Case
Output Analysis: Random.normalvariate(0.0, 1.0)
Typical Timing: 241 ± 7 ns
Statistics of 1000 samples:
 Minimum: -3.0079497786586384
 Median: (-0.009348046621921137, -0.00933763626400204)
 Maximum: 3.344803402450838
 Mean: 0.004280847996984328
 Std Deviation: 0.9885154587390768
round distribution of 100000:
 -5: 0.001%
 -4: 0.028%
 -3: 0.622%
 -2: 5.957%
 -1: 24.164%
 0: 38.052%
 1: 24.457%
 2: 6.057%
 3: 0.637%
 4: 0.025%

Output Analysis: normal_variate(0.0, 1.0)
Typical Timing: 49 ± 8 ns
Statistics of 1000 samples:
 Minimum: -2.8448154339530616
 Median: (-0.014415510583415198, -0.00946149820438376)
 Maximum: 3.2352057138442167
 Mean: 0.03240902799098029
 Std Deviation: 0.984055810917625
round distribution of 100000:
 -5: 0.001%
 -4: 0.03%
 -3: 0.609%
 -2: 5.985%
 -1: 24.224%
 0: 38.626%
 1: 23.88%
 2: 6.028%
 3: 0.593%
 4: 0.024%

Base Case
Output Analysis: Random.lognormvariate(0.0, 1.0)
Typical Timing: 301 ± 10 ns
Statistics of 1000 samples:
 Minimum: 0.029245406870064158
 Median: (0.9216088266366247, 0.9219427208910113)
 Maximum: 37.55003542504999
 Mean: 1.6590786834458462
 Std Deviation: 2.4048231765755275
round distribution of 100000:
 0: 24.45%
 1: 41.386%
 2: 16.266%
 3: 7.301%
 4: 3.982%
 5: 2.229%
 6: 1.341%
 7: 0.878%
 8: 0.593%
 9: 0.393%
 10: 0.297%
 11: 0.188%
 12: 0.139%
 13: 0.113%
 14: 0.085%
 15: 0.067%
 16: 0.048%
 17: 0.061%
 18: 0.034%
 19: 0.028%
 20: 0.021%
 21: 0.017%
 22: 0.013%
 23: 0.012%
 24: 0.012%
 25: 0.004%
 26: 0.006%
 27: 0.003%
 28: 0.004%
 29: 0.003%
 30: 0.002%
 31: 0.002%
 32: 0.001%
 33: 0.004%
 34: 0.001%
 35: 0.004%
 36: 0.004%
 37: 0.003%
 38: 0.001%
 41: 0.001%
 42: 0.001%
 45: 0.001%
 54: 0.001%

Output Analysis: log_normal_variate(0.0, 1.0)
Typical Timing: 65 ± 2 ns
Statistics of 1000 samples:
 Minimum: 0.03375741890309801
 Median: (1.0208234154905305, 1.0208978888304063)
 Maximum: 31.19363664896524
 Mean: 1.6979256215182812
 Std Deviation: 2.345853753996121
round distribution of 100000:
 0: 24.424%
 1: 41.338%
 2: 16.259%
 3: 7.469%
 4: 3.833%
 5: 2.201%
 6: 1.397%
 7: 0.854%
 8: 0.577%
 9: 0.421%
 10: 0.3%
 11: 0.215%
 12: 0.151%
 13: 0.105%
 14: 0.077%
 15: 0.078%
 16: 0.067%
 17: 0.048%
 18: 0.033%
 19: 0.022%
 20: 0.021%
 21: 0.01%
 22: 0.018%
 23: 0.022%
 24: 0.009%
 25: 0.005%
 26: 0.007%
 27: 0.006%
 28: 0.002%
 29: 0.001%
 30: 0.002%
 31: 0.004%
 32: 0.003%
 33: 0.001%
 34: 0.001%
 35: 0.004%
 36: 0.001%
 37: 0.001%
 38: 0.001%
 39: 0.001%
 40: 0.002%
 41: 0.001%
 44: 0.002%
 51: 0.001%
 53: 0.001%
 56: 0.001%
 65: 0.001%
 70: 0.001%
 135: 0.001%

Output Analysis: extreme_value_variate(0.0, 2.0)
Typical Timing: 47 ± 4 ns
Statistics of 1000 samples:
 Minimum: -3.607247003583879
 Median: (0.7079142015831905, 0.7090727371769925)
 Maximum: 14.594277470230296
 Mean: 1.1610199932316434
 Std Deviation: 2.5618687904541306
round distribution of 100000:
 -5: 0.007%
 -4: 0.286%
 -3: 2.714%
 -2: 8.856%
 -1: 15.788%
 0: 18.083%
 1: 16.459%
 2: 12.835%
 3: 9.055%
 4: 5.938%
 5: 3.801%
 6: 2.394%
 7: 1.484%
 8: 0.911%
 9: 0.516%
 10: 0.344%
 11: 0.218%
 12: 0.126%
 13: 0.065%
 14: 0.042%
 15: 0.035%
 16: 0.017%
 17: 0.012%
 18: 0.003%
 19: 0.005%
 20: 0.003%
 21: 0.002%
 22: 0.001%

Output Analysis: chi_squared_variate(5.0)
Typical Timing: 66 ± 4 ns
Statistics of 1000 samples:
 Minimum: 0.2688708925282759
 Median: (4.42019834830797, 4.422624711512022)
 Maximum: 21.833987132187605
 Mean: 5.088284916170664
 Std Deviation: 3.3139912896193797
round distribution of 100000:
 0: 0.779%
 1: 7.906%
 2: 13.709%
 3: 15.312%
 4: 14.273%
 5: 12.14%
 6: 9.738%
 7: 7.35%
 8: 5.559%
 9: 4.139%
 10: 2.897%
 11: 2.038%
 12: 1.418%
 13: 0.899%
 14: 0.604%
 15: 0.414%
 16: 0.296%
 17: 0.187%
 18: 0.11%
 19: 0.062%
 20: 0.061%
 21: 0.036%
 22: 0.031%
 23: 0.015%
 24: 0.01%
 25: 0.005%
 26: 0.004%
 27: 0.002%
 28: 0.002%
 29: 0.002%
 30: 0.001%
 37: 0.001%

Output Analysis: cauchy_variate(0.0, 2.0)
Typical Timing: 38 ± 4 ns
Statistics of 1000 samples:
 Minimum: -574.6782328790307
 Median: (-0.03045391387880989, -0.01952516123001408)
 Maximum: 2615.946142963011
 Mean: 1.9633024776880934
 Std Deviation: 89.95910672362245
round distribution of 100000:
 -200401: 0.001%
 -39630: 0.001%
 -30020: 0.001%
 -19907: 0.001%
 -19665: 0.001%
 -15718: 0.001%
 -14152: 0.001%
 -14039: 0.001%
 -10830: 0.001%
 -10143: 0.001%
 -9693: 0.001%
 -8797: 0.001%
 -8381: 0.001%
 -7156: 0.001%
 -6455: 0.001%
 -6423: 0.001%
 -5492: 0.001%
 -5396: 0.001%
 -5070: 0.001%
 -5032: 0.001%
 -4738: 0.001%
 -4624: 0.001%
 -3800: 0.001%
 -3596: 0.001%
 -3185: 0.001%
 -3073: 0.001%
 -3034: 0.001%
 -2958: 0.001%
 -2904: 0.001%
 -2638: 0.001%
 -2375: 0.001%
 -2372: 0.001%
 -2341: 0.001%
 -2059: 0.001%
 -2022: 0.001%
 -1996: 0.001%
 -1943: 0.001%
 -1909: 0.001%
 -1898: 0.001%
 -1895: 0.001%
 -1887: 0.001%
 -1839: 0.001%
 -1776: 0.001%
 -1747: 0.001%
 -1624: 0.001%
 -1611: 0.001%
 -1590: 0.001%
 -1574: 0.001%
 -1556: 0.001%
 -1541: 0.001%
 -1518: 0.001%
 -1517: 0.001%
 -1479: 0.001%
 -1458: 0.001%
 -1447: 0.001%
 -1397: 0.001%
 -1378: 0.001%
 -1342: 0.001%
 -1322: 0.001%
 -1318: 0.001%
 -1287: 0.001%
 -1277: 0.002%
 -1276: 0.001%
 -1259: 0.001%
 -1195: 0.001%
 -1182: 0.001%
 -1145: 0.001%
 -1110: 0.001%
 -1109: 0.001%
 -1086: 0.001%
 -1079: 0.002%
 -1061: 0.001%
 -1019: 0.001%
 -987: 0.001%
 -968: 0.001%
 -964: 0.001%
 -954: 0.001%
 -952: 0.001%
 -925: 0.001%
 -907: 0.001%
 -900: 0.001%
 -845: 0.001%
 -832: 0.001%
 -826: 0.001%
 -807: 0.001%
 -788: 0.001%
 -785: 0.001%
 -771: 0.001%
 -761: 0.001%
 -760: 0.001%
 -752: 0.002%
 -750: 0.001%
 -715: 0.001%
 -706: 0.001%
 -695: 0.001%
 -692: 0.001%
 -689: 0.001%
 -686: 0.001%
 -684: 0.001%
 -678: 0.001%
 -677: 0.001%
 -669: 0.001%
 -668: 0.001%
 -664: 0.002%
 -663: 0.001%
 -648: 0.001%
 -633: 0.001%
 -607: 0.001%
 -602: 0.001%
 -600: 0.001%
 -596: 0.002%
 -590: 0.001%
 -584: 0.001%
 -575: 0.002%
 -570: 0.001%
 -566: 0.001%
 -563: 0.001%
 -562: 0.001%
 -560: 0.001%
 -543: 0.002%
 -540: 0.001%
 -533: 0.001%
 -532: 0.001%
 -530: 0.001%
 -529: 0.001%
 -524: 0.001%
 -510: 0.001%
 -494: 0.001%
 -492: 0.002%
 -491: 0.001%
 -489: 0.002%
 -487: 0.001%
 -486: 0.001%
 -478: 0.001%
 -474: 0.001%
 -473: 0.002%
 -468: 0.001%
 -463: 0.001%
 -461: 0.002%
 -458: 0.001%
 -457: 0.002%
 -454: 0.002%
 -452: 0.002%
 -451: 0.001%
 -448: 0.001%
 -444: 0.001%
 -441: 0.001%
 -436: 0.001%
 -434: 0.001%
 -433: 0.002%
 -431: 0.001%
 -427: 0.001%
 -423: 0.002%
 -419: 0.002%
 -418: 0.001%
 -417: 0.001%
 -416: 0.001%
 -415: 0.001%
 -408: 0.001%
 -407: 0.001%
 -406: 0.001%
 -402: 0.001%
 -400: 0.001%
 -395: 0.002%
 -394: 0.001%
 -392: 0.003%
 -389: 0.001%
 -387: 0.001%
 -385: 0.001%
 -384: 0.001%
 -383: 0.002%
 -378: 0.002%
 -377: 0.002%
 -375: 0.001%
 -372: 0.001%
 -371: 0.001%
 -369: 0.001%
 -367: 0.001%
 -361: 0.001%
 -359: 0.001%
 -357: 0.001%
 -356: 0.001%
 -352: 0.001%
 -348: 0.001%
 -346: 0.001%
 -345: 0.001%
 -344: 0.001%
 -341: 0.002%
 -339: 0.001%
 -337: 0.001%
 -336: 0.001%
 -335: 0.001%
 -331: 0.001%
 -328: 0.001%
 -326: 0.001%
 -324: 0.003%
 -323: 0.001%
 -322: 0.001%
 -320: 0.001%
 -317: 0.001%
 -315: 0.002%
 -303: 0.001%
 -301: 0.001%
 -300: 0.001%
 -298: 0.001%
 -296: 0.001%
 -289: 0.001%
 -288: 0.001%
 -287: 0.001%
 -286: 0.001%
 -285: 0.001%
 -283: 0.001%
 -281: 0.001%
 -279: 0.001%
 -278: 0.002%
 -277: 0.001%
 -276: 0.002%
 -273: 0.003%
 -271: 0.001%
 -269: 0.001%
 -267: 0.001%
 -266: 0.001%
 -265: 0.001%
 -262: 0.002%
 -261: 0.002%
 -260: 0.001%
 -259: 0.001%
 -258: 0.001%
 -257: 0.002%
 -256: 0.002%
 -253: 0.001%
 -249: 0.002%
 -248: 0.002%
 -246: 0.001%
 -244: 0.002%
 -242: 0.001%
 -240: 0.002%
 -239: 0.002%
 -238: 0.001%
 -237: 0.002%
 -236: 0.002%
 -235: 0.001%
 -234: 0.001%
 -233: 0.001%
 -232: 0.003%
 -231: 0.001%
 -230: 0.001%
 -229: 0.003%
 -228: 0.001%
 -227: 0.001%
 -226: 0.002%
 -225: 0.002%
 -223: 0.003%
 -221: 0.002%
 -220: 0.002%
 -218: 0.002%
 -217: 0.003%
 -216: 0.002%
 -215: 0.002%
 -214: 0.002%
 -213: 0.001%
 -211: 0.003%
 -210: 0.002%
 -209: 0.002%
 -207: 0.001%
 -206: 0.001%
 -205: 0.004%
 -204: 0.001%
 -203: 0.004%
 -201: 0.003%
 -200: 0.002%
 -199: 0.004%
 -197: 0.001%
 -196: 0.002%
 -195: 0.002%
 -194: 0.003%
 -193: 0.002%
 -192: 0.002%
 -191: 0.004%
 -190: 0.003%
 -189: 0.002%
 -188: 0.002%
 -187: 0.002%
 -186: 0.001%
 -185: 0.004%
 -183: 0.004%
 -182: 0.002%
 -181: 0.003%
 -180: 0.003%
 -179: 0.001%
 -178: 0.003%
 -177: 0.001%
 -176: 0.001%
 -175: 0.002%
 -174: 0.001%
 -173: 0.003%
 -171: 0.001%
 -170: 0.002%
 -169: 0.001%
 -167: 0.002%
 -166: 0.005%
 -165: 0.005%
 -164: 0.003%
 -163: 0.003%
 -162: 0.002%
 -160: 0.002%
 -158: 0.003%
 -157: 0.004%
 -156: 0.003%
 -155: 0.001%
 -154: 0.001%
 -153: 0.007%
 -152: 0.004%
 -151: 0.001%
 -150: 0.002%
 -148: 0.003%
 -147: 0.002%
 -146: 0.002%
 -145: 0.003%
 -144: 0.001%
 -143: 0.004%
 -142: 0.003%
 -141: 0.002%
 -140: 0.003%
 -139: 0.001%
 -138: 0.001%
 -137: 0.004%
 -136: 0.004%
 -135: 0.005%
 -134: 0.004%
 -133: 0.003%
 -132: 0.004%
 -131: 0.002%
 -130: 0.003%
 -129: 0.006%
 -128: 0.004%
 -127: 0.008%
 -126: 0.004%
 -125: 0.005%
 -124: 0.007%
 -122: 0.002%
 -121: 0.003%
 -120: 0.004%
 -119: 0.002%
 -118: 0.002%
 -117: 0.007%
 -116: 0.007%
 -115: 0.003%
 -114: 0.001%
 -113: 0.004%
 -112: 0.002%
 -111: 0.005%
 -110: 0.002%
 -109: 0.006%
 -108: 0.008%
 -107: 0.004%
 -106: 0.002%
 -105: 0.009%
 -104: 0.005%
 -103: 0.005%
 -102: 0.007%
 -101: 0.006%
 -100: 0.008%
 -99: 0.004%
 -98: 0.004%
 -97: 0.007%
 -96: 0.004%
 -95: 0.002%
 -94: 0.005%
 -93: 0.008%
 -92: 0.009%
 -91: 0.006%
 -90: 0.008%
 -89: 0.013%
 -88: 0.003%
 -87: 0.004%
 -86: 0.006%
 -85: 0.004%
 -84: 0.007%
 -83: 0.008%
 -82: 0.009%
 -81: 0.01%
 -80: 0.009%
 -79: 0.012%
 -78: 0.01%
 -77: 0.011%
 -76: 0.013%
 -75: 0.015%
 -74: 0.012%
 -73: 0.016%
 -72: 0.012%
 -71: 0.007%
 -70: 0.007%
 -69: 0.009%
 -68: 0.011%
 -67: 0.013%
 -66: 0.016%
 -65: 0.016%
 -64: 0.013%
 -63: 0.02%
 -62: 0.014%
 -61: 0.013%
 -60: 0.016%
 -59: 0.02%
 -58: 0.024%
 -57: 0.017%
 -56: 0.02%
 -55: 0.022%
 -54: 0.022%
 -53: 0.022%
 -52: 0.022%
 -51: 0.03%
 -50: 0.023%
 -49: 0.028%
 -48: 0.027%
 -47: 0.034%
 -46: 0.037%
 -45: 0.026%
 -44: 0.023%
 -43: 0.034%
 -42: 0.037%
 -41: 0.04%
 -40: 0.042%
 -39: 0.045%
 -38: 0.051%
 -37: 0.05%
 -36: 0.061%
 -35: 0.053%
 -34: 0.056%
 -33: 0.047%
 -32: 0.052%
 -31: 0.064%
 -30: 0.093%
 -29: 0.087%
 -28: 0.068%
 -27: 0.082%
 -26: 0.103%
 -25: 0.098%
 -24: 0.13%
 -23: 0.131%
 -22: 0.137%
 -21: 0.14%
 -20: 0.164%
 -19: 0.167%
 -18: 0.19%
 -17: 0.205%
 -16: 0.247%
 -15: 0.287%
 -14: 0.334%
 -13: 0.378%
 -12: 0.429%
 -11: 0.458%
 -10: 0.627%
 -9: 0.75%
 -8: 0.888%
 -7: 1.172%
 -6: 1.628%
 -5: 2.196%
 -4: 3.253%
 -3: 4.813%
 -2: 8.126%
 -1: 12.839%
 0: 15.56%
 1: 12.548%
 2: 8.045%
 3: 4.894%
 4: 3.291%
 5: 2.258%
 6: 1.621%
 7: 1.238%
 8: 0.986%
 9: 0.749%
 10: 0.617%
 11: 0.521%
 12: 0.417%
 13: 0.34%
 14: 0.31%
 15: 0.24%
 16: 0.22%
 17: 0.236%
 18: 0.199%
 19: 0.185%
 20: 0.16%
 21: 0.157%
 22: 0.141%
 23: 0.105%
 24: 0.105%
 25: 0.105%
 26: 0.111%
 27: 0.09%
 28: 0.066%
 29: 0.065%
 30: 0.078%
 31: 0.062%
 32: 0.064%
 33: 0.049%
 34: 0.057%
 35: 0.04%
 36: 0.033%
 37: 0.057%
 38: 0.042%
 39: 0.05%
 40: 0.033%
 41: 0.058%
 42: 0.043%
 43: 0.039%
 44: 0.037%
 45: 0.028%
 46: 0.022%
 47: 0.021%
 48: 0.031%
 49: 0.018%
 50: 0.028%
 51: 0.027%
 52: 0.023%
 53: 0.019%
 54: 0.016%
 55: 0.017%
 56: 0.018%
 57: 0.023%
 58: 0.014%
 59: 0.016%
 60: 0.025%
 61: 0.014%
 62: 0.013%
 63: 0.012%
 64: 0.016%
 65: 0.014%
 66: 0.019%
 67: 0.02%
 68: 0.012%
 69: 0.02%
 70: 0.009%
 71: 0.014%
 72: 0.012%
 73: 0.013%
 74: 0.014%
 75: 0.011%
 76: 0.01%
 77: 0.013%
 78: 0.019%
 79: 0.019%
 80: 0.009%
 81: 0.014%
 82: 0.016%
 83: 0.011%
 84: 0.003%
 85: 0.01%
 86: 0.006%
 87: 0.013%
 88: 0.004%
 89: 0.009%
 90: 0.009%
 91: 0.008%
 92: 0.008%
 93: 0.015%
 94: 0.005%
 95: 0.004%
 96: 0.006%
 97: 0.009%
 98: 0.009%
 99: 0.007%
 100: 0.01%
 101: 0.003%
 102: 0.003%
 103: 0.004%
 104: 0.005%
 105: 0.005%
 106: 0.003%
 107: 0.009%
 108: 0.005%
 109: 0.006%
 110: 0.007%
 111: 0.001%
 112: 0.007%
 113: 0.004%
 114: 0.007%
 115: 0.005%
 116: 0.004%
 117: 0.009%
 118: 0.004%
 119: 0.003%
 120: 0.006%
 121: 0.005%
 122: 0.004%
 123: 0.002%
 124: 0.005%
 125: 0.002%
 126: 0.001%
 127: 0.002%
 128: 0.003%
 129: 0.003%
 130: 0.001%
 131: 0.003%
 132: 0.001%
 133: 0.003%
 134: 0.003%
 135: 0.001%
 136: 0.001%
 137: 0.002%
 138: 0.002%
 139: 0.002%
 140: 0.001%
 141: 0.002%
 142: 0.002%
 143: 0.004%
 144: 0.007%
 145: 0.002%
 146: 0.003%
 147: 0.005%
 150: 0.005%
 151: 0.002%
 152: 0.003%
 153: 0.003%
 154: 0.002%
 155: 0.002%
 157: 0.003%
 158: 0.002%
 159: 0.003%
 161: 0.002%
 162: 0.001%
 163: 0.001%
 164: 0.003%
 165: 0.003%
 166: 0.001%
 167: 0.007%
 168: 0.004%
 169: 0.002%
 170: 0.001%
 171: 0.003%
 172: 0.001%
 173: 0.004%
 174: 0.007%
 175: 0.001%
 176: 0.001%
 177: 0.001%
 179: 0.003%
 180: 0.003%
 181: 0.001%
 183: 0.002%
 184: 0.001%
 185: 0.005%
 187: 0.001%
 188: 0.001%
 189: 0.001%
 190: 0.001%
 192: 0.002%
 194: 0.001%
 195: 0.001%
 196: 0.003%
 197: 0.002%
 198: 0.004%
 199: 0.001%
 200: 0.004%
 201: 0.003%
 202: 0.004%
 203: 0.001%
 205: 0.001%
 208: 0.003%
 209: 0.002%
 210: 0.001%
 211: 0.001%
 212: 0.002%
 213: 0.003%
 214: 0.005%
 215: 0.001%
 216: 0.001%
 217: 0.004%
 218: 0.001%
 219: 0.001%
 220: 0.001%
 221: 0.001%
 222: 0.001%
 225: 0.002%
 226: 0.001%
 228: 0.001%
 229: 0.001%
 231: 0.001%
 233: 0.001%
 236: 0.002%
 237: 0.001%
 238: 0.002%
 240: 0.004%
 242: 0.001%
 248: 0.002%
 249: 0.001%
 251: 0.001%
 252: 0.002%
 253: 0.002%
 254: 0.001%
 255: 0.002%
 256: 0.001%
 260: 0.001%
 261: 0.001%
 264: 0.001%
 265: 0.002%
 266: 0.001%
 267: 0.002%
 270: 0.001%
 271: 0.001%
 273: 0.001%
 274: 0.001%
 275: 0.003%
 276: 0.002%
 282: 0.001%
 283: 0.001%
 287: 0.001%
 290: 0.001%
 292: 0.001%
 293: 0.001%
 295: 0.001%
 296: 0.001%
 299: 0.001%
 301: 0.001%
 304: 0.001%
 306: 0.001%
 308: 0.001%
 309: 0.001%
 310: 0.002%
 311: 0.001%
 315: 0.001%
 316: 0.001%
 317: 0.002%
 318: 0.001%
 320: 0.001%
 322: 0.002%
 323: 0.001%
 325: 0.001%
 328: 0.001%
 329: 0.001%
 330: 0.001%
 332: 0.002%
 334: 0.001%
 337: 0.002%
 339: 0.002%
 343: 0.001%
 345: 0.001%
 346: 0.001%
 349: 0.001%
 350: 0.001%
 351: 0.001%
 352: 0.001%
 353: 0.001%
 358: 0.002%
 362: 0.001%
 363: 0.001%
 364: 0.001%
 367: 0.001%
 368: 0.001%
 372: 0.001%
 373: 0.001%
 378: 0.001%
 381: 0.002%
 387: 0.001%
 389: 0.001%
 390: 0.002%
 391: 0.001%
 392: 0.001%
 393: 0.001%
 396: 0.001%
 397: 0.001%
 402: 0.003%
 404: 0.002%
 405: 0.002%
 407: 0.001%
 412: 0.003%
 417: 0.001%
 419: 0.001%
 429: 0.001%
 433: 0.001%
 437: 0.001%
 439: 0.002%
 442: 0.001%
 443: 0.001%
 445: 0.001%
 446: 0.001%
 447: 0.001%
 448: 0.001%
 449: 0.001%
 461: 0.001%
 464: 0.001%
 465: 0.001%
 467: 0.004%
 469: 0.001%
 476: 0.001%
 477: 0.002%
 479: 0.001%
 480: 0.001%
 486: 0.001%
 491: 0.001%
 492: 0.001%
 494: 0.002%
 497: 0.001%
 501: 0.001%
 505: 0.001%
 509: 0.001%
 512: 0.001%
 524: 0.002%
 532: 0.001%
 536: 0.001%
 541: 0.001%
 544: 0.001%
 545: 0.001%
 546: 0.001%
 548: 0.001%
 551: 0.001%
 553: 0.001%
 560: 0.001%
 562: 0.001%
 574: 0.001%
 580: 0.002%
 584: 0.001%
 587: 0.002%
 588: 0.001%
 589: 0.001%
 590: 0.001%
 595: 0.001%
 599: 0.001%
 604: 0.002%
 617: 0.001%
 621: 0.001%
 622: 0.001%
 625: 0.001%
 631: 0.001%
 643: 0.001%
 665: 0.001%
 671: 0.001%
 672: 0.001%
 673: 0.001%
 680: 0.002%
 688: 0.001%
 698: 0.001%
 700: 0.001%
 704: 0.001%
 706: 0.001%
 708: 0.001%
 733: 0.001%
 735: 0.001%
 750: 0.001%
 759: 0.001%
 792: 0.001%
 817: 0.001%
 821: 0.001%
 833: 0.001%
 835: 0.002%
 845: 0.002%
 874: 0.001%
 885: 0.001%
 923: 0.001%
 934: 0.001%
 959: 0.001%
 961: 0.001%
 966: 0.001%
 969: 0.001%
 976: 0.001%
 1033: 0.001%
 1041: 0.001%
 1065: 0.001%
 1075: 0.001%
 1076: 0.001%
 1083: 0.001%
 1134: 0.001%
 1136: 0.001%
 1138: 0.001%
 1143: 0.001%
 1229: 0.001%
 1253: 0.001%
 1309: 0.001%
 1336: 0.002%
 1393: 0.001%
 1414: 0.001%
 1441: 0.001%
 1459: 0.001%
 1571: 0.001%
 1777: 0.001%
 1794: 0.001%
 1820: 0.001%
 1859: 0.001%
 1875: 0.001%
 1899: 0.001%
 1915: 0.001%
 1936: 0.001%
 1977: 0.001%
 1980: 0.001%
 2041: 0.001%
 2125: 0.001%
 2144: 0.001%
 2302: 0.001%
 2360: 0.001%
 2395: 0.001%
 2564: 0.001%
 2598: 0.001%
 2616: 0.001%
 2658: 0.001%
 2797: 0.001%
 3110: 0.001%
 3215: 0.001%
 3280: 0.001%
 4106: 0.001%
 5217: 0.001%
 5756: 0.001%
 6046: 0.001%
 7834: 0.001%
 8431: 0.001%
 12077: 0.001%
 12767: 0.001%
 13679: 0.001%
 15871: 0.001%
 185084: 0.001%

Output Analysis: fisher_f_variate(2.0, 3.0)
Typical Timing: 83 ± 5 ns
Statistics of 1000 samples:
 Minimum: 0.0013000850258821752
 Median: (0.9461138466131122, 0.9466925601274419)
 Maximum: 145.42598026292492
 Mean: 2.6054292265173045
 Std Deviation: 6.956840435561045
round distribution of 100000:
 0: 35.219%
 1: 29.492%
 2: 12.224%
 3: 6.477%
 4: 3.977%
 5: 2.567%
 6: 1.822%
 7: 1.317%
 8: 1.013%
 9: 0.759%
 10: 0.624%
 11: 0.538%
 12: 0.432%
 13: 0.333%
 14: 0.278%
 15: 0.246%
 16: 0.223%
 17: 0.192%
 18: 0.169%
 19: 0.159%
 20: 0.147%
 21: 0.135%
 22: 0.094%
 23: 0.077%
 24: 0.078%
 25: 0.076%
 26: 0.059%
 27: 0.076%
 28: 0.061%
 29: 0.063%
 30: 0.05%
 31: 0.051%
 32: 0.046%
 33: 0.038%
 34: 0.032%
 35: 0.038%
 36: 0.033%
 37: 0.03%
 38: 0.029%
 39: 0.034%
 40: 0.03%
 41: 0.024%
 42: 0.027%
 43: 0.019%
 44: 0.025%
 45: 0.017%
 46: 0.022%
 47: 0.019%
 48: 0.017%
 49: 0.015%
 50: 0.012%
 51: 0.017%
 52: 0.012%
 53: 0.008%
 54: 0.011%
 55: 0.009%
 56: 0.015%
 57: 0.011%
 58: 0.007%
 59: 0.01%
 60: 0.014%
 61: 0.011%
 62: 0.008%
 63: 0.01%
 64: 0.011%
 65: 0.004%
 66: 0.009%
 67: 0.008%
 68: 0.003%
 69: 0.004%
 70: 0.004%
 71: 0.009%
 72: 0.002%
 73: 0.005%
 74: 0.005%
 75: 0.007%
 76: 0.005%
 77: 0.003%
 78: 0.003%
 79: 0.006%
 80: 0.008%
 81: 0.006%
 82: 0.004%
 83: 0.003%
 84: 0.007%
 85: 0.002%
 86: 0.004%
 87: 0.003%
 88: 0.001%
 89: 0.002%
 90: 0.002%
 91: 0.002%
 92: 0.001%
 93: 0.001%
 94: 0.002%
 95: 0.001%
 96: 0.002%
 97: 0.001%
 98: 0.003%
 99: 0.004%
 100: 0.003%
 101: 0.001%
 102: 0.003%
 104: 0.002%
 105: 0.002%
 106: 0.002%
 107: 0.003%
 108: 0.001%
 109: 0.002%
 110: 0.004%
 111: 0.002%
 112: 0.001%
 113: 0.002%
 114: 0.001%
 115: 0.002%
 116: 0.002%
 117: 0.002%
 119: 0.002%
 120: 0.004%
 121: 0.004%
 123: 0.002%
 125: 0.001%
 126: 0.002%
 128: 0.001%
 129: 0.002%
 130: 0.003%
 133: 0.001%
 134: 0.002%
 136: 0.002%
 137: 0.002%
 138: 0.001%
 139: 0.001%
 140: 0.002%
 142: 0.001%
 143: 0.001%
 145: 0.002%
 146: 0.001%
 147: 0.001%
 148: 0.002%
 150: 0.002%
 153: 0.002%
 154: 0.001%
 155: 0.001%
 157: 0.001%
 159: 0.001%
 160: 0.001%
 161: 0.001%
 162: 0.001%
 163: 0.002%
 166: 0.001%
 170: 0.001%
 172: 0.002%
 174: 0.002%
 175: 0.001%
 176: 0.002%
 178: 0.001%
 179: 0.002%
 182: 0.002%
 185: 0.001%
 186: 0.001%
 187: 0.001%
 189: 0.001%
 190: 0.001%
 191: 0.001%
 192: 0.002%
 195: 0.001%
 197: 0.002%
 198: 0.002%
 199: 0.001%
 200: 0.001%
 202: 0.001%
 203: 0.001%
 207: 0.001%
 210: 0.001%
 212: 0.001%
 213: 0.001%
 216: 0.001%
 218: 0.001%
 219: 0.001%
 225: 0.002%
 231: 0.001%
 233: 0.001%
 234: 0.002%
 237: 0.001%
 239: 0.001%
 244: 0.001%
 248: 0.001%
 257: 0.001%
 259: 0.001%
 262: 0.001%
 266: 0.001%
 267: 0.001%
 268: 0.001%
 270: 0.002%
 282: 0.001%
 286: 0.001%
 294: 0.002%
 298: 0.001%
 301: 0.001%
 306: 0.001%
 308: 0.001%
 311: 0.001%
 314: 0.001%
 327: 0.001%
 333: 0.001%
 348: 0.001%
 353: 0.001%
 359: 0.001%
 361: 0.001%
 362: 0.001%
 372: 0.001%
 392: 0.001%
 416: 0.001%
 443: 0.001%
 475: 0.001%
 477: 0.001%
 483: 0.001%
 555: 0.001%
 572: 0.001%
 784: 0.001%
 843: 0.001%
 1230: 0.001%
 1348: 0.001%
 1816: 0.001%

Output Analysis: student_t_variate(5.0)
Typical Timing: 89 ± 5 ns
Statistics of 1000 samples:
 Minimum: -5.694177355781756
 Median: (0.03401124714582299, 0.03632195884219656)
 Maximum: 4.825772901223067
 Mean: 0.03194322255526041
 Std Deviation: 1.3121991163775202
round distribution of 100000:
 -18: 0.001%
 -14: 0.001%
 -13: 0.001%
 -12: 0.002%
 -11: 0.004%
 -10: 0.002%
 -9: 0.004%
 -8: 0.014%
 -7: 0.027%
 -6: 0.071%
 -5: 0.188%
 -4: 0.552%
 -3: 1.838%
 -2: 6.972%
 -1: 22.445%
 0: 35.754%
 1: 22.252%
 2: 7.162%
 3: 1.85%
 4: 0.553%
 5: 0.185%
 6: 0.069%
 7: 0.023%
 8: 0.014%
 9: 0.003%
 10: 0.005%
 11: 0.004%
 12: 0.001%
 13: 0.001%
 14: 0.001%
 32: 0.001%


Random Booleans:

Output Analysis: percent_true(33.33)
Typical Timing: 22 ± 2 ns
Statistics of 1000 samples:
 Minimum: False
 Median: False
 Maximum: True
 Mean: 0.342
 Std Deviation: 0.47461696267754827
Distribution of 100000 samples:
 False: 66.638%
 True: 33.362%


Shuffle Performance:

some_small_list = [i for i in range(10)]
some_med_list = [i for i in range(100)]
some_large_list = [i for i in range(1000)]

Base Case:
Random.shuffle()  # fisher_yates in python
Typical Timing: 1404 ± 41 ns
Typical Timing: 12436 ± 115 ns
Typical Timing: 137094 ± 891 ns

Fortuna.shuffle()  # knuth_b in cython
Typical Timing: 225 ± 5 ns
Typical Timing: 1916 ± 23 ns
Typical Timing: 18061 ± 84 ns

Fortuna.knuth_a()  # knuth_a in cython
Typical Timing: 432 ± 10 ns
Typical Timing: 3501 ± 25 ns
Typical Timing: 41323 ± 353 ns

Fortuna.fisher_yates()  # fisher_yates in cython
Typical Timing: 457 ± 11 ns
Typical Timing: 3751 ± 90 ns
Typical Timing: 42354 ± 890 ns

smart_clamp(3, 2, 1) # should be 2:  2
Typical Timing: 40 ± 4 ns
float_clamp(3.0, 2.0, 1.0) # should be 2.0:  2.0
Typical Timing: 39 ± 3 ns


-------------------------------------------------------------------------
Total Test Time: 3.658 seconds
```


## Legal Information
Fortuna is licensed under a Creative Commons Attribution-NonCommercial 3.0 Unported License. 
See online version of this license here: <http://creativecommons.org/licenses/by-nc/3.0/>

Other licensing options are available, please contact the author for details: [Robert Sharp](mailto:webmaster@sharpdesigndigital.com)
