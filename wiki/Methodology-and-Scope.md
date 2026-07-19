# Methodology and Scope

This page states, precisely, what VitaGraph's synthetic data and models
do and do not represent. It condenses the full
[white paper](https://github.com/Ciprian-LocalPulse/vitagraph/blob/main/docs/whitepaper/VitaGraph_White_Paper.pdf)
(§4 and §6) into a quick-reference form. If you read one wiki page
before using VitaGraph for anything beyond a demo, read this one.

> ⚠️ **VitaGraph is a research reference implementation using entirely
> synthetic, seeded random data.** Nothing in this repository should be
> used for real medical, diagnostic, clinical, or therapeutic
> decision-making. The biological-age predictions produced by this
> system have not been validated against any clinical cohort and do not
> represent real biological age or health status.

## What's synthetic, and how

| Signal | Distribution | Range |
| --- | --- | --- |
| Heart rate | `Normal(μ=70, σ=8)` bpm + circadian term | `[40, 180]` |
| HRV (RMSSD-style) | `Normal(μ=55, σ=12)` ms | `[10, 120]` |
| Sleep duration | `Normal(μ=7.5, σ=1.0)` h/night | `[3, 11]` |
| Environmental exposure | `Normal(μ=0.4, σ=0.2)` | `[0, 1]` |
| Chronological age (cohort generator) | `Uniform[20, 70)` | — |

All constants above live in one place —
[`vitagraph.config.SignalBaseline`](https://ciprian-localpulse.github.io/vitagraph/api/config/)
— so they're auditable and overridable rather than scattered through
generator code.

## The synthetic biological-age label

```
biological_age =
    chronological_age
  + 0.30  · (heart_rate_avg − 70.0)
  + 1.50  · (7.5 − sleep_hours_avg)
  + 5.00  · (0.6 − activity_level)
  + 0.10  · (55.0 − hrv_avg)
  + 4.00  · environmental_exposure
  + Normal(0, 2.0)                        # noise term
```
clipped to `chronological_age ± 12` years.

**This is a data-generation convenience, not a biological or clinical
claim.** It exists so that:

- a trivial "predict the input" baseline is non-trivially beatable,
- the model has genuine, feature-correlated signal to recover, and
- every coefficient is visible, documented, and overridable.

It is **not** an implementation of any published biological-age or
epigenetic-clock algorithm, and it should not be cited as evidence
about which lifestyle factors causally affect biological aging in
reality.

## Why held-out model accuracy looks so good

Typical results (gradient boosting, 1,500 synthetic rows, `seed=42`):
MAE ≈ 1.3–1.4 years, R² ≈ 0.97–0.98 on a held-out split. This is
**expected, not impressive** — the label is generated from a documented,
largely linear formula over the same features used to predict it. High
accuracy here is a sanity check that the model-fitting mechanics are
correct on a known ground truth. **It says nothing about performance on
a real biological-age task**, which is a materially harder, noisier
problem with genuine confounding and measurement error.

## The intervention heuristic is not causal inference

`recommend_focus_area()` computes a standardized deviation from the
population baseline for five features and returns the largest one as a
"focus area" (e.g., low HRV + low sleep → "recovery / stress balance").

This answers **"which input is furthest from a population norm"**, not
**"which intervention would causally improve this person's estimate."**
Conflating the two is a common and important pitfall in applied
health-tech systems. Real causal-inference methods are tracked as
future work in
[`docs/ROADMAP.md`](https://github.com/Ciprian-LocalPulse/vitagraph/blob/main/docs/ROADMAP.md),
not implemented today.

## If you plan to plug in real data

Architecturally, this is possible — swap the synthetic generators'
output for a DataFrame matching `FEATURE_COLUMNS` / `TARGET_COLUMN` in
`vitagraph.synthetic_data`. Before doing so with **real** health data,
the project's stated commitment (see
[`data/README.md`](https://github.com/Ciprian-LocalPulse/vitagraph/blob/main/data/README.md)
and the white paper §6) is that any such data must be:

- ✅ Fully de-identified (no PHI, no PII)
- ✅ Collected under explicit participant consent for research use
- ✅ Approved by an Institutional Review Board (IRB) or equivalent
- ✅ Compliant with HIPAA/GDPR or local equivalents
- ✅ Documented with detailed provenance and collection-protocol metadata
- ✅ Placed in a separate, clearly-marked subdirectory with its own LICENSE

None of this is enforced or verified by the codebase itself — it's a
process commitment, not a technical guarantee.

## Current limitations (candidly)

1. Synthetic-only validation — no number here reflects real-world
   biological-age accuracy.
2. No causal inference — the intervention stage is a baseline heuristic.
3. No graph neural network — the ML Estimator uses flat tabular
   features, not graph structure directly, despite the "knowledge
   graph" framing.
4. Simplified, uncalibrated signal model (circadian pattern, noise).
5. No sophisticated multi-modal fusion beyond feature concatenation.

See the white paper's §7 (Limitations and Future Work) for the full
discussion, and [`docs/ROADMAP.md`](https://github.com/Ciprian-LocalPulse/vitagraph/blob/main/docs/ROADMAP.md)
for the longer-term research plan.

## Related pages

- [Architecture](Architecture) — how these pieces fit into the pipeline
- [FAQ and Troubleshooting](FAQ-and-Troubleshooting)
- Full white paper (PDF): [`docs/whitepaper/VitaGraph_White_Paper.pdf`](https://github.com/Ciprian-LocalPulse/vitagraph/blob/main/docs/whitepaper/VitaGraph_White_Paper.pdf)
