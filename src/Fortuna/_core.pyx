# distutils: language = c++
# cython: language_level=3, embedsignature=True

from hashlib import sha256
from collections.abc import MutableSequence
from numbers import Real
import operator
import os

from libc.stddef cimport size_t
from libc.stdint cimport int64_t, uint64_t, uint8_t
from cpython.list cimport PyList_New
from cpython.object cimport PyObject
from libcpp.vector cimport vector


cdef extern from "Python.h":
    PyObject* raw_float_from_double "PyFloat_FromDouble"(double) except NULL
    void raw_list_set_item "PyList_SET_ITEM"(PyObject*, Py_ssize_t, PyObject*)


cdef extern from "src/Fortuna/cpp/fortuna_core.hpp" namespace "FortunaCore":
    cdef cppclass GeneratorCore:
        GeneratorCore(uint64_t) except +
        void seed(uint64_t) except + nogil
        void reseed_from_entropy() except + nogil
        void lock() except + nogil
        void unlock() noexcept nogil
        void prepare() except + nogil

    const char* core_storm_version "FortunaCore::storm_version"() noexcept nogil
    GeneratorCore* core_module_generator "FortunaCore::module_generator"() except + nogil
    void core_module_seed "FortunaCore::module_seed"(uint64_t) except + nogil
    void core_module_entropy "FortunaCore::module_reseed_from_entropy"() except + nogil
    void core_after_fork "FortunaCore::mark_after_fork_child"() noexcept nogil

    int64_t core_signed "FortunaCore::sample_signed_unchecked"(
        GeneratorCore&, int, int64_t, int64_t, int64_t
    ) except + nogil
    uint64_t core_unsigned "FortunaCore::sample_unsigned_unchecked"(
        GeneratorCore&, int, uint64_t, uint64_t, double
    ) except + nogil
    double core_float "FortunaCore::sample_float_unchecked"(
        GeneratorCore&, int, double, double, double
    ) except + nogil
    bint core_bool "FortunaCore::sample_bool_unchecked"(
        GeneratorCore&, int, double
    ) except + nogil
    bint core_module_needs_prepare "FortunaCore::module_needs_prepare"() noexcept nogil
    void core_module_prepare "FortunaCore::module_prepare"() except + nogil
    double core_module_canonical_prepared "FortunaCore::module_canonical_prepared"() noexcept nogil
    void core_module_canonical_fill "FortunaCore::module_canonical_fill"(
        double*, size_t
    ) except + nogil
    double core_generator_canonical "FortunaCore::generator_canonical"(
        GeneratorCore&
    ) except + nogil
    void core_generator_canonical_fill "FortunaCore::generator_canonical_fill"(
        GeneratorCore&, double*, size_t
    ) except + nogil
    uint64_t core_module_random_below "FortunaCore::module_random_below_prepared"(
        uint64_t
    ) except + nogil
    uint64_t core_generator_random_below "FortunaCore::generator_random_below"(
        GeneratorCore&, uint64_t
    ) except + nogil
    uint64_t core_module_random_index "FortunaCore::module_random_index_prepared"(
        uint64_t
    ) except + nogil
    uint64_t core_generator_random_index "FortunaCore::generator_random_index"(
        GeneratorCore&, uint64_t
    ) except + nogil
    int64_t core_module_random_int "FortunaCore::module_random_int_prepared"(
        int64_t, int64_t
    ) except + nogil
    int64_t core_generator_random_int "FortunaCore::generator_random_int"(
        GeneratorCore&, int64_t, int64_t
    ) except + nogil
    int64_t core_module_random_range "FortunaCore::module_random_range_prepared"(
        int64_t, int64_t, int64_t
    ) except + nogil
    int64_t core_generator_random_range "FortunaCore::generator_random_range"(
        GeneratorCore&, int64_t, int64_t, int64_t
    ) except + nogil
    uint64_t core_module_roll_die "FortunaCore::module_roll_die_prepared"(
        uint64_t
    ) except + nogil
    uint64_t core_generator_roll_die "FortunaCore::generator_roll_die"(
        GeneratorCore&, uint64_t
    ) except + nogil
    uint64_t core_module_roll_dice "FortunaCore::module_roll_dice_prepared"(
        uint64_t, uint64_t
    ) except + nogil
    uint64_t core_generator_roll_dice "FortunaCore::generator_roll_dice"(
        GeneratorCore&, uint64_t, uint64_t
    ) except + nogil
    double core_module_random_float "FortunaCore::module_random_float_prepared"(
        double, double
    ) except + nogil
    double core_generator_random_float "FortunaCore::generator_random_float"(
        GeneratorCore&, double, double
    ) except + nogil
    double core_module_triangular "FortunaCore::module_triangular_prepared"(
        double, double, double
    ) except + nogil
    double core_generator_triangular "FortunaCore::generator_triangular"(
        GeneratorCore&, double, double, double
    ) except + nogil
    double core_module_exponential "FortunaCore::module_exponential_prepared"(
        double
    ) except + nogil
    double core_generator_exponential "FortunaCore::generator_exponential"(
        GeneratorCore&, double
    ) except + nogil
    double core_module_normal "FortunaCore::module_normal_prepared"(
        double, double
    ) except + nogil
    double core_generator_normal "FortunaCore::generator_normal"(
        GeneratorCore&, double, double
    ) except + nogil
    bint core_module_percent_true "FortunaCore::module_percent_true_prepared"(
        double
    ) except + nogil
    bint core_generator_percent_true "FortunaCore::generator_percent_true"(
        GeneratorCore&, double
    ) except + nogil
    bint core_module_bernoulli "FortunaCore::module_bernoulli_prepared"(
        double
    ) except + nogil
    bint core_generator_bernoulli "FortunaCore::generator_bernoulli"(
        GeneratorCore&, double
    ) except + nogil
    void core_validate_signed "FortunaCore::validate_signed"(
        int, int64_t, int64_t, int64_t
    ) except + nogil
    void core_validate_unsigned "FortunaCore::validate_unsigned"(
        int, uint64_t, uint64_t, double
    ) except + nogil
    void core_validate_float "FortunaCore::validate_float"(
        int, double, double, double
    ) except + nogil
    void core_validate_bool "FortunaCore::validate_bool"(
        int, double
    ) except + nogil


cdef int64_t _as_int64(object value, str name) except *:
    cdef object integer
    cdef int64_t result
    if isinstance(value, bool):
        raise TypeError(f"{name} must be an integer, not bool")
    if type(value) is int:
        result = value
        return result
    try:
        integer = operator.index(value)
    except TypeError as error:
        raise TypeError(f"{name} must be an integer") from error
    result = integer
    return result


cdef uint64_t _as_uint64(object value, str name) except *:
    cdef object integer
    cdef uint64_t result
    if isinstance(value, bool):
        raise TypeError(f"{name} must be an integer, not bool")
    if type(value) is int:
        if value < 0:
            raise ValueError(f"{name} must be nonnegative")
        result = value
        return result
    try:
        integer = operator.index(value)
    except TypeError as error:
        raise TypeError(f"{name} must be an integer") from error
    if integer < 0:
        raise ValueError(f"{name} must be nonnegative")
    result = integer
    return result


cdef uint64_t _below_high(object value) except *:
    cdef object integer
    cdef uint64_t result
    if isinstance(value, bool):
        raise TypeError("limit must be an integer, not bool")
    if type(value) is int:
        integer = value
    else:
        try:
            integer = operator.index(value)
        except TypeError as error:
            raise TypeError("limit must be an integer") from error
    if integer <= 0:
        raise ValueError("limit must be greater than zero")
    if integer > 2**64:
        raise OverflowError("limit must not exceed 2**64")
    result = integer - 1
    return result


cdef Py_ssize_t _as_count(object value) except *:
    cdef object integer
    cdef Py_ssize_t result
    if isinstance(value, bool):
        raise TypeError("count must be an integer, not bool")
    if type(value) is int:
        if value < 0:
            raise ValueError("count must be nonnegative")
        result = value
        return result
    try:
        integer = operator.index(value)
    except TypeError as error:
        raise TypeError("count must be an integer") from error
    if integer < 0:
        raise ValueError("count must be nonnegative")
    result = integer
    return result


cdef double _as_double(object value, str name) except *:
    if type(value) is float:
        return value
    if type(value) is int:
        return float(value)
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")
    return float(value)


cdef GeneratorCore* _module() except *:
    cdef GeneratorCore* result
    with nogil:
        result = core_module_generator()
    return result


cdef inline void _prepare_module_scalar() except *:
    if core_module_needs_prepare():
        with nogil:
            core_module_prepare()


cdef object _signed_dispatch(
    GeneratorCore* generator,
    int operation,
    int64_t a,
    int64_t b,
    int64_t c,
    bint bulk,
    Py_ssize_t size,
):
    cdef int64_t scalar
    cdef vector[int64_t] values
    cdef Py_ssize_t index
    with nogil:
        core_validate_signed(operation, a, b, c)
    if not bulk:
        with nogil:
            scalar = core_signed(generator[0], operation, a, b, c)
        return scalar
    values.resize(size)
    with nogil:
        for index in range(size):
            values[index] = core_signed(generator[0], operation, a, b, c)
    return list(values)


cdef object _signed_result(
    GeneratorCore* generator,
    int operation,
    int64_t a,
    int64_t b,
    int64_t c,
    object count,
):
    if count is None:
        return _signed_dispatch(generator, operation, a, b, c, False, 0)
    return _signed_dispatch(generator, operation, a, b, c, True, _as_count(count))


cdef object _signed_generator_result(
    GeneratorCore* generator,
    int operation,
    int64_t a,
    int64_t b,
    int64_t c,
    object count,
):
    cdef bint bulk = count is not None
    cdef Py_ssize_t size = _as_count(count) if bulk else 0
    with nogil:
        generator.lock()
    try:
        return _signed_dispatch(generator, operation, a, b, c, bulk, size)
    finally:
        with nogil:
            generator.unlock()


cdef object _unsigned_dispatch(
    GeneratorCore* generator,
    int operation,
    uint64_t a,
    uint64_t b,
    double parameter,
    bint bulk,
    Py_ssize_t size,
):
    cdef uint64_t scalar
    cdef vector[uint64_t] values
    cdef Py_ssize_t index
    with nogil:
        core_validate_unsigned(operation, a, b, parameter)
    if not bulk:
        with nogil:
            scalar = core_unsigned(generator[0], operation, a, b, parameter)
        return scalar
    values.resize(size)
    with nogil:
        for index in range(size):
            values[index] = core_unsigned(generator[0], operation, a, b, parameter)
    return list(values)


cdef object _unsigned_result(
    GeneratorCore* generator,
    int operation,
    uint64_t a,
    uint64_t b,
    double parameter,
    object count,
):
    if count is None:
        return _unsigned_dispatch(generator, operation, a, b, parameter, False, 0)
    return _unsigned_dispatch(
        generator, operation, a, b, parameter, True, _as_count(count)
    )


cdef object _unsigned_generator_result(
    GeneratorCore* generator,
    int operation,
    uint64_t a,
    uint64_t b,
    double parameter,
    object count,
):
    cdef bint bulk = count is not None
    cdef Py_ssize_t size = _as_count(count) if bulk else 0
    with nogil:
        generator.lock()
    try:
        return _unsigned_dispatch(generator, operation, a, b, parameter, bulk, size)
    finally:
        with nogil:
            generator.unlock()


cdef object _float_dispatch(
    GeneratorCore* generator,
    int operation,
    double a,
    double b,
    double c,
    bint bulk,
    Py_ssize_t size,
):
    cdef double scalar
    cdef vector[double] values
    cdef Py_ssize_t index
    with nogil:
        core_validate_float(operation, a, b, c)
    if not bulk:
        with nogil:
            scalar = core_float(generator[0], operation, a, b, c)
        return scalar
    values.resize(size)
    with nogil:
        for index in range(size):
            values[index] = core_float(generator[0], operation, a, b, c)
    return list(values)


cdef object _float_result(
    GeneratorCore* generator,
    int operation,
    double a,
    double b,
    double c,
    object count,
):
    if count is None:
        return _float_dispatch(generator, operation, a, b, c, False, 0)
    return _float_dispatch(generator, operation, a, b, c, True, _as_count(count))


cdef object _float_generator_result(
    GeneratorCore* generator,
    int operation,
    double a,
    double b,
    double c,
    object count,
):
    cdef bint bulk = count is not None
    cdef Py_ssize_t size = _as_count(count) if bulk else 0
    with nogil:
        generator.lock()
    try:
        return _float_dispatch(generator, operation, a, b, c, bulk, size)
    finally:
        with nogil:
            generator.unlock()


cdef list _canonical_list(vector[double]& values):
    cdef Py_ssize_t size = <Py_ssize_t>values.size()
    cdef Py_ssize_t index
    cdef list result = PyList_New(size)
    cdef PyObject* item
    for index in range(size):
        item = raw_float_from_double(values[index])
        raw_list_set_item(<PyObject*>result, index, item)
    return result


cdef list _module_canonical_bulk(object count):
    cdef vector[double] values
    cdef Py_ssize_t size = _as_count(count)
    values.resize(size)
    if size:
        with nogil:
            core_module_canonical_fill(&values[0], <size_t>size)
    return _canonical_list(values)


cdef list _generator_canonical_bulk(GeneratorCore* generator, object count):
    cdef vector[double] values
    cdef Py_ssize_t size = _as_count(count)
    values.resize(size)
    if size:
        with nogil:
            core_generator_canonical_fill(generator[0], &values[0], <size_t>size)
    return _canonical_list(values)


cdef object _bool_dispatch(
    GeneratorCore* generator,
    int operation,
    double parameter,
    bint bulk,
    Py_ssize_t size,
):
    cdef bint scalar
    cdef vector[uint8_t] values
    cdef Py_ssize_t index
    with nogil:
        core_validate_bool(operation, parameter)
    if not bulk:
        with nogil:
            scalar = core_bool(generator[0], operation, parameter)
        return bool(scalar)
    values.resize(size)
    with nogil:
        for index in range(size):
            values[index] = <uint8_t>core_bool(generator[0], operation, parameter)
    return [bool(values[index]) for index in range(size)]


cdef object _bool_result(
    GeneratorCore* generator,
    int operation,
    double parameter,
    object count,
):
    if count is None:
        return _bool_dispatch(generator, operation, parameter, False, 0)
    return _bool_dispatch(generator, operation, parameter, True, _as_count(count))


cdef object _bool_generator_result(
    GeneratorCore* generator,
    int operation,
    double parameter,
    object count,
):
    cdef bint bulk = count is not None
    cdef Py_ssize_t size = _as_count(count) if bulk else 0
    with nogil:
        generator.lock()
    try:
        return _bool_dispatch(generator, operation, parameter, bulk, size)
    finally:
        with nogil:
            generator.unlock()


cdef void _shuffle_knuth_b(GeneratorCore* generator, object data, bint synchronize) except *:
    cdef Py_ssize_t last
    cdef Py_ssize_t position
    cdef Py_ssize_t other
    if not isinstance(data, MutableSequence):
        raise TypeError("data must be a mutable sequence")
    last = len(data) - 1
    if last <= 0:
        return
    if synchronize:
        with nogil:
            generator.lock()
        try:
            # Entropy-managed generators may need process-local reseeding after
            # fork. Do that outside the GIL before the Python-object swap loop.
            with nogil:
                generator.prepare()
            for position in range(last - 1, -1, -1):
                other = <Py_ssize_t>core_unsigned(
                    generator[0], 0, <uint64_t>position, <uint64_t>last, 0.0
                )
                data[position], data[other] = data[other], data[position]
        finally:
            with nogil:
                generator.unlock()
        return
    for position in range(last - 1, -1, -1):
        other = <Py_ssize_t>core_unsigned(
            generator[0], 0, <uint64_t>position, <uint64_t>last, 0.0
        )
        data[position], data[other] = data[other], data[position]


cdef void _shuffle_fisher_yates(
    GeneratorCore* generator, object data, bint synchronize
) except *:
    cdef Py_ssize_t last
    cdef Py_ssize_t position
    cdef Py_ssize_t other
    if not isinstance(data, MutableSequence):
        raise TypeError("data must be a mutable sequence")
    last = len(data) - 1
    if last <= 0:
        return
    if synchronize:
        with nogil:
            generator.lock()
        try:
            with nogil:
                generator.prepare()
            for position in range(last, 0, -1):
                other = <Py_ssize_t>core_unsigned(
                    generator[0], 0, 0, <uint64_t>position, 0.0
                )
                data[position], data[other] = data[other], data[position]
        finally:
            with nogil:
                generator.unlock()
        return
    for position in range(last, 0, -1):
        other = <Py_ssize_t>core_unsigned(
            generator[0], 0, 0, <uint64_t>position, 0.0
        )
        data[position], data[other] = data[other], data[position]


cdef bytes _stream_payload(object stream_id):
    cdef bytes magnitude
    cdef bytes encoded
    cdef bytes sign
    if isinstance(stream_id, bool):
        raise TypeError("stream_id must be int, str, or bytes, not bool")
    if isinstance(stream_id, int):
        sign = b"-" if stream_id < 0 else b"+"
        magnitude = abs(stream_id).to_bytes(
            max(1, (abs(stream_id).bit_length() + 7) // 8), "big"
        )
        return b"i" + sign + len(magnitude).to_bytes(8, "big") + magnitude
    if isinstance(stream_id, str):
        encoded = stream_id.encode("utf-8")
        return b"s" + len(encoded).to_bytes(8, "big") + encoded
    if isinstance(stream_id, bytes):
        return b"b" + len(stream_id).to_bytes(8, "big") + stream_id
    raise TypeError("stream_id must be int, str, or bytes")


cdef uint64_t _stream_seed(object root_seed, object stream_id) except *:
    cdef uint64_t checked_root = _as_uint64(root_seed, "root_seed")
    cdef bytes payload = (
        b"Fortuna\x006.0\x00for_stream\x00"
        + int(checked_root).to_bytes(8, "big")
        + _stream_payload(stream_id)
    )
    return int.from_bytes(sha256(payload).digest()[:8], "big")


cdef class Generator:
    """Owned random engine with deterministic and entropy construction modes."""

    cdef GeneratorCore* _generator

    def __cinit__(self, seed=0):
        self._generator = NULL
        self._generator = new GeneratorCore(_as_uint64(seed, "seed"))

    def __dealloc__(self):
        if self._generator != NULL:
            del self._generator

    @classmethod
    def from_entropy(cls):
        cdef Generator result = Generator(0)
        with nogil:
            result._generator.reseed_from_entropy()
        return result

    @classmethod
    def for_stream(cls, root_seed, stream_id):
        return Generator(_stream_seed(root_seed, stream_id))

    def seed(self, value=0):
        cdef uint64_t checked = _as_uint64(value, "seed")
        with nogil:
            self._generator.lock()
        try:
            with nogil:
                self._generator.seed(checked)
        finally:
            with nogil:
                self._generator.unlock()

    def reseed_from_entropy(self):
        with nogil:
            self._generator.lock()
        try:
            with nogil:
                self._generator.reseed_from_entropy()
        finally:
            with nogil:
                self._generator.unlock()

    def percent_true(self, percent=50.0, *, count=None):
        cdef double checked = _as_double(percent, "percent")
        cdef bint scalar
        if count is not None:
            return _bool_generator_result(self._generator, 0, checked, count)
        with nogil:
            scalar = core_generator_percent_true(self._generator[0], checked)
        return bool(scalar)

    def bernoulli_variate(self, probability=0.5, *, count=None):
        cdef double checked = _as_double(probability, "probability")
        cdef bint scalar
        if count is not None:
            return _bool_generator_result(self._generator, 1, checked, count)
        with nogil:
            scalar = core_generator_bernoulli(self._generator[0], checked)
        return bool(scalar)

    def random_below(self, limit, *, count=None):
        cdef uint64_t high = _below_high(limit)
        cdef uint64_t scalar
        if count is not None:
            return _unsigned_generator_result(self._generator, 0, 0, high, 0.0, count)
        with nogil:
            scalar = core_generator_random_below(self._generator[0], high)
        return scalar

    def random_index(self, size, *, count=None):
        cdef uint64_t checked = _as_uint64(size, "size")
        cdef uint64_t scalar
        if count is not None:
            return _unsigned_generator_result(self._generator, 1, checked, 0, 0.0, count)
        with nogil:
            scalar = core_generator_random_index(self._generator[0], checked)
        return scalar

    def random_int(self, low, high, *, count=None):
        cdef int64_t checked_low = _as_int64(low, "low")
        cdef int64_t checked_high = _as_int64(high, "high")
        cdef int64_t scalar
        if count is not None:
            return _signed_generator_result(
                self._generator, 0, checked_low, checked_high, 0, count
            )
        with nogil:
            scalar = core_generator_random_int(self._generator[0], checked_low, checked_high)
        return scalar

    def random_uint(self, low, high, *, count=None):
        return _unsigned_generator_result(self._generator, 0, _as_uint64(low, "low"),
                                          _as_uint64(high, "high"), 0.0, count)

    def random_range(self, start, stop=None, step=1, *, count=None):
        cdef int64_t checked_start
        cdef int64_t checked_stop
        cdef int64_t checked_step
        cdef int64_t scalar
        if stop is None:
            stop = start
            start = 0
        checked_start = _as_int64(start, "start")
        checked_stop = _as_int64(stop, "stop")
        checked_step = _as_int64(step, "step")
        if count is not None:
            return _signed_generator_result(
                self._generator, 1, checked_start, checked_stop, checked_step, count
            )
        with nogil:
            scalar = core_generator_random_range(
                self._generator[0], checked_start, checked_stop, checked_step
            )
        return scalar

    def d(self, sides=20, *, count=None):
        cdef uint64_t checked = _as_uint64(sides, "sides")
        cdef uint64_t scalar
        if count is not None:
            return _unsigned_generator_result(self._generator, 2, checked, 0, 0.0, count)
        with nogil:
            scalar = core_generator_roll_die(self._generator[0], checked)
        return scalar

    def dice(self, rolls=1, sides=20, *, count=None):
        cdef uint64_t checked_rolls = _as_uint64(rolls, "rolls")
        cdef uint64_t checked_sides = _as_uint64(sides, "sides")
        cdef uint64_t scalar
        if count is not None:
            return _unsigned_generator_result(
                self._generator, 3, checked_rolls, checked_sides, 0.0, count
            )
        with nogil:
            scalar = core_generator_roll_dice(
                self._generator[0], checked_rolls, checked_sides
            )
        return scalar

    def ability_dice(self, rolls=4, *, count=None):
        return _unsigned_generator_result(
            self._generator, 4, _as_uint64(rolls, "rolls"), 0, 0.0, count
        )

    def plus_or_minus(self, radius=1, *, count=None):
        return _signed_generator_result(
            self._generator, 2, _as_int64(radius, "radius"), 0, 0, count
        )

    def plus_or_minus_triangular(self, radius=1, *, count=None):
        return _signed_generator_result(
            self._generator, 3, _as_int64(radius, "radius"), 0, 0, count
        )

    def plus_or_minus_normal(self, radius=1, *, count=None):
        return _signed_generator_result(
            self._generator, 4, _as_int64(radius, "radius"), 0, 0, count
        )

    def canonical(self, *, count=None):
        cdef double scalar
        if count is not None:
            return _generator_canonical_bulk(self._generator, count)
        with nogil:
            scalar = core_generator_canonical(self._generator[0])
        return scalar

    def random_float(self, low=0.0, high=1.0, *, count=None):
        cdef double checked_low = _as_double(low, "low")
        cdef double checked_high = _as_double(high, "high")
        cdef double scalar
        if count is not None:
            return _float_generator_result(
                self._generator, 1, checked_low, checked_high, 0.0, count
            )
        with nogil:
            scalar = core_generator_random_float(self._generator[0], checked_low, checked_high)
        return scalar

    def triangular(self, low, high, mode, *, count=None):
        cdef double checked_low = _as_double(low, "low")
        cdef double checked_high = _as_double(high, "high")
        cdef double checked_mode = _as_double(mode, "mode")
        cdef double scalar
        if count is not None:
            return _float_generator_result(
                self._generator, 2, checked_low, checked_high, checked_mode, count
            )
        with nogil:
            scalar = core_generator_triangular(
                self._generator[0], checked_low, checked_high, checked_mode
            )
        return scalar

    def beta_variate(self, alpha, beta, *, count=None):
        return _float_generator_result(self._generator, 3, _as_double(alpha, "alpha"),
                                       _as_double(beta, "beta"), 0.0, count)

    def pareto_variate(self, alpha, *, count=None):
        return _float_generator_result(
            self._generator, 4, _as_double(alpha, "alpha"), 0.0, 0.0, count
        )

    def vonmises_variate(self, mu, kappa, *, count=None):
        return _float_generator_result(self._generator, 5, _as_double(mu, "mu"),
                                       _as_double(kappa, "kappa"), 0.0, count)

    def binomial_variate(self, trials, probability, *, count=None):
        return _unsigned_generator_result(self._generator, 5, _as_uint64(trials, "trials"), 0,
                                          _as_double(probability, "probability"), count)

    def negative_binomial_variate(self, successes, probability, *, count=None):
        return _unsigned_generator_result(self._generator, 6,
                                          _as_uint64(successes, "successes"), 0,
                                          _as_double(probability, "probability"), count)

    def geometric_variate(self, probability, *, count=None):
        return _unsigned_generator_result(self._generator, 7, 0, 0,
                                          _as_double(probability, "probability"), count)

    def poisson_variate(self, mean, *, count=None):
        return _unsigned_generator_result(
            self._generator, 8, 0, 0, _as_double(mean, "mean"), count
        )

    def exponential_variate(self, rate, *, count=None):
        cdef double checked = _as_double(rate, "rate")
        cdef double scalar
        if count is not None:
            return _float_generator_result(self._generator, 6, checked, 0.0, 0.0, count)
        with nogil:
            scalar = core_generator_exponential(self._generator[0], checked)
        return scalar

    def gamma_variate(self, shape, scale, *, count=None):
        return _float_generator_result(self._generator, 7, _as_double(shape, "shape"),
                                       _as_double(scale, "scale"), 0.0, count)

    def weibull_variate(self, shape, scale, *, count=None):
        return _float_generator_result(self._generator, 8, _as_double(shape, "shape"),
                                       _as_double(scale, "scale"), 0.0, count)

    def normal_variate(self, mean, std_dev, *, count=None):
        cdef double checked_mean = _as_double(mean, "mean")
        cdef double checked_deviation = _as_double(std_dev, "std_dev")
        cdef double scalar
        if count is not None:
            return _float_generator_result(
                self._generator, 9, checked_mean, checked_deviation, 0.0, count
            )
        with nogil:
            scalar = core_generator_normal(
                self._generator[0], checked_mean, checked_deviation
            )
        return scalar

    def log_normal_variate(self, log_mean, log_deviation, *, count=None):
        return _float_generator_result(self._generator, 10, _as_double(log_mean, "log_mean"),
                                       _as_double(log_deviation, "log_deviation"), 0.0, count)

    def extreme_value_variate(self, location, scale, *, count=None):
        return _float_generator_result(self._generator, 11, _as_double(location, "location"),
                                       _as_double(scale, "scale"), 0.0, count)

    def chi_squared_variate(self, degrees_of_freedom, *, count=None):
        return _float_generator_result(
            self._generator, 12,
            _as_double(degrees_of_freedom, "degrees_of_freedom"), 0.0, 0.0, count
        )

    def cauchy_variate(self, location, scale, *, count=None):
        return _float_generator_result(self._generator, 13, _as_double(location, "location"),
                                       _as_double(scale, "scale"), 0.0, count)

    def fisher_f_variate(self, degrees_1, degrees_2, *, count=None):
        return _float_generator_result(self._generator, 14,
                                       _as_double(degrees_1, "degrees_1"),
                                       _as_double(degrees_2, "degrees_2"), 0.0, count)

    def student_t_variate(self, degrees_of_freedom, *, count=None):
        return _float_generator_result(
            self._generator, 15,
            _as_double(degrees_of_freedom, "degrees_of_freedom"), 0.0, 0.0, count
        )

    def front_triangular(self, size, *, count=None):
        return _unsigned_generator_result(self._generator, 9, _as_uint64(size, "size"), 0, 0.0, count)

    def center_triangular(self, size, *, count=None):
        return _unsigned_generator_result(self._generator, 10, _as_uint64(size, "size"), 0, 0.0, count)

    def back_triangular(self, size, *, count=None):
        return _unsigned_generator_result(self._generator, 11, _as_uint64(size, "size"), 0, 0.0, count)

    def mixed_triangular(self, size, *, count=None):
        return _unsigned_generator_result(self._generator, 12, _as_uint64(size, "size"), 0, 0.0, count)

    def front_exponential(self, size, *, count=None):
        return _unsigned_generator_result(self._generator, 13, _as_uint64(size, "size"), 0, 0.0, count)

    def center_normal(self, size, *, count=None):
        return _unsigned_generator_result(self._generator, 14, _as_uint64(size, "size"), 0, 0.0, count)

    def back_exponential(self, size, *, count=None):
        return _unsigned_generator_result(self._generator, 15, _as_uint64(size, "size"), 0, 0.0, count)

    def mixed_exponential_normal(self, size, *, count=None):
        return _unsigned_generator_result(self._generator, 16, _as_uint64(size, "size"), 0, 0.0, count)

    def front_poisson(self, size, *, count=None):
        return _unsigned_generator_result(self._generator, 17, _as_uint64(size, "size"), 0, 0.0, count)

    def edge_poisson(self, size, *, count=None):
        return _unsigned_generator_result(self._generator, 18, _as_uint64(size, "size"), 0, 0.0, count)

    def back_poisson(self, size, *, count=None):
        return _unsigned_generator_result(self._generator, 19, _as_uint64(size, "size"), 0, 0.0, count)

    def quantum_monty(self, size, *, count=None):
        return _unsigned_generator_result(self._generator, 20, _as_uint64(size, "size"), 0, 0.0, count)

    def random_value(self, data):
        data = tuple(data)
        if not data:
            raise ValueError("data must not be empty")
        return data[self.random_index(len(data))]

    def shuffle(self, data):
        _shuffle_knuth_b(self._generator, data, True)

    def sample(self, population, k):
        cdef Py_ssize_t checked_k = _as_count(k)
        cdef list working = list(population)
        cdef Py_ssize_t position
        cdef Py_ssize_t other
        if checked_k > len(working):
            raise ValueError("sample size exceeds population")
        for position in range(checked_k):
            other = position + self.random_index(len(working) - position)
            working[position], working[other] = working[other], working[position]
        return working[:checked_k]


def storm_version():
    return core_storm_version().decode("ascii")


def seed(value=0):
    cdef uint64_t checked = _as_uint64(value, "seed")
    with nogil:
        core_module_seed(checked)


def from_entropy():
    return Generator.from_entropy()


def for_stream(root_seed, stream_id):
    return Generator.for_stream(root_seed, stream_id)


def shuffle(data):
    _shuffle_knuth_b(_module(), data, False)


def _benchmark_shuffle_knuth_b(data):
    """Internal benchmark hook; not part of Fortuna's public API."""
    _shuffle_knuth_b(_module(), data, False)


def _benchmark_shuffle_fisher_yates(data):
    """Internal benchmark hook; not part of Fortuna's public API."""
    _shuffle_fisher_yates(_module(), data, False)


def percent_true(percent=50.0, *, count=None):
    cdef double checked = _as_double(percent, "percent")
    cdef bint scalar
    if count is not None:
        return _bool_result(_module(), 0, checked, count)
    _prepare_module_scalar()
    scalar = core_module_percent_true(checked)
    return bool(scalar)


def bernoulli_variate(probability=0.5, *, count=None):
    cdef double checked = _as_double(probability, "probability")
    cdef bint scalar
    if count is not None:
        return _bool_result(_module(), 1, checked, count)
    _prepare_module_scalar()
    scalar = core_module_bernoulli(checked)
    return bool(scalar)


def random_below(limit, *, count=None):
    cdef uint64_t high = _below_high(limit)
    cdef uint64_t scalar
    if count is not None:
        return _unsigned_result(_module(), 0, 0, high, 0.0, count)
    _prepare_module_scalar()
    scalar = core_module_random_below(high)
    return scalar


def random_index(size, *, count=None):
    cdef uint64_t checked = _as_uint64(size, "size")
    cdef uint64_t scalar
    if count is not None:
        return _unsigned_result(_module(), 1, checked, 0, 0.0, count)
    _prepare_module_scalar()
    scalar = core_module_random_index(checked)
    return scalar


def random_int(low, high, *, count=None):
    cdef int64_t checked_low = _as_int64(low, "low")
    cdef int64_t checked_high = _as_int64(high, "high")
    cdef int64_t scalar
    if count is not None:
        return _signed_result(_module(), 0, checked_low, checked_high, 0, count)
    _prepare_module_scalar()
    scalar = core_module_random_int(checked_low, checked_high)
    return scalar


def random_uint(low, high, *, count=None):
    return _unsigned_result(_module(), 0, _as_uint64(low, "low"),
                            _as_uint64(high, "high"), 0.0, count)


def random_range(start, stop=None, step=1, *, count=None):
    cdef int64_t checked_start
    cdef int64_t checked_stop
    cdef int64_t checked_step
    cdef int64_t scalar
    if stop is None:
        stop = start
        start = 0
    checked_start = _as_int64(start, "start")
    checked_stop = _as_int64(stop, "stop")
    checked_step = _as_int64(step, "step")
    if count is not None:
        return _signed_result(_module(), 1, checked_start, checked_stop, checked_step, count)
    _prepare_module_scalar()
    scalar = core_module_random_range(checked_start, checked_stop, checked_step)
    return scalar


def d(sides=20, *, count=None):
    cdef uint64_t checked = _as_uint64(sides, "sides")
    cdef uint64_t scalar
    if count is not None:
        return _unsigned_result(_module(), 2, checked, 0, 0.0, count)
    _prepare_module_scalar()
    scalar = core_module_roll_die(checked)
    return scalar


def dice(rolls=1, sides=20, *, count=None):
    cdef uint64_t checked_rolls = _as_uint64(rolls, "rolls")
    cdef uint64_t checked_sides = _as_uint64(sides, "sides")
    cdef uint64_t scalar
    if count is not None:
        return _unsigned_result(
            _module(), 3, checked_rolls, checked_sides, 0.0, count
        )
    _prepare_module_scalar()
    scalar = core_module_roll_dice(checked_rolls, checked_sides)
    return scalar


def ability_dice(rolls=4, *, count=None):
    return _unsigned_result(_module(), 4, _as_uint64(rolls, "rolls"), 0, 0.0, count)


def plus_or_minus(radius=1, *, count=None):
    return _signed_result(_module(), 2, _as_int64(radius, "radius"), 0, 0, count)


def plus_or_minus_triangular(radius=1, *, count=None):
    return _signed_result(_module(), 3, _as_int64(radius, "radius"), 0, 0, count)


def plus_or_minus_normal(radius=1, *, count=None):
    return _signed_result(_module(), 4, _as_int64(radius, "radius"), 0, 0, count)


def canonical(*, count=None):
    if count is not None:
        return _module_canonical_bulk(count)
    if core_module_needs_prepare():
        with nogil:
            core_module_prepare()
    return core_module_canonical_prepared()


def random_float(low=0.0, high=1.0, *, count=None):
    cdef double checked_low = _as_double(low, "low")
    cdef double checked_high = _as_double(high, "high")
    cdef double scalar
    if count is not None:
        return _float_result(_module(), 1, checked_low, checked_high, 0.0, count)
    _prepare_module_scalar()
    scalar = core_module_random_float(checked_low, checked_high)
    return scalar


def triangular(low, high, mode, *, count=None):
    cdef double checked_low = _as_double(low, "low")
    cdef double checked_high = _as_double(high, "high")
    cdef double checked_mode = _as_double(mode, "mode")
    cdef double scalar
    if count is not None:
        return _float_result(
            _module(), 2, checked_low, checked_high, checked_mode, count
        )
    _prepare_module_scalar()
    scalar = core_module_triangular(checked_low, checked_high, checked_mode)
    return scalar


def beta_variate(alpha, beta, *, count=None):
    return _float_result(_module(), 3, _as_double(alpha, "alpha"),
                         _as_double(beta, "beta"), 0.0, count)


def pareto_variate(alpha, *, count=None):
    return _float_result(_module(), 4, _as_double(alpha, "alpha"), 0.0, 0.0, count)


def vonmises_variate(mu, kappa, *, count=None):
    return _float_result(_module(), 5, _as_double(mu, "mu"),
                         _as_double(kappa, "kappa"), 0.0, count)


def binomial_variate(trials, probability, *, count=None):
    return _unsigned_result(_module(), 5, _as_uint64(trials, "trials"), 0,
                            _as_double(probability, "probability"), count)


def negative_binomial_variate(successes, probability, *, count=None):
    return _unsigned_result(_module(), 6, _as_uint64(successes, "successes"), 0,
                            _as_double(probability, "probability"), count)


def geometric_variate(probability, *, count=None):
    return _unsigned_result(_module(), 7, 0, 0, _as_double(probability, "probability"), count)


def poisson_variate(mean, *, count=None):
    return _unsigned_result(_module(), 8, 0, 0, _as_double(mean, "mean"), count)


def exponential_variate(rate, *, count=None):
    cdef double checked = _as_double(rate, "rate")
    cdef double scalar
    if count is not None:
        return _float_result(_module(), 6, checked, 0.0, 0.0, count)
    _prepare_module_scalar()
    scalar = core_module_exponential(checked)
    return scalar


def gamma_variate(shape, scale, *, count=None):
    return _float_result(_module(), 7, _as_double(shape, "shape"),
                         _as_double(scale, "scale"), 0.0, count)


def weibull_variate(shape, scale, *, count=None):
    return _float_result(_module(), 8, _as_double(shape, "shape"),
                         _as_double(scale, "scale"), 0.0, count)


def normal_variate(mean, std_dev, *, count=None):
    cdef double checked_mean = _as_double(mean, "mean")
    cdef double checked_deviation = _as_double(std_dev, "std_dev")
    cdef double scalar
    if count is not None:
        return _float_result(
            _module(), 9, checked_mean, checked_deviation, 0.0, count
        )
    _prepare_module_scalar()
    scalar = core_module_normal(checked_mean, checked_deviation)
    return scalar


def log_normal_variate(log_mean, log_deviation, *, count=None):
    return _float_result(_module(), 10, _as_double(log_mean, "log_mean"),
                         _as_double(log_deviation, "log_deviation"), 0.0, count)


def extreme_value_variate(location, scale, *, count=None):
    return _float_result(_module(), 11, _as_double(location, "location"),
                         _as_double(scale, "scale"), 0.0, count)


def chi_squared_variate(degrees_of_freedom, *, count=None):
    return _float_result(_module(), 12, _as_double(degrees_of_freedom, "degrees_of_freedom"),
                         0.0, 0.0, count)


def cauchy_variate(location, scale, *, count=None):
    return _float_result(_module(), 13, _as_double(location, "location"),
                         _as_double(scale, "scale"), 0.0, count)


def fisher_f_variate(degrees_1, degrees_2, *, count=None):
    return _float_result(_module(), 14, _as_double(degrees_1, "degrees_1"),
                         _as_double(degrees_2, "degrees_2"), 0.0, count)


def student_t_variate(degrees_of_freedom, *, count=None):
    return _float_result(_module(), 15, _as_double(degrees_of_freedom, "degrees_of_freedom"),
                         0.0, 0.0, count)


def front_triangular(size, *, count=None):
    return _unsigned_result(_module(), 9, _as_uint64(size, "size"), 0, 0.0, count)


def center_triangular(size, *, count=None):
    return _unsigned_result(_module(), 10, _as_uint64(size, "size"), 0, 0.0, count)


def back_triangular(size, *, count=None):
    return _unsigned_result(_module(), 11, _as_uint64(size, "size"), 0, 0.0, count)


def mixed_triangular(size, *, count=None):
    return _unsigned_result(_module(), 12, _as_uint64(size, "size"), 0, 0.0, count)


def front_exponential(size, *, count=None):
    return _unsigned_result(_module(), 13, _as_uint64(size, "size"), 0, 0.0, count)


def center_normal(size, *, count=None):
    return _unsigned_result(_module(), 14, _as_uint64(size, "size"), 0, 0.0, count)


def back_exponential(size, *, count=None):
    return _unsigned_result(_module(), 15, _as_uint64(size, "size"), 0, 0.0, count)


def mixed_exponential_normal(size, *, count=None):
    return _unsigned_result(_module(), 16, _as_uint64(size, "size"), 0, 0.0, count)


def front_poisson(size, *, count=None):
    return _unsigned_result(_module(), 17, _as_uint64(size, "size"), 0, 0.0, count)


def edge_poisson(size, *, count=None):
    return _unsigned_result(_module(), 18, _as_uint64(size, "size"), 0, 0.0, count)


def back_poisson(size, *, count=None):
    return _unsigned_result(_module(), 19, _as_uint64(size, "size"), 0, 0.0, count)


def quantum_monty(size, *, count=None):
    return _unsigned_result(_module(), 20, _as_uint64(size, "size"), 0, 0.0, count)


def _after_fork_child():
    with nogil:
        core_after_fork()


if hasattr(os, "register_at_fork"):
    os.register_at_fork(after_in_child=_after_fork_child)
