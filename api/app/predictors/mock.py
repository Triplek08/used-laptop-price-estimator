from __future__ import annotations

import math
from datetime import datetime

from app.predictors.base import Predictor, RawContribution, build_appraisal
from app.rules import CONDITION_RULE, grade_from_issues
from app.schemas import Appraisal, FormOptions, LaptopSpecs, ModelInfo

BASE_PRICE = 420_000

BRANDS = {
    "Acer": 0.90, "Apple": 1.45, "Asus": 0.97, "Dell": 1.08, "HP": 1.00, "Lenovo": 1.04,
    "Microsoft": 1.15, "MSI": 1.08, "Samsung": 1.00, "Toshiba": 0.80, "Other": 0.85,
}
TYPES = {"Notebook": 0.90, "Ultrabook": 1.12, "Gaming": 1.25, "2-in-1": 1.05, "Workstation": 1.30}
CPUS = {
    "Intel Celeron / Pentium": 0.60, "Intel Core i3": 0.80, "Intel Core i5": 1.00,
    "Intel Core i7": 1.15, "Intel Core i9": 1.35, "AMD Ryzen 3": 0.80, "AMD Ryzen 5": 1.00,
    "AMD Ryzen 7": 1.15, "AMD Ryzen 9": 1.35, "Apple M1": 1.10, "Apple M2": 1.22,
    "Apple M3": 1.35, "Apple M4": 1.50,
}
GRADES = {"like_new": (1.05, "Like new"), "good": (1.00, "Good"), "fair": (0.88, "Fair"), "worn": (0.72, "Worn")}
RUNTIMES = {
    "all_day": (1.00, "Battery: all day"),
    "half_day": (0.95, "Battery: half a day"),
    "one_to_three_hours": (0.88, "Battery: 1 to 3 hours"),
    "needs_charger": (0.78, "Battery: needs charger"),
    "unknown": (0.96, "Battery not checked"),
}

INFO = ModelInfo(kind="mock", name="Mock pricer", version="0.0-mock", mae=45_000)


def _storage_label(gb: int) -> str:
    return f"{gb // 1024} TB" if gb >= 1024 and gb % 1024 == 0 else f"{gb} GB"


class MockPredictor(Predictor):
    def options(self) -> FormOptions:
        return FormOptions(
            brands=list(BRANDS),
            laptop_types=list(TYPES),
            cpus=list(CPUS),
            ram_gb=[4, 8, 16, 32, 64],
            storage_gb=[128, 256, 512, 1024, 2048],
            screen_inches=[11.6, 13.3, 14.0, 15.6, 16.0, 17.3],
            year_min=2012,
            year_max=datetime.now().year,
            condition_rule=CONDITION_RULE,
            model=INFO,
        )

    def appraise(self, specs: LaptopSpecs) -> Appraisal:
        age = max(0, datetime.now().year - specs.year)
        grade_multiplier, grade_name = GRADES[grade_from_issues(specs.issues)]

        steps: list[tuple[str, str, float]] = [
            ("brand", f"{specs.brand} brand", BRANDS.get(specs.brand, 0.85)),
            ("laptop_type", f"{specs.laptop_type} build", TYPES.get(specs.laptop_type, 1.0)),
            ("cpu", specs.cpu, CPUS.get(specs.cpu, 1.0)),
            ("ram_gb", f"{specs.ram_gb} GB RAM", 1 + 0.13 * math.log2(specs.ram_gb / 8)),
            ("storage_gb", f"{_storage_label(specs.storage_gb)} storage", 1 + 0.07 * math.log2(specs.storage_gb / 256)),
            ("storage_type", "Hard drive, not SSD", 0.88 if specs.storage_type == "hdd" else 1.0),
        ]
        if specs.gpu == "dedicated":
            steps.append(("gpu", "Dedicated graphics", 1.15))
        if specs.screen_inches is not None:
            steps.append(("screen_inches", f'{specs.screen_inches:g}" screen', 1 + 0.015 * (specs.screen_inches - 14)))
        steps.append(("year", f"Age, {age} year{'s' if age != 1 else ''}", 0.87**age))
        steps.append(("issues", f"{grade_name} condition", grade_multiplier))
        if specs.battery_health_pct is not None:
            steps.append((
                "battery_health_pct",
                f"Battery health {specs.battery_health_pct}%",
                1 - max(0, 90 - specs.battery_health_pct) * 0.006,
            ))
        else:
            multiplier, label = RUNTIMES[specs.battery_runtime]
            steps.append(("battery_runtime", label, multiplier))

        price = float(BASE_PRICE)
        contributions: list[RawContribution] = []
        for feature, label, multiplier in steps:
            new_price = price * multiplier
            contributions.append((feature, label, new_price - price))
            price = new_price

        return build_appraisal(
            specs=specs,
            base_value=BASE_PRICE,
            contributions=contributions,
            low=price * 0.88,
            high=price * 1.12,
            model=INFO,
        )
