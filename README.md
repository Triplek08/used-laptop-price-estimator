# Used laptop price estimator

Prices a used laptop in naira and explains the price line by line, printed as a receipt. The working name is **Tally**. This is a group project for our ML class.

To see the design, open [`design/appraisal-slip.html`](design/appraisal-slip.html) in a browser. It's a working prototype, with the slip updating live as you change answers.

## How it fits together

```
form (web)  ──POST /api/appraise──▶  FastAPI  ──▶  predictor  ──▶  Appraisal  ──▶  slip
                                              mock now, trained model later
```

The web app and the model only meet at the API contract, so both can be built at the same time. [`docs/CONTRACT.md`](docs/CONTRACT.md) explains every field, the rules responses follow, and the steps for building the model.

## What's where

| Path | What it is |
|---|---|
| `design/appraisal-slip.html` | Interactive UI prototype |
| `api/app/schemas.py` | The contract: request and response models |
| `api/app/rules.py` | Shared condition grading rule |
| `api/app/predictors/mock.py` | Hand-tuned stand-in for the model |
| `api/app/predictors/model.py` | Where the trained model goes |
| `api/tests/` | Contract tests that every predictor must pass |
| `contract/` | Generated OpenAPI spec and example request, options and response |
| `model/` | Training work. Saved model files go in `model/artifacts/`, which git ignores. |

## Who does what

- **Design, frontend and architecture:** the design lead.
- **Dataset, training and `ModelPredictor`:** Kosi.

## Run the API

```bash
cd api
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload
```

Interactive docs are then at http://localhost:8000/docs.

```bash
.venv/bin/python -m pytest
```

`PREDICTOR=model` switches from the mock to the trained model.

## Status

- **Done:** API contract, mock pricer, contract tests, UI prototype.
- **Next:** dataset and trained model (Kosi), React frontend built from the prototype, and hosting.
