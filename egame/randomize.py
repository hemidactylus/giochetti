import random

from egame.type_definitions import FPair


def rnd() -> float:
    return random.random()


def srnd() -> float:
    return 2.0 * rnd() - 1.0


def msrnd(smaximum: float) -> float:
    return smaximum * srnd()


def fluctuate(base: float, famp: float) -> float:
    return base + srnd() * famp


def mrnd(maximum: float) -> float:
    return maximum * rnd()


def rrnd(range: FPair) -> float:
    return range[0] + rnd() * (range[1] - range[0])


def i_mrnd(maximum: int) -> int:
    return int(rnd() * maximum)
