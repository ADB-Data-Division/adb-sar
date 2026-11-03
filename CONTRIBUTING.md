# Contributing

Use a branch and a pull request for each coherent change.
Start from the current target branch, use a descriptive branch such as `fix/calendar-month-boundaries`, and write commits that explain the change.
Keep raw data, outputs, credentials, local notes, and unrelated research experiments out of commits.
Review `git diff --cached` and the exact staged file list before committing; stage individual paths instead of using `git add .`.
The `.gitignore` rules prevent common accidental additions but do not inspect tracked files or Git history.

## Environment and checks

Create a fresh Python 3.11 virtual environment using the setup instructions in [README.md](README.md).
Do not copy a virtual environment from another machine or reuse an environment that inherits unrelated system packages.
Install from `requirements.txt`, which includes the version constraints used for the extraction package.
Run these commands from the repository root with that environment's Python:

```shell
python -m pip check
python -m replication.validate_sample --self-test
python -m replication.validate_sample --channel-graph-check
python -m replication.validate_resampling
python -m replication.validate_fire_detections
python -m replication.validate_nightlights
python -m replication.validate_release
python -m replication.build_release --output release_outputs/adb-sar-extraction-preparation.zip
git diff --check
```

These checks use local fixtures and SDK metadata without authenticating or submitting cloud exports.
They do not establish access to private assets, complete upstream provenance, or reproduction of the paper's estimates.
Use the additional real-input and independent-reference checks in [replication/README.md](replication/README.md) when the approved inputs are available.
Document the command, input version, runtime, and result when changing an extraction method.

## Credentials, data, and notebooks

Supply account credentials through environment variables or the provider's normal local authentication mechanism.
Never save tokens, passwords, service-account files, raw or restricted data, or executed notebook outputs in Git.
Clear code-cell outputs, execution counts, and widget state before committing notebooks.
Inspect code and Markdown cells as well, since output clearing does not remove data or credentials embedded in source cells.
Use synthetic fixtures for tests and identify them explicitly.
Data sources retain their own access and redistribution terms.

Before publishing a snapshot, scan it with Gitleaks and inspect its full file inventory.
Before transferring Git history, fetch all relevant branches and tags and scan the history as well:

```shell
gitleaks git . --log-opts="--all" --redact=100
```

Do not suppress historical credential findings merely to make a check pass.
Revoke or rotate an exposed credential with its owner, then agree how to handle history with the repository maintainers.
History rewriting and force-pushing require explicit agreement because they affect collaborators and existing commit references.

## Pull requests and releases

Explain the concrete behavior changed, the validation performed, and remaining limitations.
Preserve upstream copyright notices and attribution when editing vendored or adapted code.
Obtain review before merging and check that GitHub Actions has completed successfully.
For the initial ADB publication, complete the unresolved items in [PUBLICATION.md](PUBLICATION.md) before treating the repository as final.
The team's code licence must be confirmed by the authors and ADB; third-party MIT notices do not assign a licence to the whole repository.
