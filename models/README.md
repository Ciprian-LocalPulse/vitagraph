# models/

This directory contains trained model artifacts and their metadata.

## Model Artifacts

Models trained by VitaGraph are serialized in two files:

1. **`bio_age_model.joblib`** — Scikit-learn model (pickled)
2. **`bio_age_model.json`** — Metadata sidecar (model type, features, training metrics)

### JSON Metadata Format

```json
{
  "model_type": "gradient_boosting",
  "features": [
    "chronological_age",
    "heart_rate_avg",
    "hrv_avg",
    "sleep_hours_avg",
    "activity_level",
    "environmental_exposure"
  ],
  "saved_at": "2026-07-18T10:30:00+00:00",
  "metrics": {
    "mae": 2.34,
    "rmse": 3.12,
    "r2": 0.87
  }
}
```

This metadata ensures reproducibility: loading the model includes knowing which features were used and what performance was observed.

## Version Control

Models are **not version-controlled** (too large, regenerated often). Instead:

- `git` tracks `.gitignore` which excludes `*.joblib` and `*.json`
- Trained models are stored in your output directory (default: `./outputs/models/`)
- To publish a model, store it in a release artifact or model hub (e.g., Hugging Face)

## Reproducibility

To reproduce a trained model:

```python
from vitagraph.pipeline import run_pipeline
from vitagraph.config import PipelineDefaults

config = PipelineDefaults(
    num_individuals=5,
    num_sleep_days=30,
    training_samples=500,
    random_seed=42,  # Ensure reproducibility
    model_type="gradient_boosting",
)

result = run_pipeline(config=config, output_dir="./outputs")
# Model saved to: ./outputs/models/bio_age_model.joblib
```

The `random_seed` parameter in `PipelineDefaults` ensures all random data generation is deterministic.

## Model Serving

To load and use a trained model:

```python
from vitagraph import BioAgeEstimator

estimator = BioAgeEstimator()
estimator.load_model("models/bio_age_model.joblib")

# Make a prediction
import pandas as pd
sample = pd.DataFrame([{
    "chronological_age": 40,
    "heart_rate_avg": 72,
    "hrv_avg": 50,
    "sleep_hours_avg": 7,
    "activity_level": 0.6,
    "environmental_exposure": 0.3,
}])

prediction = estimator.predict(sample)[0]
print(f"Predicted biological age: {prediction:.2f}")
```

Or via CLI:

```bash
vitagraph predict \
  --model-path models/bio_age_model.joblib \
  --chronological-age 40 \
  --heart-rate 72 \
  --hrv 50 \
  --sleep-hours 7 \
  --activity-level 0.6 \
  --environmental-exposure 0.3
```

## Model Transparency

Every model trained by VitaGraph is fully interpretable:

- **Linear**: Inspect coefficients directly
- **Random Forest**: Use `estimator.feature_importance()` to see which features matter most
- **Gradient Boosting**: Use SHAP values (external library) for per-prediction explanations

## Validation & Benchmarking

VitaGraph's models are currently trained on **synthetic data only**. To validate on real data:

1. Partner with a clinical site with longitudinal biometric + biological-age measurements
2. Train models on the real cohort
3. Report cross-validated performance (MAE, RMSE, R²)
4. Publish results in a peer-reviewed journal

See [docs/ROADMAP.md](../docs/ROADMAP.md) for real-data integration plans.

## Future: Model Hub

We plan to publish pre-trained models on Hugging Face Model Hub or similar, with:

- Model card (architecture, training data, performance, limitations)
- Versioning (v0.2, v0.3, v1.0, etc.)
- Easy download: `huggingface_hub.from_pretrained("vitagraph/bio-age-v0.2")`

---

**Made for Research** | *Reproducible & Transparent Modeling*
