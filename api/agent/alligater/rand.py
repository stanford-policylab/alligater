import random
from typing import Optional, Union

_rand: Union[random.Random, random.SystemRandom] = random.SystemRandom()


def seed(num: Optional[int] = None):
    """Seed the random number generator.

    By default, and if no seed is given, we will use the system's best random
    number generator available (i.e., true random). For production this is
    good; in tests you can seed to create predictable results.
    """
    global _rand
    if num is None:
        _rand = random.SystemRandom()
    _rand = random.Random(num)


def getrandbits(n: int) -> int:
    """Proxy to random.getrandbits using our RNG.

    Args:
        n - number of bits

    Returns:
        Random information with `n` bits.
    """
    global _rand
    return _rand.getrandbits(n)
