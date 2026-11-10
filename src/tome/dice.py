"""Deterministic dice mechanics and TriO posture resolution for TOME."""

import random
from enum import Enum

from tome.models import Posture


class PostureTier(str, Enum):
    OBVIOUS = "Obvious"
    OPTION = "Option"
    ODD = "Odd"


def roll_dice(sides: int, count: int = 1, seed: int | None = None) -> int:
    """Roll 'count' dice with 'sides' faces each."""
    rng = random.Random(seed) if seed is not None else random
    return sum(rng.randint(1, sides) for _ in range(count))


def roll_d66(seed: int | None = None) -> int:
    """Roll a standard d66 (tens digit 1-6, units digit 1-6). Returns 11-66."""
    rng = random.Random(seed) if seed is not None else random
    d1 = rng.randint(1, 6)
    d2 = rng.randint(1, 6)
    return d1 * 10 + d2


def get_posture_die_sides(posture: Posture) -> int:
    """Map posture to its step-die size."""
    if posture == Posture.STABLE:
        return 4
    elif posture == Posture.PRESSURED:
        return 6
    elif posture == Posture.CORNERED:
        return 8
    raise ValueError(f"Unknown posture: {posture}")


def resolve_posture_tier(posture: Posture, seed: int | None = None) -> tuple[int, PostureTier]:
    """Roll a faction's posture step-die and determine its TriO action tier."""
    sides = get_posture_die_sides(posture)
    roll = roll_dice(sides, count=1, seed=seed)
    if roll <= 3:
        tier = PostureTier.OBVIOUS
    elif roll <= 5:
        tier = PostureTier.OPTION
    else:
        tier = PostureTier.ODD
    return roll, tier
