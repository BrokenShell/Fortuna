import math
import multiprocessing

import pytest

import Fortuna


def _extreme_distribution_worker(method, args, result_queue):
    try:
        value = getattr(Fortuna.Generator(1), method)(*args)
    except Exception as error:  # noqa: BLE001 - subprocess reports the public exception
        result_queue.put(type(error).__name__)
    else:
        result_queue.put(("value", value))


@pytest.mark.parametrize(
    ("method", "args"),
    [
        ("percent_true", (-0.1,)),
        ("percent_true", (100.1,)),
        ("bernoulli_variate", (-0.1,)),
        ("bernoulli_variate", (math.nan,)),
        ("binomial_variate", (3, 1.1)),
        ("negative_binomial_variate", (0, 0.5)),
        ("geometric_variate", (0.0,)),
        ("poisson_variate", (-1.0,)),
        ("exponential_variate", (0.0,)),
        ("gamma_variate", (0.0, 1.0)),
        ("weibull_variate", (1.0, 0.0)),
        ("normal_variate", (0.0, -1.0)),
        ("log_normal_variate", (0.0, -1.0)),
        ("chi_squared_variate", (0.0,)),
        ("cauchy_variate", (0.0, 0.0)),
        ("fisher_f_variate", (1.0, 0.0)),
        ("student_t_variate", (0.0,)),
        ("beta_variate", (0.0, 1.0)),
        ("pareto_variate", (0.0,)),
        ("vonmises_variate", (0.0, -1.0)),
    ],
)
def test_distribution_domains(method, args):
    with pytest.raises(ValueError):
        getattr(Fortuna.Generator(1), method)(*args)


def test_distribution_output_contracts():
    generator = Fortuna.Generator(11)
    assert all(isinstance(value, bool) for value in generator.percent_true(25, count=100))
    assert all(0 <= value <= 10 for value in generator.binomial_variate(10, 0.3, count=100))
    assert all(value >= 0 for value in generator.poisson_variate(3.0, count=100))
    assert all(value >= 1.0 for value in generator.pareto_variate(2.0, count=100))
    assert all(0.0 <= value <= 1.0 for value in generator.beta_variate(2.0, 5.0, count=100))
    assert all(0.0 <= value < math.tau for value in generator.vonmises_variate(1.0, 2.0, count=100))


def test_random_float_and_triangular_bounds():
    generator = Fortuna.Generator(41)
    assert all(-3.0 <= value < 7.0 for value in generator.random_float(-3.0, 7.0, count=500))
    assert all(0.0 <= value <= 10.0 for value in generator.triangular(0.0, 10.0, 2.0, count=500))
    with pytest.raises(OverflowError):
        generator.random_float(-1e308, 1e308)


@pytest.mark.parametrize(
    ("method", "args", "exception_name"),
    [
        ("beta_variate", (5e-324, 5e-324), "ValueError"),
        ("gamma_variate", (1e308, 1e308), "ValueError"),
        ("gamma_variate", (1.0, 1e308), "OverflowError"),
        ("binomial_variate", (2**63, 0.5), "OverflowError"),
        ("fisher_f_variate", (5e-324, 5e-324), "ValueError"),
        ("student_t_variate", (5e-324,), "ValueError"),
        ("poisson_variate", (1e100,), "OverflowError"),
    ],
)
def test_pathological_std_distribution_inputs_fail_quickly(method, args, exception_name):
    context = multiprocessing.get_context("spawn")
    queue = context.Queue()
    process = context.Process(target=_extreme_distribution_worker, args=(method, args, queue))
    process.start()
    process.join(timeout=3.0)
    if process.is_alive():
        process.terminate()
        process.join()
        pytest.fail(f"{method}{args!r} did not terminate within three seconds")
    assert process.exitcode == 0
    assert queue.get(timeout=1.0) == exception_name


def test_float_distribution_outputs_are_finite_or_raise():
    generator = Fortuna.Generator(111)
    cases = (
        ("exponential_variate", (0.5,)),
        ("gamma_variate", (2.0, 3.0)),
        ("weibull_variate", (2.0, 3.0)),
        ("normal_variate", (0.0, 1.0)),
        ("log_normal_variate", (0.0, 1.0)),
        ("extreme_value_variate", (0.0, 1.0)),
        ("chi_squared_variate", (3.0,)),
        ("cauchy_variate", (0.0, 1.0)),
        ("fisher_f_variate", (3.0, 5.0)),
        ("student_t_variate", (3.0,)),
        ("beta_variate", (2.0, 5.0)),
        ("pareto_variate", (2.0,)),
    )
    for method, args in cases:
        values = getattr(generator, method)(*args, count=1_000)
        assert all(math.isfinite(value) for value in values)


def test_poisson_supported_ceiling_terminates_and_is_representable():
    context = multiprocessing.get_context("spawn")
    queue = context.Queue()
    process = context.Process(
        target=_extreme_distribution_worker,
        args=("poisson_variate", (float(2**63),), queue),
    )
    process.start()
    process.join(timeout=3.0)
    if process.is_alive():
        process.terminate()
        process.join()
        pytest.fail("poisson_variate at the supported 2^63 ceiling did not terminate")
    assert process.exitcode == 0
    result = queue.get(timeout=1.0)
    assert result[0] == "value"
    assert 0 <= result[1] < 2**64 - 1

    just_above_ceiling = math.nextafter(float(2**63), math.inf)
    with pytest.raises(OverflowError, match=r"2\^63"):
        Fortuna.Generator(1).poisson_variate(just_above_ceiling)
