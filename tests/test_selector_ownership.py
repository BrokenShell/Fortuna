import pytest

from Fortuna import Generator, RandomValue, TruffleShuffle, WeightedChoice


@pytest.mark.parametrize(
    "factory",
    [
        lambda generator: RandomValue((1, 2), generator=generator),
        lambda generator: TruffleShuffle((1, 2), generator=generator),
        lambda generator: WeightedChoice(((1, 1),), generator=generator),
    ],
)
def test_value_engine_generator_binding_is_read_only(factory):
    generator = Generator(1)
    selector = factory(generator)

    assert selector.generator is generator
    with pytest.raises(AttributeError):
        selector.generator = Generator(2)
