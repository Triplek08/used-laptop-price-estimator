from __future__ import annotations

from pathlib import Path

from app.predictors.base import Predictor
from app.schemas import Appraisal, FormOptions, LaptopSpecs

ARTIFACTS_DIR = Path(__file__).resolve().parents[3] / "model" / "artifacts"


class ModelPredictor(Predictor):
    def __init__(self, artifacts_dir: Path = ARTIFACTS_DIR) -> None:
        raise NotImplementedError("ModelPredictor isn't built yet. See docs/CONTRACT.md.")

    def options(self) -> FormOptions:
        raise NotImplementedError

    def appraise(self, specs: LaptopSpecs) -> Appraisal:
        raise NotImplementedError
