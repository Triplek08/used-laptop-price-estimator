from __future__ import annotations

import secrets
from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import datetime, timezone

from app.rules import CONDITION_RULE, grade_from_issues
from app.schemas import (
    Appraisal,
    ConditionRule,
    Contribution,
    ContributionSource,
    FormOptions,
    LaptopSpecs,
    ModelInfo,
    PriceRange,
)

RawContribution = tuple[str, str, float] | tuple[str, str, float, ContributionSource]


class Predictor(ABC):
    @abstractmethod
    def options(self) -> FormOptions: ...

    @abstractmethod
    def appraise(self, specs: LaptopSpecs) -> Appraisal: ...


def _round(value: float, step: int) -> int:
    return int(round(value / step) * step)


def build_appraisal(
    *,
    specs: LaptopSpecs,
    base_value: float,
    contributions: Sequence[RawContribution],
    low: float,
    high: float,
    model: ModelInfo,
    confidence: float = 0.8,
    step: int = 1000,
    rule: ConditionRule = CONDITION_RULE,
) -> Appraisal:
    """Rounds to `step` naira and moves the rounding drift onto the largest line so the slip adds up exactly."""
    base = _round(base_value, step)
    lines = [
        Contribution(
            feature=raw[0],
            label=raw[1],
            amount=_round(raw[2], step),
            source=raw[3] if len(raw) > 3 else "model",
        )
        for raw in contributions
    ]
    lines = [line for line in lines if line.amount != 0]

    estimate = _round(base_value + sum(raw[2] for raw in contributions), step)
    drift = estimate - (base + sum(line.amount for line in lines))
    if drift and lines:
        max(lines, key=lambda line: abs(line.amount)).amount += drift
    elif drift:
        base += drift

    range_step = step * 5
    price_range = PriceRange(
        low=min(_round(low, range_step), estimate),
        high=max(_round(high, range_step), estimate),
        confidence=confidence,
    )
    return Appraisal(
        id=f"A-{secrets.token_hex(3).upper()}",
        created_at=datetime.now(timezone.utc),
        condition_grade=grade_from_issues(specs.issues, rule),
        base_value=base,
        contributions=lines,
        estimate=estimate,
        range=price_range,
        model=model,
    )
