import pytest

import alligater


@pytest.fixture(autouse=True)
def alligater_uuid():
    """Seed the alligater PRNG for deterministic tests."""
    alligater.seed(0)
