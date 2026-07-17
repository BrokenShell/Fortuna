import multiprocessing
import os
from collections import deque

import pytest

from Fortuna import Generator


class _IndexValue:
    def __init__(self, value):
        self.value = value

    def __index__(self):
        return self.value


class _OverrideGenerator(Generator):
    def __init__(self, seed=0):
        self.indices = deque()
        self.calls = []

    def random_index(self, size, *, count=None):
        self.calls.append((size, count))
        return self.indices.popleft()


def _override_generator(*indices, seed=0):
    generator = _OverrideGenerator(seed)
    generator.indices.extend(indices)
    return generator


def test_direct_subclass_random_value_accepts_and_validates_index_override():
    generator = _override_generator(_IndexValue(1))

    assert generator.random_value(value for value in ("zero", "one")) == "one"
    assert generator.calls == [(2, None)]


@pytest.mark.parametrize(
    ("result", "error", "message"),
    [
        (False, TypeError, "generated index must be an integer, not bool"),
        (object(), TypeError, "generated index must be an integer"),
        (-1, ValueError, r"outside \[0, 2\)"),
        (2, ValueError, r"outside \[0, 2\)"),
    ],
)
def test_direct_subclass_random_value_rejects_invalid_index_override(
    result,
    error,
    message,
):
    generator = _override_generator(result, 0)

    with pytest.raises(error, match=message):
        generator.random_value(("zero", "one"))

    assert generator.calls == [(2, None)]


def test_direct_subclass_random_value_errors_before_requesting_an_index():
    generator = _override_generator(0)

    with pytest.raises(ValueError, match="data must not be empty"):
        generator.random_value(())

    def broken_values():
        yield "first"
        raise RuntimeError("broken iterable")

    with pytest.raises(RuntimeError, match="broken iterable"):
        generator.random_value(broken_values())

    assert generator.calls == []


def test_direct_subclass_sample_accepts_and_validates_each_index_override():
    generator = _override_generator(_IndexValue(3), _IndexValue(2), _IndexValue(0))

    assert generator.sample(range(5), 3) == [3, 0, 2]
    assert generator.calls == [(5, None), (4, None), (3, None)]


@pytest.mark.parametrize(
    ("result", "error", "message"),
    [
        (False, TypeError, "generated index must be an integer, not bool"),
        (object(), TypeError, "generated index must be an integer"),
        (-1, ValueError, r"outside \[0, 5\)"),
        (5, ValueError, r"outside \[0, 5\)"),
    ],
)
def test_direct_subclass_sample_rejects_invalid_index_override(
    result,
    error,
    message,
):
    generator = _override_generator(result, 0)

    with pytest.raises(error, match=message):
        generator.sample(range(5), 1)

    assert generator.calls == [(5, None)]


def test_direct_subclass_sample_validates_inputs_before_requesting_an_index():
    generator = _override_generator(0)
    materialized = False

    def population():
        nonlocal materialized
        materialized = True
        yield 1

    class BrokenCount:
        def __index__(self):
            raise RuntimeError("broken count")

    with pytest.raises(RuntimeError, match="broken count"):
        generator.sample(population(), BrokenCount())
    assert not materialized

    with pytest.raises(ValueError, match="sample size exceeds population"):
        generator.sample(range(2), 3)

    assert generator.calls == []


def test_direct_subclass_shuffle_deliberately_keeps_native_schedule():
    generator = _override_generator(False, seed=8128)
    values = list(range(10))

    generator.shuffle(values)

    assert sorted(values) == list(range(10))
    assert generator.calls == []


def test_generator_class_factories_preserve_subclass_and_constructor_calls():
    class RecordingGenerator(Generator):
        constructor_seeds = []

        def __init__(self, seed=0):
            self.constructor_seed = seed
            self.constructor_seeds.append(seed)

    entropy = RecordingGenerator.from_entropy()
    stream = RecordingGenerator.for_stream(42, "worker-3")
    stream_control = Generator.for_stream(42, "worker-3")

    assert type(entropy) is RecordingGenerator
    assert entropy.constructor_seed == 0
    assert type(stream) is RecordingGenerator
    assert stream.constructor_seed != 0
    assert stream.random_below(2**64) == stream_control.random_below(2**64)
    assert RecordingGenerator.constructor_seeds == [0, stream.constructor_seed]


@pytest.mark.parametrize("factory", ["from_entropy", "for_stream"])
@pytest.mark.parametrize("replacement", [object(), Generator(0)])
def test_generator_class_factories_reject_constructor_that_discards_cls(factory, replacement):
    class BrokenNewGenerator(Generator):
        def __new__(cls, seed=0):
            return replacement

    method = getattr(BrokenNewGenerator, factory)
    args = () if factory == "from_entropy" else (42, "worker-3")

    with pytest.raises(
        TypeError,
        match="Generator subclass constructor must return an instance of cls",
    ):
        method(*args)


@pytest.mark.skipif(
    "fork" not in multiprocessing.get_all_start_methods(), reason="fork unavailable"
)
def test_subclass_factories_preserve_fork_process_semantics():
    class GeneratorSubclass(Generator):
        pass

    deterministic = GeneratorSubclass.for_stream(42, "fork-probe")
    deterministic_control = GeneratorSubclass.for_stream(42, "fork-probe")
    assert deterministic.random_below(2**64) == deterministic_control.random_below(2**64)
    inherited_deterministic = deterministic_control.random_below(2**64)
    entropy = GeneratorSubclass.from_entropy()

    read_fd, write_fd = os.pipe()
    process_id = os.fork()
    if process_id == 0:  # pragma: no cover - assertions occur in parent
        os.close(read_fd)
        values = (
            deterministic.random_below(2**64),
            entropy.random_below(2**64),
        )
        os.write(write_fd, f"{values[0]},{values[1]}".encode("ascii"))
        os.close(write_fd)
        os._exit(0)
    os.close(write_fd)
    child_deterministic, child_entropy = map(int, os.read(read_fd, 256).decode("ascii").split(","))
    os.close(read_fd)
    os.waitpid(process_id, 0)

    assert child_deterministic == inherited_deterministic
    assert deterministic.random_below(2**64) == inherited_deterministic
    assert child_entropy != entropy.random_below(2**64)
