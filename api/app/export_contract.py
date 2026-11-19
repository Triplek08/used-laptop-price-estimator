from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app.main import app
from app.predictors.mock import MockPredictor
from app.schemas import LaptopSpecs

CONTRACT_DIR = Path(__file__).resolve().parents[2] / "contract"


def main() -> None:
    mock = MockPredictor()
    (CONTRACT_DIR / "openapi.json").write_text(json.dumps(app.openapi(), indent=2) + "\n")
    (CONTRACT_DIR / "example-options.json").write_text(mock.options().model_dump_json(indent=2) + "\n")

    specs = LaptopSpecs.model_validate_json((CONTRACT_DIR / "example-request.json").read_text())
    # A fixed id and time keep the example stable until the contract or the mock changes.
    appraisal = mock.appraise(specs).model_copy(
        update={"id": "A-00042A", "created_at": datetime(2026, 11, 19, 12, 0, tzinfo=timezone.utc)}
    )
    (CONTRACT_DIR / "example-response.json").write_text(appraisal.model_dump_json(indent=2) + "\n")
    print(f"Wrote openapi.json, example-options.json and example-response.json to {CONTRACT_DIR}")


if __name__ == "__main__":
    main()
