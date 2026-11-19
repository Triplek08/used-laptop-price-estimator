from __future__ import annotations

from collections.abc import Iterable

from app.schemas import Condition, ConditionRule, Issue

CONDITION_RULE = ConditionRule(
    points={
        "scratches": 1,
        "worn_keys": 1,
        "repaired": 1,
        "dent_or_crack": 2,
        "screen_damage": 2,
        "loose_hinge": 2,
        "something_broken": 3,
    },
    min_points={"like_new": 0, "good": 1, "fair": 3, "worn": 5},
)


def condition_points(issues: Iterable[Issue], rule: ConditionRule = CONDITION_RULE) -> int:
    return sum(rule.points[issue] for issue in issues)


def grade_from_issues(issues: Iterable[Issue], rule: ConditionRule = CONDITION_RULE) -> Condition:
    total = condition_points(issues, rule)
    grade: Condition = "like_new"
    for name, minimum in sorted(rule.min_points.items(), key=lambda item: item[1]):
        if total >= minimum:
            grade = name
    return grade
