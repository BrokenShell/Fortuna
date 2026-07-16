import multiprocessing
import os
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

import Fortuna


def _module_worker(_):
    return Fortuna.random_uint(0, 2**64 - 1, count=8)


def test_module_seed_is_thread_local():
    Fortuna.seed(77)
    control = Fortuna.Generator(77)
    main_first = Fortuna.random_uint(0, 2**64 - 1)
    barrier = threading.Barrier(3)

    def draw_in_thread():
        Fortuna.seed(8128)
        barrier.wait()
        values = Fortuna.random_uint(0, 2**64 - 1, count=32)
        barrier.wait()
        return values

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(draw_in_thread) for _ in range(2)]
        barrier.wait()
        barrier.wait()
        sequences = [future.result() for future in futures]
    main_second = Fortuna.random_uint(0, 2**64 - 1)
    assert sequences[0] == sequences[1]
    assert main_first == control.random_uint(0, 2**64 - 1)
    assert main_second == control.random_uint(0, 2**64 - 1)


def test_unseeded_threads_receive_independent_entropy_streams():
    with ThreadPoolExecutor(max_workers=4) as executor:
        sequences = list(executor.map(_module_worker, range(4)))
    assert len({tuple(sequence) for sequence in sequences}) == 4


def test_shared_generator_serializes_entire_bulk_operations():
    count = 20_000
    workers = 4
    shared = Fortuna.Generator(12345)
    control = Fortuna.Generator(12345)
    expected_chunks = [
        tuple(control.random_uint(0, 2**64 - 1, count=count)) for _ in range(workers)
    ]
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(shared.random_uint, 0, 2**64 - 1, count=count) for _ in range(workers)
        ]
        actual_chunks = [tuple(future.result()) for future in futures]
    assert sorted(actual_chunks) == sorted(expected_chunks)


def test_count_conversion_can_reenter_the_same_generator():
    generator = Fortuna.Generator(912)
    control = Fortuna.Generator(912)

    class ReentrantCount:
        def __index__(self):
            assert generator.random_uint(0, 2**64 - 1) == control.random_uint(0, 2**64 - 1)
            return 0

    assert generator.random_uint(0, 10, count=ReentrantCount()) == []
    assert generator.random_uint(0, 2**64 - 1) == control.random_uint(0, 2**64 - 1)


@pytest.mark.skipif(
    "fork" not in multiprocessing.get_all_start_methods(), reason="fork unavailable"
)
def test_explicit_generator_state_is_copied_by_fork():
    generator = Fortuna.Generator(909)
    control = Fortuna.Generator(909)
    assert generator.random_uint(0, 2**64 - 1) == control.random_uint(0, 2**64 - 1)
    expected = control.random_uint(0, 2**64 - 1)
    read_fd, write_fd = os.pipe()
    process_id = os.fork()
    if process_id == 0:  # pragma: no cover - assertion occurs in parent
        os.close(read_fd)
        value = generator.random_uint(0, 2**64 - 1)
        os.write(write_fd, str(value).encode("ascii"))
        os.close(write_fd)
        os._exit(0)
    os.close(write_fd)
    child_value = int(os.read(read_fd, 128))
    os.close(read_fd)
    os.waitpid(process_id, 0)
    assert child_value == expected
    assert generator.random_uint(0, 2**64 - 1) == expected


@pytest.mark.skipif(
    "fork" not in multiprocessing.get_all_start_methods(), reason="fork unavailable"
)
def test_module_and_entropy_generators_reseed_after_fork():
    Fortuna.seed(404)
    module_control = Fortuna.Generator(404)
    assert Fortuna.random_uint(0, 2**64 - 1) == module_control.random_uint(0, 2**64 - 1)
    inherited_module_value = module_control.random_uint(0, 2**64 - 1)

    entropy_generator = Fortuna.from_entropy()
    read_fd, write_fd = os.pipe()
    process_id = os.fork()
    if process_id == 0:  # pragma: no cover - assertions occur in parent
        os.close(read_fd)
        values = (
            Fortuna.random_uint(0, 2**64 - 1),
            entropy_generator.random_uint(0, 2**64 - 1),
        )
        os.write(write_fd, f"{values[0]},{values[1]}".encode("ascii"))
        os.close(write_fd)
        os._exit(0)
    os.close(write_fd)
    child_module, child_entropy = map(int, os.read(read_fd, 256).decode("ascii").split(","))
    os.close(read_fd)
    os.waitpid(process_id, 0)

    assert Fortuna.random_uint(0, 2**64 - 1) == inherited_module_value
    assert child_module != inherited_module_value
    assert child_entropy != entropy_generator.random_uint(0, 2**64 - 1)


@pytest.mark.skipif(
    "spawn" not in multiprocessing.get_all_start_methods(), reason="spawn unavailable"
)
def test_spawn_workers_initialize_module_streams_independently():
    context = multiprocessing.get_context("spawn")
    with context.Pool(4) as pool:
        sequences = pool.map(_module_worker, range(4), chunksize=1)
    assert len({tuple(sequence) for sequence in sequences}) == 4
