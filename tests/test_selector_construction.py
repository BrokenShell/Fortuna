import Fortuna
from Fortuna import RandomValue, TruffleShuffle

VALUES = tuple(range(20))


def test_random_value_construction_and_cycle_consume_no_entropy():
    generator = Fortuna.Generator(8128)
    control = Fortuna.Generator(8128)

    selector = RandomValue(VALUES, generator=generator)
    selector.cycle()
    selector.cycle()

    assert generator.random_below(2**64) == control.random_below(2**64)


def test_random_value_profiles_do_not_initialize_truffle():
    selector = RandomValue(VALUES, generator=Fortuna.Generator(8128))

    selector.uniform()
    selector.front_triangular()
    selector.center_triangular()
    selector.back_triangular()

    assert selector._truffle is None


def test_random_value_lazily_constructs_one_truffle_selector():
    selector = RandomValue(VALUES, generator=Fortuna.Generator(8128))
    selector.truffle_shuffle()
    truffle = selector._truffle
    selector.truffle_shuffle()

    assert isinstance(truffle, TruffleShuffle)
    assert selector._truffle is truffle


def test_random_value_embedded_truffle_matches_standalone_schedule():
    first_generator = Fortuna.Generator(8128)
    second_generator = Fortuna.Generator(8128)
    selector = RandomValue(VALUES, generator=first_generator)
    standalone = TruffleShuffle(VALUES, generator=second_generator)

    assert [selector.truffle_shuffle() for _ in range(20)] == [standalone() for _ in range(20)]
    assert first_generator.random_below(2**64) == second_generator.random_below(2**64)
