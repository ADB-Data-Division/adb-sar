# ADB public repository preparation

Target: https://github.com/ADB-Data-Division/adb-sar.
The clean import is under review in [draft PR #1](https://github.com/ADB-Data-Division/adb-sar/pull/1).
The repository remains private and the pull request is not merged.
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
The initial import passed hosted checks on both Windows and Ubuntu, including the full fetched-history secret scan.
Check the current PR head for the results of subsequent changes.

A Gitleaks 8.30.1 scan of the baseline tracked snapshot found no credentials.
A separate scan of all branches and tags in a fresh mirror scanned 23 commits and reported three historical detections in `owm.ipynb`.
Local inspection confirmed that the detections involve one distinct OpenWeather key; the value is omitted here and must not be copied into reports or issues.
The historical key was not tested against the service, so its current validity is unknown.
The full-history CI secret scan will fail on that existing history until it is cleaned or the approved files are imported without the contaminated history.
Keep that gate enabled rather than allowlisting the historical credential.

The ADB import contains a separate clean history, not those personal-repository commits.
Both its reviewed source snapshot and its fetched history passed the initial hosted secret scan.

## Requirements and verification

| Requirement | Automated evidence and controls | Remaining limit |
| --- | --- | --- |
| Reproducible methods | Python 3.11 dependency constraints; formula, CLI, SDK graph, archive, and publication tests on Windows and Ubuntu. | Full paper reproduction still needs confirmed joins, derived fields, approved inputs, and the Stata contribution. |
| Efficient processing | Streaming CSV assembly with SQLite duplicate checking; block-based nightlights and crop-mask processing. A synthetic 100,000-row, 22,788,915-byte CSV used 530,737 peak traced Python bytes in the local Windows check. | This measures Python allocations for one assembly case, not native allocations, SQLite cache, process RSS, cloud runtime, or full-dataset performance. Optional Stata conversion materializes its input in pandas. |
| Structure and documentation | The root README identifies the supported `replication/` package, research-only sources, tested setup, and the ADB clone URL. CLI help and the extraction guide document inputs, outputs, and historical conventions. | Research notebooks and draft Stata documentation do not constitute a tested complete paper pipeline. |
| Sensitive information and data | Gitleaks scans files and complete fetched history. An explicit tracked-file policy rejects data, binary archives, unknown file types, local data directories, saved notebook outputs, attachments, and widget state. | Automated scanners are not proof about data rights or the meaning of source text. The old OpenWeather key still needs owner confirmation of revocation. |
| Version control | Changes use `codex/import-extraction`, draft PR #1, descriptive commits, and CI with read-only permissions and pinned actions. | Protected-branch enforcement is unavailable while this repository is private under the current GitHub plan. |

Seven additional assembly CLI tests cover precision and leading zeros, quoted newlines, full duplicate detection, preservation of existing output on failure, input-overwrite refusal, JSON column union, malformed JSON, and bounded Python allocations.
Duplicate JSON fields and non-finite numbers are now rejected instead of silently changing assembled values.
Three additional publication-policy tests cover data and archive files, hidden notebook state, and enforcement with Python optimization enabled.
The complete suite now contains 32 tests plus the channel and resampling graph checks.
All test inputs added for these checks are synthetic and generated in temporary directories.
An additional local crop-mask check passed exact comparison of a 64-by-64 window from an existing JAXA source raster, plus synthetic adjacency, overlap, and input-overwrite checks; the source raster is excluded from the repository.

GitHub's branch-protection endpoint returned HTTP 403 with: `Upgrade to GitHub Pro or make this repository public to enable this feature.`
No plan or visibility change was made to bypass that restriction.
When ADB's repository plan or approved visibility permits it, configure `main` to require pull requests and the Windows, Ubuntu, and secret-scan checks before merging.

## Remaining publication decisions

- [ ] Confirm that the exposed OpenWeather credential has been revoked or rotated by its owner.
- [x] Import a reviewed snapshot into the existing ADB repository using a separate clean history and a pull request.
- [x] Exclude the personal repository's historical Git objects from the ADB import.
- [ ] Obtain the authors' and ADB's decision on the team's code licence; none has been specified yet.
- [ ] Confirm approved access and redistribution arrangements for custom crop-mask and preprocessed nightlight inputs.
- [ ] Resolve or explicitly accept the documented limits on pre-handoff joins, derived fields, fire inputs, and historical versus corrected outputs.
- [ ] Confirm whether ADB expects the extraction contribution alone or the combined Python and Stata paper replication package.
- [ ] Complete draft manuscript, Stata, figure, data-availability, and citation fields if the combined package is required.
- [ ] Review the exact destination branch, file inventory, and checks before merging the publication pull request.
- [ ] Enable required pull requests and status checks on `main` when GitHub's plan and approved repository visibility permit protected branches.

No raw data or restricted inputs should be uploaded to satisfy these items.
The licence and missing provenance must be supplied or confirmed by the responsible people rather than inferred from the existing code.

## Handoff procedure

Inspect the existing destination and preserve its contents and history.
Prepare the publication change on a separate branch and use a pull request with the test results and scope limitations.
A snapshot import must retain author and source attribution and the third-party licence notices, while excluding the personal repository's historical Git objects.
An ownership transfer would also transfer historical commits, issues, and pull requests and therefore requires resolving the history findings first.
Use a tagged release and record the final commit and archive checksum only after review and successful checks.

See GitHub's [repository transfer documentation](https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository) and [sensitive-data removal guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).
