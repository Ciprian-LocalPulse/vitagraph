# data/

This directory is reserved for sample datasets, data schemas, and anonymized real-world cohorts (future).

## Current Status

Currently, VitaGraph generates all data synthetically via `vitagraph.synthetic_data` and `vitagraph.bio_signal_processor`. No real datasets are stored in this repository.

## Future Use

As VitaGraph matures (v1.0+), this directory will contain:

1. **Sample anonymized datasets**
   - Example real-world biometric time series (if partnered with clinical sites)
   - Subset data for demos and tutorials
   - Always de-identified per HIPAA/GDPR standards

2. **Data schemas & documentation**
   - Column definitions, units, data types
   - Expected ranges and distributions
   - Metadata documentation

3. **Data processing scripts**
   - Scripts to harmonize real EHR, wearable, and genomic data
   - Unit conversions (e.g., mmol/L ↔ mg/dL)
   - Handling missing values, outliers, time zones

4. **Synthetic data generators (per domain)**
   - Currently in `vitagraph.synthetic_data` and `vitagraph.bio_signal_processor`
   - May be moved here if the repository grows

## Privacy & Ethics

Any real-world data added to VitaGraph will:

- ✅ Be fully de-identified (no PHI, no PII)
- ✅ Have explicit participant consent for research
- ✅ Be approved by an Institutional Review Board (IRB)
- ✅ Follow HIPAA and GDPR compliance
- ✅ Include detailed metadata on provenance and collection protocols
- ✅ Be placed in a separate, clearly-marked subdirectory with its own LICENSE

## Dataset Versioning (once real/large data lands here)

Once this directory holds real or otherwise sizeable datasets, they
should **not** be committed directly to Git. Two supported options:

### Option A — DVC (recommended for tabular/scientific data)

```bash
pip install dvc
dvc init
dvc add data/<dataset_name>.csv
git add data/<dataset_name>.csv.dvc data/.gitignore
git commit -m "data: track <dataset_name> with DVC"
dvc remote add -d storage <your-remote-url>   # e.g. S3, GCS, Azure, or SSH
dvc push
```

This keeps small `.dvc` pointer files in Git (diffable, reviewable) while
the actual data lives in a configured remote, with `dvc pull` fetching it
on demand. `.dvc/cache` and `.dvc/tmp` are already excluded via
[`.gitignore`](../.gitignore).

### Option B — Git LFS (simpler, GitHub-native)

```bash
git lfs install
git lfs track "data/*.csv" "data/*.parquet"
git add .gitattributes
```

Prefer DVC when datasets need remote storage decoupled from GitHub, or
when you want DVC's pipeline/versioning features (`dvc.yaml` stages) on
top of raw file tracking; prefer Git LFS for simpler cases already
comfortable living entirely on GitHub's LFS storage.

## Contributing Data


If you have anonymized research data you'd like to contribute:

1. Open a GitHub Issue describing the dataset (size, modalities, cohort demographics)
2. Verify it meets ethical/legal requirements (IRB approval, consent, de-identification)
3. Work with maintainers to integrate it (usually in a separate branch/tag)
4. Publish any results in a peer-reviewed journal

See [CONTRIBUTING.md](../CONTRIBUTING.md) for more details.

---

**Made for Research** | *Responsible Data Stewardship*
