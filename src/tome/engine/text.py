from collections.abc import Sequence


def normalize(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value.strip()


def is_non_whitespace(value: str) -> bool:
    return normalize(value) != ""


def matches(left: str, right: str) -> bool:
    return normalize(left) == normalize(right)


def find_match(value: str, candidates: Sequence[str]) -> str | None:
    return next((candidate for candidate in candidates if matches(value, candidate)), None)


def has_matching_pair(values: Sequence[str]) -> bool:
    return len({normalize(value) for value in values}) != len(values)
