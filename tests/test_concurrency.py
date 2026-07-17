import multiprocessing
import os
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

import Fortuna


def _module_worker(_):
    return Fortuna.random_below(2**64, count=8)


def test_module_seed_is_thread_local():
    Fortuna.seed(77)
    control = Fortuna.Generator(77)
    main_first = Fortuna.random_below(2**64)
    barrier = threading.Barrier(3)

    def draw_in_thread():
        Fortuna.seed(8128)
        barrier.wait()
        values = Fortuna.random_below(2**64, count=32)
        barrier.wait()
        return values

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(draw_in_thread) for _ in range(2)]
        barrier.wait()
        barrier.wait()
        sequences = [future.result() for future in futures]
    main_second = Fortuna.random_below(2**64)
    assert sequences[0] == sequences[1]
    assert main_first == control.random_below(2**64)
    assert main_second == control.random_below(2**64)


def test_unseeded_threads_receive_independent_entropy_streams():
    with ThreadPoolExecutor(max_workers=4) as executor:
        sequences = list(executor.map(_module_worker, range(4)))
    assert len({tuple(sequence) for sequence in sequences}) == 4


def test_shared_generator_serializes_entire_bulk_operations():
    count = 20_000
    workers = 4
    shared = Fortuna.Generator(12345)
    control = Fortuna.Generator(12345)
    expected_chunks = [tuple(control.random_below(2**64, count=count)) for _ in range(workers)]
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(shared.random_below, 2**64, count=count) for _ in range(workers)]
        actual_chunks = [tuple(future.result()) for future in futures]
    assert sorted(actual_chunks) == sorted(expected_chunks)


def test_shared_generator_serializes_specialized_canonical_bulk_operations():
    count = 10_000
    workers = 4
    shared = Fortuna.Generator(54321)
    control = Fortuna.Generator(54321)
    expected_chunks = [tuple(control.canonical(count=count)) for _ in range(workers)]
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(shared.canonical, count=count) for _ in range(workers)]
        actual_chunks = [tuple(future.result()) for future in futures]
    assert sorted(actual_chunks) == sorted(expected_chunks)


def test_shared_generator_serializes_specialized_scalar_operations():
    draws = 2_000
    workers = 4
    shared = Fortuna.Generator(67890)
    control = Fortuna.Generator(67890)
    expected = sorted(control.random_below(2**64, count=draws * workers))

    def draw_chunk():
        return [shared.random_below(2**64) for _ in range(draws)]

    with ThreadPoolExecutor(max_workers=workers) as executor:
        chunks = list(executor.map(lambda _: draw_chunk(), range(workers)))
    actual = sorted(value for chunk in chunks for value in chunk)
    assert actual == expected
    assert shared.random_below(2**64) == control.random_below(2**64)


def test_count_conversion_can_reenter_the_same_generator():
    generator = Fortuna.Generator(912)
    control = Fortuna.Generator(912)

    class ReentrantCount:
        def __index__(self):
            assert generator.random_below(2**64) == control.random_below(2**64)
            return 0

    assert generator.random_below(11, count=ReentrantCount()) == []
    assert generator.random_below(2**64) == control.random_below(2**64)


def test_specialized_argument_conversion_can_reenter_the_same_generator():
    generator = Fortuna.Generator(913)
    control = Fortuna.Generator(913)

    class ReentrantSize:
        def __index__(self):
            assert generator.random_below(2**64) == control.random_below(2**64)
            return 100

    class ReentrantFloat(float):
        def __float__(self):
            assert generator.random_below(2**64) == control.random_below(2**64)
            return super().__float__()

    assert generator.random_index(ReentrantSize()) == control.random_index(100)
    assert generator.random_float(ReentrantFloat(-1.0), 1.0) == control.random_float(-1.0, 1.0)


@pytest.mark.skipif(
    "fork" not in multiprocessing.get_all_start_methods(), reason="fork unavailable"
)
def test_explicit_generator_state_is_copied_by_fork():
    generator = Fortuna.Generator(909)
    control = Fortuna.Generator(909)
    assert generator.random_below(2**64) == control.random_below(2**64)
    expected = control.random_below(2**64)
    read_fd, write_fd = os.pipe()
    process_id = os.fork()
    if process_id == 0:  # pragma: no cover - assertion occurs in parent
        os.close(read_fd)
        value = generator.random_below(2**64)
        os.write(write_fd, str(value).encode("ascii"))
        os.close(write_fd)
        os._exit(0)
    os.close(write_fd)
    child_value = int(os.read(read_fd, 128))
    os.close(read_fd)
    os.waitpid(process_id, 0)
    assert child_value == expected
    assert generator.random_below(2**64) == expected


@pytest.mark.skipif(
    "fork" not in multiprocessing.get_all_start_methods(), reason="fork unavailable"
)
def test_explicit_truffle_selector_state_is_copied_by_fork():
    generator = Fortuna.Generator(910)
    control_generator = Fortuna.Generator(910)
    selector = Fortuna.TruffleShuffle(range(100), generator=generator)
    control = Fortuna.TruffleShuffle(range(100), generator=control_generator)
    expected = control()

    read_fd, write_fd = os.pipe()
    process_id = os.fork()
    if process_id == 0:  # pragma: no cover - assertion occurs in parent
        os.close(read_fd)
        value = selector()
        os.write(write_fd, str(value).encode("ascii"))
        os.close(write_fd)
        os._exit(0)
    os.close(write_fd)
    child_value = int(os.read(read_fd, 128))
    os.close(read_fd)
    os.waitpid(process_id, 0)

    assert child_value == expected
    assert selector() == expected
    assert generator.random_below(2**64) == control_generator.random_below(2**64)


@pytest.mark.skipif(
    "fork" not in multiprocessing.get_all_start_methods(), reason="fork unavailable"
)
def test_module_and_entropy_generators_reseed_after_fork():
    Fortuna.seed(404)
    module_control = Fortuna.Generator(404)
    assert Fortuna.random_below(2**64) == module_control.random_below(2**64)
    inherited_module_value = module_control.random_below(2**64)

    entropy_generator = Fortuna.from_entropy()
    read_fd, write_fd = os.pipe()
    process_id = os.fork()
    if process_id == 0:  # pragma: no cover - assertions occur in parent
        os.close(read_fd)
        values = (
            Fortuna.random_below(2**64),
            entropy_generator.random_below(2**64),
        )
        os.write(write_fd, f"{values[0]},{values[1]}".encode("ascii"))
        os.close(write_fd)
        os._exit(0)
    os.close(write_fd)
    child_module, child_entropy = map(int, os.read(read_fd, 256).decode("ascii").split(","))
    os.close(read_fd)
    os.waitpid(process_id, 0)

    assert Fortuna.random_below(2**64) == inherited_module_value
    assert child_module != inherited_module_value
    assert child_entropy != entropy_generator.random_below(2**64)


@pytest.mark.skipif(
    "fork" not in multiprocessing.get_all_start_methods(), reason="fork unavailable"
)
def test_module_truffle_selector_reseeds_engine_after_fork():
    Fortuna.seed(405)
    control_generator = Fortuna.Generator(405)
    selector = Fortuna.TruffleShuffle(range(100))
    control = Fortuna.TruffleShuffle(range(100), generator=control_generator)
    inherited_value = control()
    inherited_sentinel = control_generator.random_below(2**64)

    read_fd, write_fd = os.pipe()
    process_id = os.fork()
    if process_id == 0:  # pragma: no cover - assertions occur in parent
        os.close(read_fd)
        child_value = selector()
        child_sentinel = Fortuna.random_below(2**64)
        os.write(write_fd, f"{child_value},{child_sentinel}".encode("ascii"))
        os.close(write_fd)
        os._exit(0)
    os.close(write_fd)
    _child_value, child_sentinel = map(int, os.read(read_fd, 256).decode("ascii").split(","))
    os.close(read_fd)
    os.waitpid(process_id, 0)

    assert selector() == inherited_value
    assert Fortuna.random_below(2**64) == inherited_sentinel
    assert child_sentinel != inherited_sentinel


@pytest.mark.skipif(
    "fork" not in multiprocessing.get_all_start_methods(), reason="fork unavailable"
)
def test_specialized_canonical_reseeds_module_and_entropy_generator_after_fork():
    Fortuna.seed(505)
    control = Fortuna.Generator(505)
    assert Fortuna.canonical() == control.canonical()
    inherited_value = control.canonical()
    entropy_generator = Fortuna.from_entropy()

    read_fd, write_fd = os.pipe()
    process_id = os.fork()
    if process_id == 0:  # pragma: no cover - assertions occur in parent
        os.close(read_fd)
        values = (Fortuna.canonical(), entropy_generator.canonical())
        os.write(write_fd, f"{values[0]!r},{values[1]!r}".encode("ascii"))
        os.close(write_fd)
        os._exit(0)
    os.close(write_fd)
    child_module, child_entropy = map(float, os.read(read_fd, 256).decode("ascii").split(","))
    os.close(read_fd)
    os.waitpid(process_id, 0)

    assert Fortuna.canonical() == inherited_value
    assert child_module != inherited_value
    assert child_entropy != entropy_generator.canonical()


@pytest.mark.skipif(
    "fork" not in multiprocessing.get_all_start_methods(), reason="fork unavailable"
)
def test_specialized_scalar_reseeds_module_and_entropy_generator_after_fork():
    Fortuna.seed(606)
    control = Fortuna.Generator(606)
    assert Fortuna.random_int(-(2**63), 2**63 - 1) == control.random_int(-(2**63), 2**63 - 1)
    inherited_value = control.random_int(-(2**63), 2**63 - 1)
    entropy_generator = Fortuna.from_entropy()

    read_fd, write_fd = os.pipe()
    process_id = os.fork()
    if process_id == 0:  # pragma: no cover - assertions occur in parent
        os.close(read_fd)
        values = (
            Fortuna.random_int(-(2**63), 2**63 - 1),
            entropy_generator.random_int(-(2**63), 2**63 - 1),
        )
        os.write(write_fd, f"{values[0]},{values[1]}".encode("ascii"))
        os.close(write_fd)
        os._exit(0)
    os.close(write_fd)
    child_module, child_entropy = map(int, os.read(read_fd, 256).decode("ascii").split(","))
    os.close(read_fd)
    os.waitpid(process_id, 0)

    assert Fortuna.random_int(-(2**63), 2**63 - 1) == inherited_value
    assert child_module != inherited_value
    assert child_entropy != entropy_generator.random_int(-(2**63), 2**63 - 1)


@pytest.mark.skipif(
    "spawn" not in multiprocessing.get_all_start_methods(), reason="spawn unavailable"
)
def test_spawn_workers_initialize_module_streams_independently():
    context = multiprocessing.get_context("spawn")
    with context.Pool(4) as pool:
        sequences = pool.map(_module_worker, range(4), chunksize=1)
    assert len({tuple(sequence) for sequence in sequences}) == 4
