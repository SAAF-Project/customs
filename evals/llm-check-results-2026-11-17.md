# LLM check results, 17 November 2026

First judged run of the three checks in [`llm_checks.yaml`](../llm_checks.yaml), which cover the criteria tagged `[llm]` in [`AUDIT-CRITERIA.md`](../AUDIT-CRITERIA.md).

| Field | Value |
|---|---|
| Customs version | 0.1.0, branch `anja/no-silent-pass` (pull request #8) |
| Judge | Claude Opus 5.5, acting as judge, reading the console output of each run |
| Independence | **Not independent.** The same assistant drafted the criteria and the checks. Treat these verdicts as a first reading, to be repeated by an independent judge (for example with the Orq.ai skill `/orq-criteria-to-evals` at `saaf-project.orq.ai`) or by a reviewer. |
| Data | Synthetic only: the example skills in `tests/fixtures/` and a throwaway repository created for the run |

## The runs

The raw output is not stored in this repository. The blocked run quotes the synthetic attack text from `tests/fixtures/poisoned`, which Customs would report in any file outside `tests/fixtures/`. Each run can be repeated with the command below.

| Run | Command | Exit | Result |
|---|---|---|---|
| R1 Blocked | `python3 customs/customs.py --root tests/fixtures/poisoned` | 1 | BLOCKED, 10 blocking and 4 other findings |
| R2 Cleared | `python3 customs/customs.py --root tests/fixtures/clean` | 0 | CLEARED, 1 file inspected, no findings |
| R3 Not assessed | `--changed-since main` on a throwaway repository whose only change is one Python file | 2 | NOT ASSESSED, names the file not inspected |
| R4 Nothing inspected | the same as R3, with `--allow-empty` | 0 | NOTHING INSPECTED |

## Verdicts

| Check | Runs read | Verdict | Reasoning |
|---|---|---|---|
| CO-1.7 | R1 | **Pass** | All 10 blocking findings give the file, the line and a plain English reason that says why the content could harm the user (for example, that hidden characters can carry instructions a reviewer cannot see, or that an instruction sends data to an outside destination). No blocking finding gives only a rule code. Observation: the five findings under CUS-O1 share one generic reason, so a reviewer has to read the quoted excerpt to see which kind of override each one is. |
| CO-3.6 | R1 to R4 | **Pass** | Each run states the number of files inspected, one result word and the reason for it. Observation: before this run, the CLEARED line in R2 gave only the count of findings below the threshold, not the reason the run cleared. The wording was changed in the same pull request to "No finding at High or above in the 1 file(s) inspected", and R2 was repeated with the new wording. |
| N-5 | R2, R4 | **Pass** | Neither run calls the content safe, approved or free of risk. R2 ends by saying the merge decision stays with the reviewer, and R4 says the run is not evidence that any content is safe. |

## What is still open

- An independent judge has not yet read these runs.
- The checks have been read against synthetic runs only, not against runs on real SAAF pull requests.
