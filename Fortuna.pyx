#!python3
#distutils: language = c++
from collections import deque
from itertools import cycle
from math import sqrt
from typing import Any, List, Sequence, Tuple, Callable, Iterable, Dict

version = "5.4.3"

cdef extern from "Storm.hpp":
    const char* _storm_version "Storm::get_version"()
    void _seed "Storm::Engine::seed"(unsigned long long)
    double _float_clamp "Storm::GearBox::clamp"(double, double, double)
    long long _smart_clamp "Storm::GearBox::clamp"(long long, long long, long long)
    unsigned long long _max_uint "Storm::Meters::max_uint"()
    long long _min_int "Storm::Meters::min_int"()
    long long _max_int "Storm::Meters::max_int"()
    double _min_float "Storm::Meters::min_float"()
    double _max_float "Storm::Meters::max_float"()
    double _min_below "Storm::Meters::min_below"()
    double _min_above "Storm::Meters::min_above"()
    int _percent_true "Storm::GetBool::percent_true"(double)
    int _bernoulli "Storm::GetBool::bernoulli_variate"(double)
    long long _d "Storm::GetInt::d"(long long)
    long long _dice "Storm::GetInt::dice"(long long, long long)
    long long _ability_dice "Storm::GetInt::ability_dice"(long long)
    long long _random_int "Storm::GetInt::uniform_int_variate"(long long, long long)
    unsigned long long _random_uint "Storm::GetInt::uniform_uint_variate"(unsigned long long, unsigned long long)
    long long _binomial "Storm::GetInt::binomial_variate"(long long, double)
    long long _neg_binomial "Storm::GetInt::negative_binomial_variate"(long long, double)
    long long _geometric "Storm::GetInt::geometric_variate"(double)
    long long _poisson "Storm::GetInt::poisson_variate"(double)
    long long _random_below "Storm::GetInt::random_below"(long long)
    long long _random_range "Storm::GetInt::random_range"(long long, long long, long long)
    long long _plus_or_minus "Storm::GetInt::plus_or_minus"(long long)
    long long _plus_or_minus_linear "Storm::GetInt::plus_or_minus_linear"(long long)
    long long _plus_or_minus_gauss "Storm::GetInt::plus_or_minus_gauss"(long long)
    long long _random_index "Storm::GetIndex::random_index"(long long)
    long long _front_gauss "Storm::GetIndex::front_gauss"(long long)
    long long _middle_gauss "Storm::GetIndex::middle_gauss"(long long)
    long long _back_gauss "Storm::GetIndex::back_gauss"(long long)
    long long _quantum_gauss "Storm::GetIndex::quantum_gauss"(long long)
    long long _front_poisson "Storm::GetIndex::front_poisson"(long long)
    long long _middle_poisson "Storm::GetIndex::middle_poisson"(long long)
    long long _back_poisson "Storm::GetIndex::back_poisson"(long long)
    long long _quantum_poisson "Storm::GetIndex::quantum_poisson"(long long)
    long long _front_linear "Storm::GetIndex::front_linear"(long long)
    long long _middle_linear "Storm::GetIndex::middle_linear"(long long)
    long long _back_linear "Storm::GetIndex::back_linear"(long long)
    long long _quantum_linear "Storm::GetIndex::quantum_linear"(long long)
    long long _quantum_monty "Storm::GetIndex::quantum_monty"(long long)
    double _canonical "Storm::GetFloat::canonical_variate"()
    double _random_float "Storm::GetFloat::uniform_real_variate"(double, double)
    double _triangular "Storm::GetFloat::triangular_variate"(double, double, double)
    double _exponential "Storm::GetFloat::exponential_variate"(double)
    double _gamma "Storm::GetFloat::gamma_variate"(double, double)
    double _weibull "Storm::GetFloat::weibull_variate"(double, double)
    double _normal "Storm::GetFloat::normal_variate"(double, double)
    double _log_normal "Storm::GetFloat::log_normal_variate"(double, double)
    double _extreme_value "Storm::GetFloat::extreme_value_variate"(double, double)
    double _chi_squared "Storm::GetFloat::chi_squared_variate"(double)
    double _cauchy "Storm::GetFloat::cauchy_variate"(double, double)
    double _fisher_f "Storm::GetFloat::fisher_f_variate"(double, double)
    double _student_t "Storm::GetFloat::student_t_variate"(double)
    double _beta "Storm::GetFloat::beta_variate"(double, double)
    double _pareto "Storm::GetFloat::pareto_variate"(double)
    double _vonmises "Storm::GetFloat::vonmises_variate"(double, double)


def storm_version() -> str:
    """ Current version of Storm """
    return _storm_version().decode("utf-8")


def seed(value: int = 0) -> None:
    """ Seeds the Hurricane Engine
    Uses a hardware seeding methodology iff the host supports it and value == 0
    Software seeding should only be used in single-thread applications.
    :param value: Integer [0, 18446744073709551615] default: 0, best if very large or 0
    :return: None """
    _seed(value)


def max_uint() -> int:
    """ Maximum Unsigned Integer """
    return _max_uint()


def max_int() -> int:
    """ Maximum Integer """
    return _max_int()


def min_int() -> int:
    """ Minimum Integer """
    return _min_int()


def min_float() -> float:
    """ Minimum Float """
    return _min_float()


def max_float() -> float:
    """ Maximum Float """
    return _max_float()


def min_below() -> float:
    """ Minimum Float below zero """
    return _min_below()


def min_above() -> float:
    """ Minimum Float above zero """
    return _min_above()


def distribution_range(func: Callable, lower, upper):
    """ Distribution Range

    @param func: ZeroCool random distribution, F(N) -> [0, N-1]
    @param lower: minimum
    @param upper: maximum
    @return: returns random value in range [lo, hi]
    """
    return lower + func(1 + upper - lower)


class DistributionRange:
    """ DistributionRange

    @param zero_cool: ZeroCool random distribution, F(N) -> [0, N-1]
    @param lower: minimum
    @param upper: maximum
    """

    def __init__(self, zero_cool: Callable, lower, upper):
        self.zero_cool = zero_cool
        self.lower = lower
        self.upper = upper

    def __call__(self):
        return self.lower + self.zero_cool(1 + self.upper - self.lower)


def random_below(limit: int) -> int:
    """ Random Below: Flat uniform distribution.
    Returns a random integer in the range [0, limit), or (limit, 0] for
    negative limit. Returns zero for limit of zero.

    @param limit: Specified limit
    @return: Random integer in the range [0, limit), or (limit, 0]
    """
    return _random_below(limit)


def random_index(limit: int) -> int:
    """ Random Index: Flat uniform distribution.
    Canonical ZeroCool method.
    Returns a random integer in the range [0, limit), or [limit, 0) for
    negative numbers. The symmetry of this function matches how python will
    index a list from the back for negative values.

    @param limit: Specified limit
    @return: Random integer in the range [0, limit), or [limit, 0)
    """
    return _random_index(limit)


def random_int(left_limit: int, right_limit: int) -> int:
    """ Random Integer: Flat uniform distribution.

    @param left_limit: Integer. Typically, the lower of the two.
    @param right_limit: Integer. Typically, the higher of the two.
    @return: Integer. Random integer in the range [left_limit, right_limit].
    """
    return _random_int(left_limit, right_limit)


def random_uint(left_limit: int, right_limit: int) -> int:
    """ Random Unsigned Integer: Flat uniform distribution.

    @param left_limit: Unsigned Integer. Typically, the lower of the two.
    @param right_limit: Unsigned Integer. Typically, the higher of the two.
    @return: Integer. Random unsigned integer in the range [left_limit, right_limit].
    """
    return _random_uint(left_limit, right_limit)


def random_range(start: int, stop: int = 0, step: int = 1) -> int:
    """ Random Range: Flat uniform distribution.
    The order of the inputs `start` and `stop` are interchangeable.
    Conceptually: A = min(start, stop), B = max(start, stop), C = step
    The sign of the step parameter controls the phase of the output.
    Negative stepping will flip the inclusivity of the distribution.
    In other words: a negative step means to count down, not up.

    @param start: Typically the lower bound. Inclusive.
    @param stop: Typically the upper limit. Exclusive.
    @param step: Size of the increments within the distribution.
    @return: Random Integer in range [A, B) by C, or (A, B] by |C| for -C
    """
    return _random_range(start, stop, step)


def d(sides: int = 20) -> int:
    """ D: Flat uniform distribution.
    Represents a single roll of a given die, d20 by default.
    Flat uniform distribution.
    @param sides: The size of the die is equal to the number of sides.
    @return: Value of the die rolled.
    """
    return _d(sides)


def dice(rolls: int = 1, sides: int = 20) -> int:
    """ Dice: Geometric distribution.
    Represents the sum of multiple rolls of the same size die.
    Geometric distribution based on the number and size of the dice rolled.
    @param rolls: The number of rolls to make.
    @param sides: The size of the die is equal to the number of sides.
    @return: Sum of the dice rolled.
    """
    return _dice(rolls, sides)


def ability_dice(rolls: int = 4) -> int:
    """ Ability Dice: Geometric distribution.
    @param rolls :: Number of d6 rolls. Default = 4. Clamped in range [3, 9]
    @return int :: Returns the sum of the top 3 of N d(6), where N = rolls.
    """
    return _ability_dice(rolls)


def plus_or_minus(number: int = 1) -> int:
    """ Plus or Minus: Flat uniform distribution.

    @param number: Integer. Maximum variance from zero. Default is one.
    @return: Random integer in range [-number, number]. Mean = 0.
    """
    return _plus_or_minus(number)


def plus_or_minus_linear(number: int = 1) -> int:
    """ Plus or Minus Linear: Linear distribution centered on zero.

    @param number: Integer. Maximum variance from zero. Default is one.
    @return: Random integer in range [-number, number]. Mean = 0.
    """
    return _plus_or_minus_linear(number)


def plus_or_minus_gauss(number: int = 1) -> int:
    """ Plus or Minus Gaussian: Gaussian distribution centered on zero.

    @param number: Integer. Maximum variance from zero. Default is one.
    @return: Random integer in range [-number, number]. Mean = 0.
    """
    return _plus_or_minus_gauss(number)


def percent_true(truth_factor: float = 50.0) -> bool:
    """ Percent True
    Produces True or False based on the probability of True as a percentage.

    @param truth_factor: Float. Default is 50. Probability of True.
    @return: Random bool.
    """
    return _percent_true(truth_factor) == 1


def canonical() -> float:
    """ Canonical: Flat uniform distribution.
    Inclusiveness can vary across platforms.

    @return: Random float in range [0.0, 1.0)
    """
    return _canonical()


def random_float(left_limit: float = 0.0, right_limit: float = 1.0) -> float:
    """ Random Floating Point: Flat uniform distribution.
    Returns a random float in range [left_limit, right_limit).
    """
    return _random_float(left_limit, right_limit)


def triangular(low: float, high: float, mode: float) -> float:
    """ Triangular
    Returns a random float in range [low, high] with a linear
        distribution about the mode. """
    return _triangular(low, high, mode)


def float_clamp(target: float, lo: float, hi: float) -> float:
    """ Float Clamp
    Essentially the same as median but considerably faster.
    @return :: Returns the middle value of three float arguments,
        input order does not matter.
    """
    return _float_clamp(target, lo, hi)


def smart_clamp(target: int, lo: int, hi: int) -> int:
    """ Smart Clamp
    Essentially the same as median but considerably faster.
    @return :: Returns the middle value of three integer arguments,
        input order does not matter.
    """
    return _smart_clamp(target, lo, hi)


def flatten(maybe_callable: Any, *args, flat: bool = True, **kwargs):
    """ Flatten
    Internal only.
    Recursively calls the input object and returns the result.
    The arguments are only passed in on the first evaluation.
    If the object is not callable it is simply returned without error.
    Essentially this is the opposite of bind, and it's recursive.
    Conceptually this is somewhat like collapsing the wave function.
    Often flatten is used as the last step in lazy evaluation.
    @param maybe_callable :: Any Object that might be callable.
    @param flat :: Boolean, default is True. Optional, keyword only.
        Disables flattening if flat is set to False,
        conceptually this turns flatten() into the identity function.
    @param args: Optional arguments used to flatten the maybe_callable object.
    @param kwargs: Optional arguments used to flatten the maybe_callable object.
    @return :: Recursively Flattened Object.
    """
    if flat is False or not callable(maybe_callable):
        return maybe_callable
    else:
        try:
            return flatten(maybe_callable(*args, **kwargs))
        except TypeError:
            return maybe_callable


def shuffle(array: List[Any]):
    """ Knuth B Shuffle Algorithm
    Destructive, in-place shuffle.
    Reverse Order Random Swap to Back

    @param array: List of values to be shuffled.
    """
    size = len(array) - 1
    for i in reversed(range(size)):
        j = _random_int(i, size)
        array[i], array[j] = array[j], array[i]


def knuth_a(array: List[Any]):
    """ Knuth A Shuffle Algorithm
    Destructive, in-place shuffle.
    In Order Random Swap to Front

    @param array: List of values to be shuffled.
    """
    for i in range(1, len(array)):
        j = _random_below(i + 1)
        array[i], array[j] = array[j], array[i]


def fisher_yates(array: List[Any]):
    """ Fisher Yates Shuffle Algorithm
    Destructive, in-place shuffle.
    Reverse Order Random Swap to Front

    @param array: List of values to be shuffled.
    """
    for i in reversed(range(1, len(array))):
        j = _random_below(i + 1)
        array[i], array[j] = array[j], array[i]


def front_gauss(size: int) -> int:
    """ Gamma Index Distribution: Front Peak. """
    return _front_gauss(size)


def middle_gauss(size: int) -> int:
    """ Gaussian Index Distribution: Middle Peak. """
    return _middle_gauss(size)


def back_gauss(size: int) -> int:
    """ Gamma Index Distribution: Back Peak. """
    return _back_gauss(size)


def quantum_gauss(size: int) -> int:
    """ Quantum Gaussian Index Distribution: Three-way Monty. """
    return _quantum_gauss(size)


def front_poisson(size: int) -> int:
    """ Poisson Index Distribution: Front 1/3 Peak. """
    return _front_poisson(size)


def middle_poisson(size: int) -> int:
    """ Symmetric Poisson Index Distribution. """
    return _middle_poisson(size)


def back_poisson(size: int) -> int:
    """ Poisson Index Distribution: Back 1/3 Peak. """
    return _back_poisson(size)


def quantum_poisson(size: int) -> int:
    """ Quantum Poisson Index Distribution: Three-way Monty.
        Twin Peaks """
    return _quantum_poisson(size)


def front_linear(size: int) -> int:
    """ Linear Geometric Index Distribution: 45 Degree Front Peak.
        Left Triangle """
    return _front_linear(size)


def middle_linear(size: int) -> int:
    """ Linear Geometric Index Distribution: 45 Degree Middle Peak.
        Pyramid """
    return _middle_linear(size)


def back_linear(size: int) -> int:
    """ Linear Geometric Index Distribution: 45 Degree Back Peak.
        Right Triangle """
    return _back_linear(size)


def quantum_linear(size: int) -> int:
    """ Quantum Geometric Index Distribution: Three-way Monty.
        Saw Tooth """
    return _quantum_linear(size)


def quantum_monty(size: int) -> int:
    """ Quantum Monty Index Distribution: Nine-way Monty.
        Quantum Wave. """
    return _quantum_monty(size)


ZeroCool = {
    "random_index": random_index,
    "front_linear": front_linear,
    "middle_linear": middle_linear,
    "back_linear": back_linear,
    "quantum_linear": quantum_linear,
    "front_gauss": front_gauss,
    "middle_gauss": middle_gauss,
    "back_gauss": back_gauss,
    "quantum_gauss": quantum_gauss,
    "front_poisson": front_poisson,
    "middle_poisson": middle_poisson,
    "back_poisson": back_poisson,
    "quantum_poisson": quantum_poisson,
    "quantum_monty": quantum_monty,
}


def random_value(data: Sequence[Any]) -> Any:
    """ Random Value Function
    Equivalent to Random.choice. Flat uniform distribution.
    Also see RandomValue class for additional options.
    The function is measurably faster than the class,
        but the class offers far more flexibility. """
    return data[_random_index(len(data))]


def cumulative_weighted_choice(weighted_table: Sequence[Tuple[int, Any]]) -> Any:
    """ Cumulative Weighted Choice Function
    Similar to Random.choices.
    Also see CumulativeWeightedChoice and RelativeWeightedChoice.
    The function is measurably faster than the class,
        but the class offers far more flexibility. """
    max_weight = weighted_table[-1][0]
    rand = _random_index(max_weight)
    for weight, value in weighted_table:
        if weight > rand:
            return value


def truffle_shuffle(data: Sequence[Any]) -> Callable:
    """ Truffle Shuffle Function: Function Factory
    Same as the class of the same name, implemented as a higher-order function.
    """
    working_data = list(data)
    shuffle(working_data)
    data = deque(working_data)
    rotate_size = int(sqrt(len(working_data)))
    def worker() -> Any:
        data.rotate(1 + _front_poisson(rotate_size))
        return data[-1]
    return worker


def sample(population: Sequence[Any], k: int) -> List[Any]:
    n = len(population)
    assert 0 < k <= n, "Sample size k is larger than population or is negative"
    if k == 1:
        return [random_value(population)]
    elif k >= n // 2:
        result = list(population)
        shuffle(result)
        return result[:k]
    else:
        result = []
        selected = set()
        for i in range(k):
            j = _random_index(n)
            while j in selected:
                j = _random_index(n)
            selected.add(j)
            result.append(population[j])
        return result


class RandomValue:
    """ Random Value Class
    Random Value Generator Class that supports dependency injection.
    @param collection :: Collection of Values. Tuple recommended.
    @param zero_cool :: Optional ZeroCool Method, kwarg only.
        Default = random_index()
    @param flat :: Bool. Default: True.
        Option to automatically flatten callable values with lazy evaluation.
    @return :: Callable Object. `Callable(*args, **kwargs) -> Value`
        @param *args, **kwargs :: Optional arguments used to flatten the return.
        @return Value or Value(*args, **kwargs) if Callable.

    Please refer to https://pypi.org/project/Fortuna/ for full documentation.
    """
    __slots__ = ("data", "zero_cool", "flat")

    def __init__(self,
                 collection: Iterable[Any],
                 zero_cool: Callable[[int], int] = random_index,
                 flat: bool = True):
        self.data = tuple(collection)
        assert len(self.data) > 0, "Input Error, Empty Container"
        self.zero_cool = zero_cool
        self.flat = flat

    def __call__(self, *args, **kwargs) -> Any:
        return flatten(self.data[self.zero_cool(len(self.data))], *args, flat=self.flat, **kwargs)


class TruffleShuffle:
    """ Truffle Shuffle
    Produces random values from a collection with a Wide Uniform Distribution.

    @param collection :: Collection of Values. Any list-like object, a Set is
        recommended but not required.
    @param flat :: Bool. Default: True. Option to automatically flatten
        callable values with lazy evaluation.
    @return :: Callable Object. `Callable(*args, **kwargs) -> Value`
        @param *args, **kwargs :: Optional arguments used to flatten the
            return Value (below) if Callable.
        @return :: Value or Value(*args, **kwargs) if Callable.

    Wide Uniform Distribution: "Wide" refers to the average distance between
    consecutive occurrences of the same value. The average width of the output
    distribution will naturally scale up with the size of the collection.
    The goal of this type of distribution is to keep the output sequence free
    of clumps or streaks of the same value, while maintaining randomness and
    uniform probability. This is not the same as a flat uniform distribution.
    The two distributions over time will be statistically similar for any
    given set, but the repetitiveness of the output sequence will be
    very different.

    TruffleShuffle is a state machine. It does no comparisons, and keeps no
    additional history list. As such it is very fast to call and does not
    lose performance or grow in memory over time.

    Please refer to https://pypi.org/project/Fortuna/ for full documentation.
    """
    __slots__ = ("flat", "data", "rotate_size")

    def __init__(self, collection: Iterable[Any], flat: bool = True):
        self.flat = flat
        data = list(collection)
        shuffle(data)
        self.data = deque(data)
        self.rotate_size = int(sqrt(len(self.data)))

    def __call__(self, *args, **kwargs) -> Any:
        self.data.rotate(1 + _front_poisson(self.rotate_size))
        return flatten(self.data[-1], *args, flat=self.flat, **kwargs)


class QuantumMonty:
    """ Quantum Monty
    @param collection :: Collection of Values.
    @param flat :: Bool. Default is True. Option to automatically flatten
        callable values with lazy evaluation.
    @return :: Callable Object with Monty Methods for producing various
        distributions of the collection.
        @param *args, **kwargs :: Optional arguments used to flatten the return
            Value (below) if Callable.
        @return :: Random value from the collection.

    Please refer to https://pypi.org/project/Fortuna/ for full documentation.
    """
    __slots__ = ("flat", "size", "data", "truffle_shuffle", "cycles")

    def __init__(self, collection: Iterable[Any], flat: bool = True):
        self.flat = flat
        self.data = tuple(collection)
        self.size = len(self.data)
        assert self.size > 0, "Input Error, Empty Container"
        self.cycles = cycle(self.data)
        self.truffle_shuffle = TruffleShuffle(self.data, flat)

    def __call__(self, *args, **kwargs) -> Any:
        return self.quantum_monty(*args, **kwargs)

    def dispatch(self, monty: str) -> Callable:
        """ For automation, prefer to use the methods directly when possible. """
        return {
            "flat_uniform": self.flat_uniform,
            "cycle": self.cycle,
            "truffle_shuffle": self.truffle_shuffle,
            "front_linear": self.front_linear,
            "middle_linear": self.middle_linear,
            "back_linear": self.back_linear,
            "quantum_linear": self.quantum_linear,
            "front_gauss": self.front_gauss,
            "middle_gauss": self.middle_gauss,
            "back_gauss": self.back_gauss,
            "quantum_gauss": self.quantum_gauss,
            "front_poisson": self.front_poisson,
            "middle_poisson": self.middle_poisson,
            "back_poisson": self.back_poisson,
            "quantum_poisson": self.quantum_poisson,
            "quantum_monty": self.quantum_monty,
        }[monty]

    def flat_uniform(self, *args, **kwargs) -> Any:
        return flatten(
            self.data[_random_index(self.size)], *args, flat=self.flat, **kwargs
        )

    def cycle(self, *args, **kwargs):
        return flatten(next(self.cycles))

    def front_linear(self, *args, **kwargs) -> Any:
        return flatten(
            self.data[_front_linear(self.size)], *args, flat=self.flat, **kwargs
        )

    def middle_linear(self, *args, **kwargs) -> Any:
        return flatten(
            self.data[_middle_linear(self.size)], *args, flat=self.flat, **kwargs
        )

    def back_linear(self, *args, **kwargs) -> Any:
        return flatten(
            self.data[_back_linear(self.size)], *args, flat=self.flat, **kwargs
        )

    def quantum_linear(self, *args, **kwargs) -> Any:
        return flatten(
            self.data[_quantum_linear(self.size)], *args, flat=self.flat, **kwargs
        )

    def front_gauss(self, *args, **kwargs) -> Any:
        return flatten(
            self.data[_front_gauss(self.size)], *args, flat=self.flat, **kwargs)

    def middle_gauss(self, *args, **kwargs) -> Any:
        return flatten(
            self.data[_middle_gauss(self.size)], *args, flat=self.flat, **kwargs
        )

    def back_gauss(self, *args, **kwargs) -> Any:
        return flatten(
            self.data[_back_gauss(self.size)], *args, flat=self.flat, **kwargs
        )

    def quantum_gauss(self, *args, **kwargs) -> Any:
        return flatten(
            self.data[_quantum_gauss(self.size)], *args, flat=self.flat, **kwargs
        )

    def front_poisson(self, *args, **kwargs) -> Any:
        return flatten(
            self.data[_front_poisson(self.size)], *args, flat=self.flat, **kwargs
        )

    def middle_poisson(self, *args, **kwargs) -> Any:
        return flatten(
            self.data[_middle_poisson(self.size)], *args, flat=self.flat, **kwargs
        )

    def back_poisson(self, *args, **kwargs) -> Any:
        return flatten(
            self.data[_back_poisson(self.size)], *args, flat=self.flat, **kwargs
        )

    def quantum_poisson(self, *args, **kwargs) -> Any:
        return flatten(
            self.data[_quantum_poisson(self.size)], *args, flat=self.flat, **kwargs
        )

    def quantum_monty(self, *args, **kwargs) -> Any:
        return flatten(
            self.data[_quantum_monty(self.size)], *args, flat=self.flat, **kwargs
        )


class FlexCat:
    """ Flex Cat
    FlexCat is a lot like a multidimensional QuantumMonty.

    The initializer takes two optional keyword arguments to specify the
    algorithms to be used to make random selections. The algorithm specified
    for selecting a key need not be the same as the one for selecting values.
    An optional key may be provided at call time to bypass the random
    key selection. Keys passed in this way must exactly match a
    key in the Matrix.

    By default, FlexCat will use key_bias="front_linear"
    and val_bias="truffle_shuffle", this will make the top of the data
    structure geometrically more common than the bottom, and it will
    truffle shuffle the sequence values. This config is known as TopCat,
    it produces a descending-step, wide inner-distribution sequence.
    Many other combinations are available.

    Please refer to https://pypi.org/project/Fortuna/ for full documentation.
    """
    __slots__ = ("random_cat", "random_selection", "cat_keys", "matrix_data",
                 "double_cycle", "cycle")

    def __init__(self,
                 matrix_data: Dict[Any, Iterable[Any]],
                 key_bias: str = "front_linear",
                 val_bias: str = "truffle_shuffle",
                 flat: bool = True):
        """
        @param matrix_data :: Dictionary of Value Sequences.
        @parm key_bias :: Default is "front_linear". String indicating the
            name of the algorithm to use for random key selection.
        @parm val_bias :: Default is "truffle_shuffle". String indicating the
            name of the algorithm to use for random value selection.
        @param flat :: Bool. Default is True. Option to automatically flatten
            callable values with lazy evaluation.
        @return :: Callable Instance
        """
        self.double_cycle = key_bias == val_bias == "cycle"
        self.matrix_data = matrix_data
        self.cat_keys = matrix_data.keys()
        self.random_cat = QuantumMonty(
            tuple(self.cat_keys),
            flat=False,
        ).dispatch(key_bias)
        self.random_selection = {
            key: QuantumMonty(
                tuple(seq),
                flat=flat,
            ).dispatch(val_bias)
            for key, seq in matrix_data.items()
        }
        cycle_source = []
        for seq in matrix_data.values():
            cycle_source += seq
        self.cycle = cycle(cycle_source)

    def __call__(self, cat_key=None, *args, **kwargs) -> Any:
        """
        @param cat_key :: Optional String. Default is None.
            Key selection by name.
        @param *args, **kwargs :: Optional arguments used to flatten the
            return Value (below) if Callable.
        @return :: Value. Returns a random value generated with val_bias
            from a random sequence generated with key_bias.
        """
        if self.double_cycle:
            return next(self.cycle)
        monty = self.random_selection
        key = cat_key if cat_key is not None else self.random_cat()
        return monty[key](*args, **kwargs)


class WeightedChoice:
    """ Weighted Choice
    Base Class, internal only.

    Weighted Choice offers two strategies for selecting random values
    from a sequence where programmable rarity is desired. RelativeWeightedChoice
    & CumulativeWeightedChoice Both produce a custom distribution of values
    based on the weights of the values.

    The choice to use one strategy over the other is purely about which
    one suits you or your data best. Relative weights are easier to
    understand at a glance. However, many RPG Treasure Tables map rather
    nicely to a cumulative weighted strategy.

    Please refer to https://pypi.org/project/Fortuna/ for full documentation.
    """
    __slots__ = ("flat", "max_weight", "data")

    def __call__(self, *args, **kwargs) -> Any:
        """
        @param *args, **kwargs :: Optional arguments
            used to flatten the return Value (below) if Callable.
        @return :: Random value from the weighted_table,
            distribution based on the weights of the values.
        """
        rand = _random_below(self.max_weight)
        for weight, value in self.data:
            if weight > rand:
                return flatten(value, *args, flat=self.flat, **kwargs)


class RelativeWeightedChoice(WeightedChoice):
    """ Relative Weighted Choice """
    __slots__ = ("flat", "max_weight", "data")

    def __init__(self,
                 weighted_table: Iterable[Tuple[int, Any]],
                 flat: bool = True):
        """
        @param weighted_table :: Table of weighted pairs.
            [ (w1, v1), (w2, v2), (w3, v3)... ] or zip(weights, values)
        @param flat :: Bool. Default: True. Option to automatically
            flatten callable values with lazy evaluation.
        @return :: Callable Instance
        """
        self.flat = flat
        optimized_data = sorted(
            [list(itm) for itm in weighted_table],
            key=lambda x: x[0], reverse=True)
        cum_weight = 0
        for w_pair in optimized_data:
            cum_weight += w_pair[0]
            w_pair[0] = cum_weight
        self.max_weight = optimized_data[-1][0]
        self.data = tuple(tuple(itm) for itm in optimized_data)


class CumulativeWeightedChoice(WeightedChoice):
    """ Cumulative Weighted Choice """
    __slots__ = ("flat", "max_weight", "data")

    def __init__(self,
                 weighted_table: Iterable[Tuple[int, Any]],
                 flat: bool = True):
        """
        @param weighted_table :: Table of weighted pairs.
        @param flat :: Bool. Default: True. Option to automatically
            flatten callable values with lazy evaluation.
        @return :: Callable Instance

        Note: Logic dictates Cumulative Weights must be unique!
        """
        self.flat = flat
        data = sorted([list(itm) for itm in weighted_table], key=lambda x: x[0])
        prev_weight = 0
        for w_pair in data:
            w_pair[0], prev_weight = w_pair[0] - prev_weight, w_pair[0]
        optimized_data = sorted(data, key=lambda x: x[0], reverse=True)
        cum_weight = 0
        for w_pair in optimized_data:
            cum_weight += w_pair[0]
            w_pair[0] = cum_weight
        self.max_weight = optimized_data[-1][0]
        self.data = tuple(tuple(itm) for itm in optimized_data)


class MultiChoice:
    """ Multiple Choice
    MultiChoice: generates multiple choice style questions on the terminal. """

    def __init__(self,
                 query: str,
                 *,
                 options: Iterable[str] = (),
                 default: str = "",
                 strict: bool = False,
                 cursor: str = ">>>"):
        """ Multiple Choice
        @param query: String.
            Question for the user.
        @param options: Optional Iterable of Strings.
            Options presented to the user as a numbered sequence.
            The user may enter an answer as text or one of the numbers.
        @param default: Optional String.
            This is returned if no user input is provided.
            If no default is provided a random choice will be made.
        @param strict: Optional Bool. Default=False
            True: Answer must be in the options tuple. Not case-sensitive.
            False: Accepts any answer.
        @param cursor: Optional String. Default='>>>' Indicates user input.
        """
        self.cursor = cursor + ' '
        self.prompt = query
        self.options = tuple(options)
        self.default = default.lower()
        self.strict = strict
        self.data = {
            str(k + 1): v.lower() for k, v in enumerate(self.options)
        }
        self.choice_pack = (
            self.prompt,
            *(f"{k}. {v.title()}" for k, v in self.data.items()),
            self.cursor,
        )

    def _get_answer(self) -> str:
        return input('\n'.join(self.choice_pack)).lower() or self.default

    def __call__(self) -> str:
        """ @return: String. Returns the user's selection. """
        selection = self._get_answer()
        if not selection and self.options:
            return random_value(self.options)
        elif selection in self.data.values():
            return selection.title()
        elif selection in self.data.keys():
            return self.data[selection].title()
        elif selection and not self.strict:
            return selection.title()
        else:
            return self()


def beta_variate(alpha: float, beta: float) -> float:
    return _beta(alpha, beta)


def pareto_variate(alpha: float) -> float:
    return _pareto(alpha)


def vonmises_variate(mu: float, kappa: float) -> float:
    return _vonmises(mu, kappa)


def bernoulli_variate(ratio_of_truth: float) -> bool:
    return _bernoulli(ratio_of_truth) == 1


def binomial_variate(number_of_trials: int, probability: float) -> int:
    return _binomial(number_of_trials, probability)


def negative_binomial_variate(number_of_trials: int, probability: float) -> int:
    return _neg_binomial(number_of_trials, probability)


def geometric_variate(probability: float) -> int:
    return _geometric(probability)


def poisson_variate(mean: float) -> int:
    return _poisson(mean)


def exponential_variate(lambda_rate: float) -> float:
    return _exponential(lambda_rate)


def gamma_variate(shape: float, scale: float) -> float:
    return _gamma(shape, scale)


def weibull_variate(shape: float, scale: float) -> float:
    return _weibull(shape, scale)


def normal_variate(mean: float, std_dev: float) -> float:
    return _normal(mean, std_dev)


def log_normal_variate(log_mean: float, log_deviation: float) -> float:
    return _log_normal(log_mean, log_deviation)


def extreme_value_variate(location: float, scale: float) -> float:
    return _extreme_value(location, scale)


def chi_squared_variate(degrees_of_freedom: float) -> float:
    return _chi_squared(degrees_of_freedom)


def cauchy_variate(location: float, scale: float) -> float:
    return _cauchy(location, scale)


def fisher_f_variate(degrees_of_freedom_1: float, degrees_of_freedom_2: float) -> float:
    return _fisher_f(degrees_of_freedom_1, degrees_of_freedom_2)


def student_t_variate(degrees_of_freedom: float) -> float:
    return _student_t(degrees_of_freedom)
