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
    return fluctuate(range[0], range[1] - range[0])
