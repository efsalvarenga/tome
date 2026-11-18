import random
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Final

from pydantic import ValidationError

from tome.engine.errors import MechanicsError
from tome.engine.models import Outcome, SparkTables, TrioTier
from tome.tables import TABLE_ACTION, TABLE_DISPOSITION, TABLE_FOCUS, TABLE_METHOD, TABLE_MOTIVATION

TABLE_NAMES: Final = ("Action", "Focus", "Method", "Disposition", "Motivation")
DEFAULT_TABLE_SET_ID: Final = "trio-d66-v1"


def default_spark_tables() -> SparkTables:
    try:
        return SparkTables.model_validate(
            {
                "Action": dict(TABLE_ACTION),
                "Focus": dict(TABLE_FOCUS),
                "Method": dict(TABLE_METHOD),
                "Disposition": dict(TABLE_DISPOSITION),
                "Motivation": dict(TABLE_MOTIVATION),
            }
        )
    except ValidationError as exc:
        raise MechanicsError("The built-in spark tables are invalid.") from exc


def _checked_face(face: int) -> int:
    if type(face) is not int or not 1 <= face <= 6:
        raise MechanicsError("A d6 result is outside its defined range.")
    return face


def tier_for_roll(roll: int) -> TrioTier:
    _checked_face(roll)
    if roll <= 3:
        return "Obvious"
    if roll <= 5:
        return "Option"
    return "Odd"


@dataclass(frozen=True)
class TurnCues:
    posture_roll: int
    trio_tier: TrioTier
    table_names: tuple[str, str]
    d66_keys: tuple[int, int]
    spark_tags: tuple[str, str]


def first_round_order(
    rng: random.Random,
    actor_ids: Sequence[str],
    supplied: Sequence[str] | None,
) -> list[str]:
    if supplied is not None:
        return list(supplied)
    order = list(actor_ids)
    rng.shuffle(order)
    return order


def draw_turn_cues(rng: random.Random, tables: SparkTables) -> TurnCues:
    posture_roll = _checked_face(rng.randint(1, 6))
    names = tuple(rng.sample(list(TABLE_NAMES), 2))
    keys = tuple(
        10 * _checked_face(rng.randint(1, 6)) + _checked_face(rng.randint(1, 6)) for _ in names
    )
    try:
        tags = tuple(f"{name}:{getattr(tables, name)[key]}" for name, key in zip(names, keys))
    except (KeyError, AttributeError) as exc:
        raise MechanicsError("A sampled spark-table entry is missing.") from exc
    return TurnCues(posture_roll, tier_for_roll(posture_roll), names, keys, tags)


def roll_resolution(rng: random.Random) -> tuple[int, int]:
    return _checked_face(rng.randint(1, 6)), _checked_face(rng.randint(1, 6))


def net_vote_modifier(final_votes: Iterable[int]) -> int:
    return max(-3, min(3, sum(final_votes)))


def resolve_outcome(adjusted_total: int) -> Outcome:
    return "Success" if adjusted_total >= 7 else "Failure"
