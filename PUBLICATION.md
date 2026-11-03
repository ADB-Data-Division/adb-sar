# ADB public repository preparation

Target: https://github.com/ADB-Data-Division/adb-sar.
This file records preparation and remaining decisions, not approval or a completed transfer.
The source baseline is `790118e81a2e96b08c2798291c11a6214fa5f424` from `sonleh96/adb-sar`.

## Scope

The supported contribution is Python extraction and preprocessing under `replication/`, with historical source notebooks and documentation.
The tracked repository does not include the delivered CSV, the large local data directories, or the final Stata analysis files described in the draft Zenodo guide.
Publish a reviewed set of tracked files rather than copying the working directory.
Notebook code-cell outputs are cleared for publication.
The extraction archive is narrower than the complete repository and carries its own explicit file allowlist.

## Verification on 3 November 2026

A fresh Python 3.11.9 environment installed the direct requirements without inheriting system packages and passed `pip check`.
Seven formula and date tests, six fire-preparation CLI tests, and five nightlights CLI tests passed.
Four archive tests cover deterministic exact-byte packaging, required dependency constraints, rejected data and notebook files, and rejected credential assignments.
Offline Earth Engine checks passed for the ESI/Aqua graph, all 256 QC bytes, and the five resampling graphs.
These are bounded method and fixture checks, not remote extraction or paper reproduction.
The dependency constraints preserve the tested package versions; CI is configured for Python 3.11 on Windows and Ubuntu.
Hosted CI results must be checked after the publication branch is pushed.

A Gitleaks 8.30.1 scan of the baseline tracked snapshot found no credentials.
A separate scan of all branches and tags in a fresh mirror scanned 23 commits and reported three historical detections in `owm.ipynb`.
Local inspection confirmed that the detections involve one distinct OpenWeather key; the value is omitted here and must not be copied into reports or issues.
The historical key was not tested against the service, so its current validity is unknown.
The full-history CI secret scan will fail on that existing history until it is cleaned or the approved files are imported without the contaminated history.
Keep that gate enabled rather than allowlisting the historical credential.

## Remaining publication decisions

- [ ] Confirm that the exposed OpenWeather credential has been revoked or rotated by its owner.
- [ ] Agree the destination import method after inspecting the ADB repository: a clean reviewed snapshot, or a history transfer after coordinated secret removal.
- [ ] Do not mirror-push the existing personal-repository history while the credential remains in historical blobs.
- [ ] Obtain the authors' and ADB's decision on the team's code licence; none has been specified yet.
- [ ] Confirm approved access and redistribution arrangements for custom crop-mask and preprocessed nightlight inputs.
- [ ] Resolve or explicitly accept the documented limits on pre-handoff joins, derived fields, fire inputs, and historical versus corrected outputs.
- [ ] Confirm whether ADB expects the extraction contribution alone or the combined Python and Stata paper replication package.
- [ ] Complete draft manuscript, Stata, figure, data-availability, and citation fields if the combined package is required.
- [ ] Review the exact destination branch, file inventory, and checks before merging the publication pull request.

No raw data or restricted inputs should be uploaded to satisfy these items.
The licence and missing provenance must be supplied or confirmed by the responsible people rather than inferred from the existing code.

## Handoff procedure

Inspect the existing destination and preserve its contents and history.
Prepare the publication change on a separate branch and use a pull request with the test results and scope limitations.
A snapshot import must retain author and source attribution and the third-party licence notices, while excluding the personal repository's historical Git objects.
An ownership transfer would also transfer historical commits, issues, and pull requests and therefore requires resolving the history findings first.
Use a tagged release and record the final commit and archive checksum only after review and successful checks.

See GitHub's [repository transfer documentation](https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository) and [sensitive-data removal guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).
