# adb-sar

Python extraction and preprocessing for the Vietnam crop-health study.
The [extraction guide](replication/README.md) covers NDVI, RVI, PM2.5, weather, nightlights, fire, ESI, Aqua FPAR, JAXA crop masks, and rice calendars.
The [notebook guide](NOTEBOOKS.md) documents historical experiments; the [deposit README](zenodo/README.md) covers the combined Python and Stata contribution.

Son's extraction contribution ends at the data supplied to Eugenia, including `SAR_SVN_rice_reprod.csv`.
Some pre-handoff joins and derived fields remain undocumented; her later dataset construction, analysis, and figures belong to the Stata contribution.
Bicubic and nightlights month corrections can change historical values, and reconstructed fire inputs still need reconciliation.
See the extraction guide for provenance and unresolved inputs.
Zenodo submission is pending.

Preparation for the ADB public repository is tracked in [PUBLICATION.md](PUBLICATION.md).
See [CONTRIBUTING.md](CONTRIBUTING.md) for branches, pull requests, offline checks, and data handling.

## Setup

Install Git and Python 3.11.
[requirements.txt](requirements.txt) installs the direct dependencies in [replication/requirements.txt](replication/requirements.txt), with transitive versions constrained by [constraints-py311.txt](replication/constraints-py311.txt).
The constraints were resolved and tested in a clean Windows Python 3.11.9 environment on 3 November 2026.
GitHub Actions runs the offline checks on Windows and Ubuntu with Python 3.11.
Inspect the [current checks](https://github.com/ADB-Data-Division/adb-sar/actions) for the exact revision being reviewed.

```shell
git clone https://github.com/ADB-Data-Division/adb-sar.git
cd adb-sar
```

The repository requires approved GitHub access while it is private.
During review of the initial import, run `git switch codex/import-extraction` after cloning; the default `main` branch contains only the review placeholder until the pull request is merged.

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m replication.validate_sample --self-test
.\.venv\Scripts\python.exe -m replication.extract_covariates --tile-id N10E105_0_1 --start-month 2019-01 --end-month 2019-01
```

Linux or macOS:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
.venv/bin/python -m replication.validate_sample --self-test
.venv/bin/python -m replication.extract_covariates --tile-id N10E105_0_1 --start-month 2019-01 --end-month 2019-01
```

The self-test checks local methods; the final command prints a plan without authentication or exports.
For commands below, use the environment's Python executable or activate it first.

## Data access and extraction

Supply the [required inputs](replication/README.md#required-inputs) separately.
Earth Engine exports require your account, a registered project, and access to the crop-mask and monthly nightlights assets.
Authenticate with `.\.venv\Scripts\earthengine.exe authenticate` on Windows or `.venv/bin/earthengine authenticate` on Linux/macOS.

Check the plan, then request an export:

```shell
python -m replication.extract_covariates --tile-id N10E105_0_1 --start-month 2019-01 --end-month 2019-01 --project YOUR_PROJECT --crop-mask-asset YOUR_CROP_MASK_ASSET --ntl-asset-prefix YOUR_MONTHLY_NTL_ASSET_FOLDER --submit
```

See [Execution](replication/README.md#execution) for other workflows and the [notebook guide](NOTEBOOKS.md) for experimental dependencies.
The OpenWeather notebook requires the `OPENWEATHER_API_KEY` environment variable.
Keep credentials out of code and saved outputs.

## Repository structure and validation

| Path | Role |
| --- | --- |
| `replication/` | Supported extraction and preprocessing CLIs, dependency constraints, and method/fixture validators. |
| Root notebooks, `src/`, and `preprocess_spatial_models.py` | Historical research sources with additional inputs and dependencies; not a final paper-analysis workflow. |
| `tools/check_publication.py`, `tests/` | Checks and regression tests for the tracked publication file inventory, notebook state, Python syntax, and extraction archive. |
| `zenodo/README.md` | Draft combined Python and Stata deposit description; missing analysis inputs and author decisions remain explicit. |

Run the complete command list in [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.
The assembly validator exercises 100,000 synthetic rows with disk-backed duplicate checking and checks that Python allocations stay bounded.
This is a local scaling check, not a full-dataset performance benchmark or a bound on total process memory.
See [PUBLICATION.md](PUBLICATION.md) for the requirements, evidence, and unresolved release decisions.

## Code archive

```shell
python -m replication.build_release --output release_outputs/adb-sar-extraction-preparation.zip
```

The ZIP contains the extraction README, requirements, dependency constraints, and Python files.
After unzipping, install in a Python 3.11 environment with `python -m pip install -r replication/requirements.txt` from the parent of `replication/`.

Contact: Son Le, sonle.h96@gmail.com.
