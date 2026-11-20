# Changelog

## v1.2.0 (2026-11-20)

### Added

- The reusable workflow has an `allow-empty` input (boolean, default `false`). When it is `true`, the workflow passes `--allow-empty`, so a pull request that changes no file Customs inspects reports NOTHING INSPECTED and exits with `0`, never CLEARED. CUS-G1 is still reported for changes to Customs controls. Meant only for repositories whose code holds no prompts; the README explains the opt-in and asks adopters to name the check for what it covers, for example "Customs (manifests and docs)". This repository's own Customs workflow does not opt in.
- Criterion CO-3.8 in `AUDIT-CRITERIA.md`, with two tests, for the opt-in.

### Changed

- `actions/checkout` is now v7.0.1 and `actions/setup-python` v7.1.0 in every workflow, both on Node 24, still pinned to a full commit SHA.

### Fixed

- The reusable workflow's header no longer says to replace `SAAF-Project/customs` with the published location, and neither does the README: that is where Customs is published.

## v1.1.0 (2026-11-18)

`VERSION` in `customs/customs.py` was `0.1.0` while the release tags were already at `v1.0.1`, so `customs --version` and the report gave a version that did not match any release. It is now `1.1.0`, the same as this release's tag.

### Added

- `agent.yaml`, the Living Map manifest (standard 2) (#3).
- `AUDIT-CRITERIA.md` with four control objectives, `llm_checks.yaml` and six tests for criteria that had none (standard 3) (#4).
- `requirements.txt`: standard library only, plus `tomli` on Python older than 3.11 (standard 7) (#7, which replaced #5, closed without merging).
- A Test column in `AUDIT-CRITERIA.md`: every `[code]` criterion names its command and every `[llm]` criterion points to `llm_checks.yaml` (#11).
- Rule CUS-G2, "Prompt sections changed": with `--changed-since`, names the paragraphs and numbered steps of instruction files that were added, removed or reworded. Informational, never blocking (#12).
- `scripts/check_criteria.py` and the Criteria workflow, which run every criterion on each pull request and push to `main` (#13).

### Fixed

- Customs no longer reports CLEARED when it inspected nothing. It reports NOT ASSESSED and exits with `2` (CO-3.5) (#8).
- Changes to `agent.yaml` are now reported as CUS-G1, as the mandate promises (CO-2.4) (#9).
- Test runs no longer add their own tables to the GitHub Actions job summary, and the duplicate CUS-G1 row is gone from the README. Adds criterion CO-1.8 for CUS-G2 (#14).

### Changed

- Every GitHub action in the workflows is pinned to a full commit SHA (#6).
- The README lists the current files and control list (#10).
