import os

from app.predictors.base import Predictor, build_appraisal

__all__ = ["Predictor", "build_appraisal", "get_predictor"]


def get_predictor() -> Predictor:
    kind = os.getenv("PREDICTOR", "mock").strip().lower()
    if kind == "mock":
        from app.predictors.mock import MockPredictor

        return MockPredictor()
    if kind == "model":
        from app.predictors.model import ModelPredictor

        return ModelPredictor()
    raise ValueError(f"Unknown PREDICTOR={kind!r}. Use 'mock' or 'model'.")
