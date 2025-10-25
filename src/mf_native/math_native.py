import random


def _random():
    return random.random()


def _randint(a: int, b: int) -> int:
    return random.randint(a, b)

def _choice(seq):
    return random.choice(seq)


def _shuffle(x: list):
    return random.shuffle(x)


def _sample(population, k: int):
    return random.sample(population, k)
