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
- Installation requires C++20 Compiler and C++20 Standard Library.
- New in version 5, Fortuna now supports Windows.
  - Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/
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

##### Fortuna 5.6.0
- Storm Update 4.0.4
- Minor bug fixes

##### Fortuna 5.5.7
- Storm Update 4.0.3

##### Fortuna 5.5.6
- Performance test update
- Documentation update

##### Fortuna 5.5.5
- All platforms now require C++20

##### Fortuna 5.5.4
- Bug fixes

##### Fortuna 5.5.3
- Bug fixes

##### Fortuna 5.5.2
- Bug fixes

##### Fortuna 5.5.1
- Bug fixes

##### Fortuna 5.5.0
- Bug fixes

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
- Hardware: Mac Studio: M1 Ultra
- Software: macOS 14.5, Python 3.11.3

```
MonkeyScope: Fortuna Quick Test
Fortuna Version: 5.6.0
Storm Version: 4.0.4

Smart Clamp: Pass
Float Clamp: Pass

Data:
some_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

Base Case
Output Analysis: Random.choice(some_list)
Typical Timing: 194 ± 17 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 4
 Maximum: 9
 Mean: 4.479
 Std Deviation: 2.886848262879934
Distribution of 10000 samples:
 0: 10.08%
 1: 9.8%
 2: 9.79%
 3: 9.98%
 4: 9.82%
 5: 9.75%
 6: 10.14%
 7: 10.17%
 8: 10.37%
 9: 10.1%

Output Analysis: random_value(some_list)
Typical Timing: 38 ± 3 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 4
 Maximum: 9
 Mean: 4.382
 Std Deviation: 2.8845097324149207
Distribution of 10000 samples:
 0: 10.17%
 1: 9.84%
 2: 10.5%
 3: 10.08%
 4: 9.86%
 5: 9.58%
 6: 9.74%
 7: 9.81%
 8: 9.84%
 9: 10.58%


Wide Distribution
Truffle = TruffleShuffle(some_list)
Output Analysis: Truffle()
Typical Timing: 215 ± 18 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 5
 Maximum: 9
 Mean: 4.559
 Std Deviation: 2.8818091234194925
Distribution of 10000 samples:
 0: 9.83%
 1: 9.71%
 2: 10.09%
 3: 10.2%
 4: 9.82%
 5: 10.34%
 6: 9.82%
 7: 10.17%
 8: 9.89%
 9: 10.13%

truffle = truffle_shuffle(some_list)
Output Analysis: truffle()
Typical Timing: 72 ± 6 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 4
 Maximum: 9
 Mean: 4.487
 Std Deviation: 2.843574672294877
Distribution of 10000 samples:
 0: 10.07%
 1: 9.91%
 2: 10.18%
 3: 10.43%
 4: 9.9%
 5: 10.03%
 6: 9.56%
 7: 10.03%
 8: 9.98%
 9: 9.91%


QuantumMonty
some_tuple = tuple(i for i in range(10))

monty = QuantumMonty(some_tuple)
Output Analysis: monty()
Typical Timing: 259 ± 17 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 4
 Maximum: 9
 Mean: 4.558
 Std Deviation: 2.8274777860543185
Distribution of 10000 samples:
 0: 10.89%
 1: 9.06%
 2: 9.4%
 3: 9.18%
 4: 11.74%
 5: 11.18%
 6: 9.49%
 7: 9.1%
 8: 9.08%
 9: 10.88%

rand_value = <Fortuna.RandomValue object at 0x101b01640>
Output Analysis: rand_value()
Typical Timing: 188 ± 11 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 4
 Maximum: 9
 Mean: 4.351
 Std Deviation: 2.912435626976377
Distribution of 10000 samples:
 0: 9.71%
 1: 9.13%
 2: 10.21%
 3: 10.34%
 4: 9.97%
 5: 10.06%
 6: 10.3%
 7: 10.4%
 8: 9.93%
 9: 9.95%


Weighted Tables:
population = ('A', 'B', 'C', 'D')
cum_weights = (1, 3, 6, 10)
rel_weights = (1, 2, 3, 4)
cum_weighted_table = zip(cum_weights, population)
rel_weighted_table = zip(rel_weights, population)

Cumulative Base Case
Output Analysis: Random.choices(population, cum_weights=cum_weights)
Typical Timing: 569 ± 21 ns
Distribution of 10000 samples:
 A: 9.86%
 B: 20.53%
 C: 30.26%
 D: 39.35%

cum_weighted_choice = CumulativeWeightedChoice(cum_weighted_table)
Output Analysis: cum_weighted_choice()
Typical Timing: 192 ± 8 ns
Distribution of 10000 samples:
 A: 9.53%
 B: 21.06%
 C: 30.01%
 D: 39.4%

Output Analysis: cumulative_weighted_choice(tuple(zip(cum_weights, population)))
Typical Timing: 79 ± 5 ns
Distribution of 10000 samples:
 A: 10.16%
 B: 19.89%
 C: 29.72%
 D: 40.23%

Relative Base Case
Output Analysis: Random.choices(population, weights=rel_weights)
Typical Timing: 705 ± 30 ns
Distribution of 10000 samples:
 A: 9.67%
 B: 20.82%
 C: 29.38%
 D: 40.13%

rel_weighted_choice = RelativeWeightedChoice(rel_weighted_table)
Output Analysis: rel_weighted_choice()
Typical Timing: 194 ± 10 ns
Distribution of 10000 samples:
 A: 9.71%
 B: 19.71%
 C: 30.45%
 D: 40.13%


Random Matrix Values:
some_matrix = {'A': (1, 2, 3, 4), 'B': (10, 20, 30, 40), 'C': (100, 200, 300, 400)}

flex_cat = FlexCat(some_matrix)
Output Analysis: flex_cat()
Typical Timing: 416 ± 24 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 4
 Maximum: 400
 Mean: 35.549
 Std Deviation: 82.61531873623613
Distribution of 10000 samples:
 1: 13.92%
 2: 13.72%
 3: 14.44%
 4: 14.01%
 10: 8.4%
 20: 8.21%
 30: 8.24%
 40: 8.35%
 100: 2.77%
 200: 2.64%
 300: 2.65%
 400: 2.65%

Output Analysis: flex_cat("C")
Typical Timing: 249 ± 5 ns
Statistics of 1000 samples:
 Minimum: 100
 Median: 300
 Maximum: 400
 Mean: 249.8
 Std Deviation: 111.2309863856845
Distribution of 10000 samples:
 100: 25.22%
 200: 24.76%
 300: 24.86%
 400: 25.16%


Random Integers:
Base Case
Output Analysis: Random.randrange(10)
Typical Timing: 162 ± 5 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 5
 Maximum: 9
 Mean: 4.659
 Std Deviation: 2.8395037914716337
Distribution of 10000 samples:
 0: 9.99%
 1: 10.25%
 2: 10.13%
 3: 9.78%
 4: 9.46%
 5: 10.2%
 6: 9.69%
 7: 10.54%
 8: 10.31%
 9: 9.65%

Output Analysis: random_below(10)
Typical Timing: 35 ± 1 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 4
 Maximum: 9
 Mean: 4.446
 Std Deviation: 2.905774858368681
Distribution of 10000 samples:
 0: 10.06%
 1: 10.36%
 2: 10.49%
 3: 9.79%
 4: 9.84%
 5: 9.66%
 6: 10.38%
 7: 9.91%
 8: 9.42%
 9: 10.09%

Output Analysis: random_index(10)
Typical Timing: 34 ± 1 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 5
 Maximum: 9
 Mean: 4.585
 Std Deviation: 2.859537017062719
Distribution of 10000 samples:
 0: 10.03%
 1: 10.52%
 2: 9.3%
 3: 9.85%
 4: 10.04%
 5: 9.77%
 6: 10.01%
 7: 10.09%
 8: 10.0%
 9: 10.39%

Output Analysis: random_range(10)
Typical Timing: 45 ± 2 ns
Statistics of 1000 samples:
 Minimum: 0
 Median: 4
 Maximum: 9
 Mean: 4.476
 Std Deviation: 2.9455220420326342
Distribution of 10000 samples:
 0: 10.28%
 1: 10.11%
 2: 10.27%
 3: 9.95%
 4: 9.21%
 5: 9.98%
 6: 9.76%
 7: 10.38%
 8: 9.6%
 9: 10.46%

Output Analysis: random_below(-10)
Typical Timing: 43 ± 1 ns
Statistics of 1000 samples:
 Minimum: -9
 Median: -4
 Maximum: 0
 Mean: -4.361
 Std Deviation: 2.8766219692469073
Distribution of 10000 samples:
 -9: 9.98%
 -8: 9.5%
 -7: 10.08%
 -6: 10.25%
 -5: 10.3%
 -4: 10.15%
 -3: 10.16%
 -2: 10.25%
 -1: 9.51%
 0: 9.82%

Output Analysis: random_index(-10)
Typical Timing: 44 ± 1 ns
Statistics of 1000 samples:
 Minimum: -10
 Median: -6
 Maximum: -1
 Mean: -5.606
 Std Deviation: 2.9067530361579075
Distribution of 10000 samples:
 -10: 10.35%
 -9: 9.9%
 -8: 9.44%
 -7: 10.39%
 -6: 10.63%
 -5: 10.08%
 -4: 9.82%
 -3: 9.72%
 -2: 10.44%
 -1: 9.23%

Output Analysis: random_range(-10)
Typical Timing: 52 ± 1 ns
Statistics of 1000 samples:
 Minimum: -10
 Median: -5
 Maximum: -1
 Mean: -5.444
 Std Deviation: 2.8637501750440917
Distribution of 10000 samples:
 -10: 9.82%
 -9: 9.5%
 -8: 9.89%
 -7: 10.63%
 -6: 9.85%
 -5: 9.94%
 -4: 9.95%
 -3: 10.0%
 -2: 10.38%
 -1: 10.04%

Base Case
Output Analysis: Random.randrange(1, 10)
Typical Timing: 189 ± 3 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 5
 Maximum: 9
 Mean: 5.035
 Std Deviation: 2.613925708127071
Distribution of 10000 samples:
 1: 11.48%
 2: 11.04%
 3: 11.06%
 4: 10.97%
 5: 10.62%
 6: 11.68%
 7: 10.79%
 8: 11.0%
 9: 11.36%

Output Analysis: random_range(1, 10)
Typical Timing: 45 ± 1 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 5
 Maximum: 9
 Mean: 5.137
 Std Deviation: 2.538636578101654
Distribution of 10000 samples:
 1: 10.49%
 2: 10.84%
 3: 10.82%
 4: 10.65%
 5: 11.49%
 6: 11.56%
 7: 11.36%
 8: 11.13%
 9: 11.66%

Output Analysis: random_range(10, 1)
Typical Timing: 46 ± 2 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 5
 Maximum: 9
 Mean: 5.049
 Std Deviation: 2.509760526005997
Distribution of 10000 samples:
 1: 10.82%
 2: 10.35%
 3: 11.73%
 4: 10.96%
 5: 11.75%
 6: 11.07%
 7: 11.12%
 8: 11.33%
 9: 10.87%

Base Case
Output Analysis: Random.randint(-5, 5)
Typical Timing: 215 ± 7 ns
Statistics of 1000 samples:
 Minimum: -5
 Median: 0
 Maximum: 5
 Mean: -0.156
 Std Deviation: 3.1358407959425327
Distribution of 10000 samples:
 -5: 9.2%
 -4: 8.93%
 -3: 9.09%
 -2: 9.06%
 -1: 8.78%
 0: 9.09%
 1: 8.92%
 2: 8.78%
 3: 9.19%
 4: 9.61%
 5: 9.35%

Output Analysis: random_int(-5, 5)
Typical Timing: 44 ± 1 ns
Statistics of 1000 samples:
 Minimum: -5
 Median: 0
 Maximum: 5
 Mean: -0.21
 Std Deviation: 3.2174916087306666
Distribution of 10000 samples:
 -5: 9.16%
 -4: 9.18%
 -3: 9.47%
 -2: 9.43%
 -1: 8.94%
 0: 8.88%
 1: 8.72%
 2: 9.09%
 3: 9.0%
 4: 8.83%
 5: 9.3%

Output Analysis: random_uint(18446744073709551605, 18446744073709551615)
Typical Timing: 64 ± 5 ns
Statistics of 1000 samples:
 Minimum: 18446744073709551605
 Median: 18446744073709551610
 Maximum: 18446744073709551615
 Mean: 1.8446744073709552e+19
 Std Deviation: 3.201873825745792
Distribution of 10000 samples:
 18446744073709551605: 9.49%
 18446744073709551606: 9.31%
 18446744073709551607: 8.87%
 18446744073709551608: 8.79%
 18446744073709551609: 9.29%
 18446744073709551610: 9.06%
 18446744073709551611: 9.06%
 18446744073709551612: 8.92%
 18446744073709551613: 8.95%
 18446744073709551614: 9.48%
 18446744073709551615: 8.78%

Base Case
Output Analysis: Random.randrange(1, 20, 2)
Typical Timing: 224 ± 6 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 9
 Maximum: 19
 Mean: 9.912
 Std Deviation: 5.6568768995141
Distribution of 10000 samples:
 1: 9.99%
 3: 9.71%
 5: 10.17%
 7: 9.63%
 9: 10.16%
 11: 10.04%
 13: 9.88%
 15: 9.86%
 17: 10.3%
 19: 10.26%

Output Analysis: random_range(1, 20, 2)
Typical Timing: 44 ± 3 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 11
 Maximum: 19
 Mean: 9.98
 Std Deviation: 5.68928536531329
Distribution of 10000 samples:
 1: 9.98%
 3: 9.7%
 5: 9.68%
 7: 10.07%
 9: 10.18%
 11: 10.21%
 13: 9.97%
 15: 10.33%
 17: 10.27%
 19: 9.61%

Output Analysis: random_range(1, 20, -2)
Typical Timing: 44 ± 2 ns
Statistics of 1000 samples:
 Minimum: 2
 Median: 10
 Maximum: 20
 Mean: 10.984
 Std Deviation: 5.769664897811054
Distribution of 10000 samples:
 2: 10.02%
 4: 9.99%
 6: 10.21%
 8: 9.31%
 10: 10.23%
 12: 9.36%
 14: 10.46%
 16: 9.81%
 18: 10.29%
 20: 10.32%

Output Analysis: random_range(20, 1, -2)
Typical Timing: 44 ± 2 ns
Statistics of 1000 samples:
 Minimum: 2
 Median: 12
 Maximum: 20
 Mean: 11.174
 Std Deviation: 5.738523734781852
Distribution of 10000 samples:
 2: 10.25%
 4: 10.26%
 6: 10.23%
 8: 10.18%
 10: 9.95%
 12: 10.08%
 14: 9.75%
 16: 9.73%
 18: 9.64%
 20: 9.93%

Output Analysis: d(10)
Typical Timing: 34 ± 3 ns
Statistics of 1000 samples:
 Minimum: 1
 Median: 5
 Maximum: 10
 Mean: 5.439
 Std Deviation: 2.817839459447472
Distribution of 10000 samples:
 1: 10.47%
 2: 10.28%
 3: 9.62%
 4: 10.05%
 5: 10.31%
 6: 10.11%
 7: 10.21%
 8: 9.32%
 9: 9.96%
 10: 9.67%

Output Analysis: dice(3, 6)
Typical Timing: 57 ± 5 ns
Statistics of 1000 samples:
 Minimum: 3
 Median: 11
 Maximum: 18
 Mean: 10.619
 Std Deviation: 3.0336516019546544
Distribution of 10000 samples:
 3: 0.5%
 4: 1.46%
 5: 2.75%
 6: 4.59%
 7: 7.04%
 8: 9.11%
 9: 11.51%
 10: 12.92%
 11: 12.21%
 12: 11.56%
 13: 9.96%
 14: 6.96%
 15: 4.51%
 16: 3.23%
 17: 1.32%
 18: 0.37%

Output Analysis: ability_dice(4)
Typical Timing: 98 ± 4 ns
Statistics of 1000 samples:
 Minimum: 3
 Median: 12
 Maximum: 18
 Mean: 12.264
 Std Deviation: 2.888017424574278
Distribution of 10000 samples:
 3: 0.15%
 4: 0.33%
 5: 0.72%
 6: 1.61%
 7: 3.03%
 8: 4.6%
 9: 7.38%
 10: 8.89%
 11: 11.18%
 12: 13.27%
 13: 13.44%
 14: 12.28%
 15: 9.96%
 16: 7.25%
 17: 4.32%
 18: 1.59%

Output Analysis: plus_or_minus(5)
Typical Timing: 31 ± 2 ns
Statistics of 1000 samples:
 Minimum: -5
 Median: 0
 Maximum: 5
 Mean: -0.069
 Std Deviation: 3.1474029206863783
Distribution of 10000 samples:
 -5: 8.87%
 -4: 9.39%
 -3: 8.94%
 -2: 9.57%
 -1: 8.96%
 0: 8.79%
 1: 9.32%
 2: 9.27%
 3: 9.25%
 4: 8.64%
 5: 9.0%

Output Analysis: plus_or_minus_linear(5)
Typical Timing: 40 ± 2 ns
Statistics of 1000 samples:
 Minimum: -5
 Median: 0
 Maximum: 5
 Mean: -0.036
 Std Deviation: 2.3854547563084054
Distribution of 10000 samples:
 -5: 2.65%
 -4: 5.35%
 -3: 8.27%
 -2: 11.15%
 -1: 14.14%
 0: 16.68%
 1: 13.5%
 2: 11.03%
 3: 8.38%
 4: 5.62%
 5: 3.23%

Output Analysis: plus_or_minus_gauss(5)
Typical Timing: 51 ± 5 ns
Statistics of 1000 samples:
 Minimum: -5
 Median: 0
 Maximum: 5
 Mean: -0.039
 Std Deviation: 1.6613967735731399
Distribution of 10000 samples:
 -5: 0.23%
 -4: 1.21%
 -3: 4.39%
 -2: 11.63%
 -1: 20.7%
 0: 24.58%
 1: 20.58%
 2: 10.97%
 3: 4.33%
 4: 1.13%
 5: 0.25%


Random Floats:
Base Case
Typical Timing: 23 ± 3 ns
Typical Timing: 24 ± 2 ns
Base Case
Output Analysis: Random.uniform(0.0, 10.0)
Typical Timing: 68 ± 2 ns
Statistics of 1000 samples:
 Minimum: 0.023402851721330276
 Median: (5.491653105252218, 5.493947751449272)
 Maximum: 9.964817457922248
 Mean: 5.27858407136633
 Std Deviation: 2.8181734385140573
floor distribution of 10000:
 0: 10.25%
 1: 9.78%
 2: 9.74%
 3: 9.76%
 4: 10.06%
 5: 10.22%
 6: 10.35%
 7: 9.44%
 8: 10.34%
 9: 10.06%

Output Analysis: random_float(0.0, 10.0)
Typical Timing: 25 ± 1 ns
Statistics of 1000 samples:
 Minimum: 0.0023965521759968574
 Median: (5.009607231697496, 5.015728880988601)
 Maximum: 9.979607195689656
 Mean: 5.032765724837154
 Std Deviation: 2.893871103454299
floor distribution of 10000:
 0: 10.58%
 1: 9.75%
 2: 10.15%
 3: 9.6%
 4: 9.83%
 5: 10.04%
 6: 9.98%
 7: 10.15%
 8: 10.14%
 9: 9.78%

Base Case
Output Analysis: Random.triangular(0.0, 10.0, 5.0)
Typical Timing: 137 ± 4 ns
Statistics of 1000 samples:
 Minimum: 0.22425041428260195
 Median: (5.003276392257881, 5.003996212550992)
 Maximum: 9.88449098067192
 Mean: 4.99433195027209
 Std Deviation: 1.992264050432249
round distribution of 10000:
 0: 0.55%
 1: 4.07%
 2: 7.74%
 3: 11.76%
 4: 16.57%
 5: 19.15%
 6: 15.93%
 7: 12.1%
 8: 7.92%
 9: 3.75%
 10: 0.46%

Output Analysis: triangular(0.0, 10.0, 5.0)
Typical Timing: 36 ± 1 ns
Statistics of 1000 samples:
 Minimum: 0.18382572092747493
 Median: (5.068962015548432, 5.074270702297919)
 Maximum: 9.694364845599836
 Mean: 5.042078124751621
 Std Deviation: 1.973892245691539
round distribution of 10000:
 0: 0.52%
 1: 4.1%
 2: 7.92%
 3: 11.67%
 4: 15.96%
 5: 19.25%
 6: 16.75%
 7: 11.63%
 8: 7.91%
 9: 3.82%
 10: 0.47%

Base Case
Output Analysis: Random.vonmisesvariate(0.0, 1.0)
Typical Timing: 348 ± 13 ns
Statistics of 1000 samples:
 Minimum: 0.004013008472991597
 Median: (3.039093632769718, 3.0432221525373366)
 Maximum: 6.280468869819905
 Mean: 3.083552571219304
 Std Deviation: 2.3059472085985324
round distribution of 10000:
 0: 16.48%
 1: 22.01%
 2: 9.07%
 3: 4.88%
 4: 6.87%
 5: 16.73%
 6: 23.96%

Output Analysis: vonmises_variate(0.0, 1.0)
Typical Timing: 86 ± 3 ns
Statistics of 1000 samples:
 Minimum: 0.0027471787233385
 Median: (3.613041794125548, 3.6237007185764063)
 Maximum: 6.28292438678854
 Mean: 3.227612003213251
 Std Deviation: 2.3063749553195456
round distribution of 10000:
 0: 16.74%
 1: 21.28%
 2: 8.32%
 3: 4.96%
 4: 6.73%
 5: 17.69%
 6: 24.28%

Base Case
Output Analysis: Random.expovariate(2.0)
Typical Timing: 107 ± 2 ns
Statistics of 1000 samples:
 Minimum: 0.00037153627687095395
 Median: (0.38167706798136336, 0.38280511185076094)
 Maximum: 3.9350477234554853
 Mean: 0.5141085234483942
 Std Deviation: 0.48635516925398947
round distribution of 10000:
 0: 62.89%
 1: 32.09%
 2: 4.36%
 3: 0.59%
 4: 0.06%
 5: 0.01%

Output Analysis: exponential_variate(2.0)
Typical Timing: 32 ± 1 ns
Statistics of 1000 samples:
 Minimum: 0.0008520523654106783
 Median: (0.35980522582795194, 0.35993338995219076)
 Maximum: 3.7999709869742255
 Mean: 0.5020788767150727
 Std Deviation: 0.49440568500375964
round distribution of 10000:
 0: 64.1%
 1: 31.22%
 2: 4.09%
 3: 0.47%
 4: 0.11%
 5: 0.01%

Base Case
Output Analysis: Random.gammavariate(1.0, 1.0)
Typical Timing: 163 ± 11 ns
Statistics of 1000 samples:
 Minimum: 0.002318571921186066
 Median: (0.69116429825915, 0.691798454086174)
 Maximum: 5.6878517706334
 Mean: 0.9712735806061341
 Std Deviation: 0.9430616975349418
round distribution of 10000:
 0: 38.68%
 1: 38.9%
 2: 14.46%
 3: 4.94%
 4: 1.91%
 5: 0.75%
 6: 0.2%
 7: 0.11%
 8: 0.04%
 9: 0.01%

Output Analysis: gamma_variate(1.0, 1.0)
Typical Timing: 42 ± 9 ns
Statistics of 1000 samples:
 Minimum: 0.0015115477125178436
 Median: (0.6878505235126586, 0.6910580746987727)
 Maximum: 6.333726583824109
 Mean: 1.0091432323822187
 Std Deviation: 1.0329480316089907
round distribution of 10000:
 0: 39.06%
 1: 38.48%
 2: 14.43%
 3: 5.06%
 4: 1.9%
 5: 0.68%
 6: 0.28%
 7: 0.08%
 8: 0.01%
 9: 0.01%
 11: 0.01%

Base Case
Output Analysis: Random.weibullvariate(1.0, 1.0)
Typical Timing: 152 ± 10 ns
Statistics of 1000 samples:
 Minimum: 0.0012846615769389457
 Median: (0.6959125670609901, 0.6960108369809325)
 Maximum: 6.019174765374365
 Mean: 0.9942726305048782
 Std Deviation: 0.9686281025277446
round distribution of 10000:
 0: 39.19%
 1: 38.62%
 2: 13.76%
 3: 5.15%
 4: 2.17%
 5: 0.75%
 6: 0.3%
 7: 0.04%
 8: 0.02%

Output Analysis: weibull_variate(1.0, 1.0)
Typical Timing: 57 ± 2 ns
Statistics of 1000 samples:
 Minimum: 1.1440881621293634e-05
 Median: (0.6887840102648795, 0.6892108925667445)
 Maximum: 6.9208828308442305
 Mean: 0.990214622191376
 Std Deviation: 0.9861811567922861
round distribution of 10000:
 0: 39.73%
 1: 39.03%
 2: 13.62%
 3: 4.68%
 4: 1.85%
 5: 0.71%
 6: 0.29%
 7: 0.05%
 8: 0.03%
 9: 0.01%

Base Case
Output Analysis: Random.normalvariate(0.0, 1.0)
Typical Timing: 246 ± 12 ns
Statistics of 1000 samples:
 Minimum: -2.9680525465226935
 Median: (-0.059688447937004896, -0.05939496661812857)
 Maximum: 3.6049546330945734
 Mean: -0.025784019169090313
 Std Deviation: 0.9936137055112212
round distribution of 10000:
 -4: 0.01%
 -3: 0.6%
 -2: 5.69%
 -1: 24.68%
 0: 37.83%
 1: 24.58%
 2: 6.08%
 3: 0.49%
 4: 0.04%

Output Analysis: normal_variate(0.0, 1.0)
Typical Timing: 48 ± 4 ns
Statistics of 1000 samples:
 Minimum: -2.9094888749140013
 Median: (0.03471835330534263, 0.034971460449014724)
 Maximum: 3.572833765486576
 Mean: 0.03330044483871605
 Std Deviation: 0.9883365510844506
round distribution of 10000:
 -4: 0.06%
 -3: 0.38%
 -2: 5.74%
 -1: 24.37%
 0: 38.02%
 1: 24.78%
 2: 6.07%
 3: 0.52%
 4: 0.06%

Base Case
Output Analysis: Random.lognormvariate(0.0, 1.0)
Typical Timing: 303 ± 12 ns
Statistics of 1000 samples:
 Minimum: 0.034471458413960265
 Median: (0.9402626809138573, 0.9440900010829929)
 Maximum: 23.496134963562216
 Mean: 1.6274851969090813
 Std Deviation: 2.0706788712517183
round distribution of 10000:
 0: 24.72%
 1: 41.12%
 2: 16.17%
 3: 7.43%
 4: 3.83%
 5: 2.3%
 6: 1.29%
 7: 1.05%
 8: 0.55%
 9: 0.52%
 10: 0.17%
 11: 0.21%
 12: 0.1%
 13: 0.14%
 14: 0.04%
 15: 0.02%
 16: 0.03%
 17: 0.08%
 18: 0.03%
 19: 0.02%
 20: 0.01%
 21: 0.05%
 22: 0.02%
 23: 0.04%
 30: 0.01%
 31: 0.01%
 32: 0.02%
 33: 0.01%
 43: 0.01%

Output Analysis: log_normal_variate(0.0, 1.0)
Typical Timing: 73 ± 2 ns
Statistics of 1000 samples:
 Minimum: 0.019726064065275144
 Median: (0.9824453534791109, 0.9856114818874442)
 Maximum: 27.563123457449453
 Mean: 1.6824957334358843
 Std Deviation: 2.1430458344764753
round distribution of 10000:
 0: 24.56%
 1: 40.97%
 2: 16.81%
 3: 7.46%
 4: 3.54%
 5: 2.43%
 6: 1.33%
 7: 0.93%
 8: 0.44%
 9: 0.37%
 10: 0.29%
 11: 0.28%
 12: 0.11%
 13: 0.1%
 14: 0.08%
 15: 0.05%
 16: 0.06%
 17: 0.02%
 18: 0.01%
 19: 0.04%
 20: 0.01%
 21: 0.01%
 22: 0.01%
 26: 0.03%
 28: 0.02%
 29: 0.01%
 30: 0.01%
 36: 0.01%
 59: 0.01%

timer(beta_variate, 1.0, 1.0)
Typical Timing: 48 ± 1 ns

timer(pareto_variate, 1.0)
Typical Timing: 37 ± 1 ns

timer(bernoulli_variate, 0.5)
Typical Timing: 21 ± 1 ns

timer(binomial_variate, 3, 0.5)
Typical Timing: 103 ± 2 ns

timer(negative_binomial_variate, 3, 0.5)
Typical Timing: 74 ± 2 ns

timer(geometric_variate, 0.5)
Typical Timing: 39 ± 1 ns

timer(poisson_variate, 0.5)
Typical Timing: 38 ± 1 ns

timer(extreme_value_variate, 0.0, 2.0)
Typical Timing: 49 ± 1 ns

timer(chi_squared_variate, 5.0)
Typical Timing: 73 ± 2 ns

timer(cauchy_variate, 0.0, 2.0)
Typical Timing: 39 ± 1 ns

timer(fisher_f_variate, 2.0, 3.0)
Typical Timing: 91 ± 3 ns

timer(student_t_variate, 5.0)
Typical Timing: 94 ± 2 ns

Random Booleans:
Output Analysis: percent_true(33.33)
Typical Timing: 22 ± 1 ns
Statistics of 1000 samples:
 Minimum: False
 Median: False
 Maximum: True
 Mean: 0.301
 Std Deviation: 0.45892222610112227
Distribution of 10000 samples:
 False: 67.36%
 True: 32.64%


Shuffle Performance:
	some_small_list = [i for i in range(10)]
	some_med_list = [i for i in range(100)]
	some_large_list = [i for i in range(1000)]

Base Case:
Random.shuffle()  # fisher_yates in python
Typical Timing: 1395 ± 26 ns
Typical Timing: 12202 ± 83 ns
Typical Timing: 136852 ± 1899 ns

Fortuna.shuffle()  # knuth_b in cython
Typical Timing: 210 ± 8 ns
Typical Timing: 1835 ± 25 ns
Typical Timing: 17323 ± 127 ns

Fortuna.knuth_a()  # knuth_a in cython
Typical Timing: 453 ± 7 ns
Typical Timing: 4000 ± 17 ns
Typical Timing: 45393 ± 411 ns

Fortuna.fisher_yates()  # fisher_yates in cython
Typical Timing: 490 ± 8 ns
Typical Timing: 4037 ± 13 ns
Typical Timing: 45653 ± 862 ns


Clamp Performance:
smart_clamp(3, 2, 1) # should be 2:  2
Typical Timing: 37 ± 2 ns
float_clamp(3.0, 2.0, 1.0) # should be 2.0:  2.0
Typical Timing: 38 ± 2 ns


-------------------------------------------------------------------------
Total Test Time: 1.078 seconds
```


## Legal Information
Fortuna is licensed under a Creative Commons Attribution-NonCommercial 3.0 Unported License. 
See online version of this license here: <http://creativecommons.org/licenses/by-nc/3.0/>

Other licensing options are available, please contact the author for details: [Robert Sharp](mailto:webmaster@sharpdesigndigital.com)
