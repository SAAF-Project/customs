# Audit criteria: Customs

This document says what Customs must be judged against as an auditee. The [README](README.md) says what Customs does and how to run it. Customs is a control in its own right, so the criteria below are about whether the guard itself can be relied on, not about the prompts and skills it inspects.

## Metadata

| Field | Value |
|---|---|
| **Agent** | Customs |
| **Repository** | https://github.com/SAAF-Project/customs |
| **Maintainer(s)** | Anja Nell (@AnjaNellRE), Tony Barratt (@TonyBarratt100) |
| **Last reviewed** | 2026-11-17 |
| **Status** | Draft |

Sources used to draft this document: the README, `customs/rules.py`, `customs/customs.py`, `agent.yaml`, the tests in `tests/test_customs.py`, and a set of manual runs on throwaway synthetic repositories on 17 November 2026 for behaviour the tests did not yet cover. All content used is synthetic.

## 1. What the agent does

Customs inspects every pull request that changes shared SAAF prompts, skills or agent settings, before the change is merged and reused by other organisations. It reads the changed files as text and reports content that could steer an agent against the person using it: hidden text, override wording, instructions to send data out, network or download commands, credential references and agent settings that remove approval prompts. Findings at or above the blocking severity (High by default) fail the check, with a plain English explanation of what was found and where. Customs is a deterministic script: it calls no model and makes no network calls.

## 2. Control objectives and framework mapping

| Control objective | Framework and area | Why relevant |
|---|---|---|
| CO-1: Hidden or harmful instructions in a contribution are detected and block the merge before the content is reused. | COBIT and ITIL, change management (requesting, testing and approving IT changes before they are implemented) | Customs is a pre-implementation check on changes to content that many organisations run in their own audit environments. The threat it addresses is prompt injection, as described in the OWASP guidance for AI systems. Customs itself is not an AI system, so OWASP is cited as the source of the threat, not as a framework Customs is assessed against. |
| CO-2: The contribution under inspection cannot weaken the guard. Settings and exceptions come from the base branch, and every change to Customs itself is shown to the reviewer. | ISO 27001, segregation of duties | Whoever proposes a change must not be able to approve it, or relax the control that checks it, in the same step. |
| CO-3: No silent pass. Customs never reports a scan as cleared when it inspected nothing it was asked to inspect, and every finding can be traced to a rule, a file and a line. | IIA Global Internal Audit Standards, performing engagements (sufficient, reliable and relevant information) | A result that looks the same whether or not anything was inspected is not evidence, and a conclusion built on it cannot be relied on. |
| CO-4: Exceptions are justified, approved, time-limited and stay visible. | COSO 2013, control activities | An accepted risk needs an owner, a reason and an end date. Without them the exception list becomes a way round the control. |

AI-specific regulation (such as the EU AI Act) is deliberately not mapped: Customs makes no model calls, and citing it would be padding rather than a real control.

## 3. Acceptance criteria (testable, pass or fail)

**CO-1: Detect and block**
- [code] CO-1.1 Given the poisoned example contribution in `tests/fixtures/poisoned`, Customs exits with 1 and reports at least CUS-H1, CUS-H2, CUS-H3, CUS-O1, CUS-N1, CUS-N2, CUS-S1, CUS-P1 and CUS-P2.
- [code] CO-1.2 Given text hidden in Unicode tag characters, Customs decodes it, shows the decoded text in the finding, and inspects the decoded text again.
- [code] CO-1.3 Given wording that tells an agent to set aside its instructions, in English or in Dutch, Customs reports CUS-O1.
- [code] CO-1.4 Given a command that downloads code and runs it straight away, Customs reports CUS-N5.
- [code] CO-1.5 Given the clean example skill in `tests/fixtures/clean`, Customs exits with 0 and reports no findings.
- [code] CO-1.6 Given guardrail wording that forbids an action (for example "do not finalise the report without approval from the reviewer"), Customs does not report CUS-O1.
- [llm] CO-1.7 Given a blocked contribution, every blocking finding explains in plain English what was found, where it is and why it could harm the user, so that a reviewer who does not read code can decide what to do.
  Limitation, stated honestly: Customs matches patterns. An instruction rephrased so that no pattern matches, or written in a language other than English or Dutch, is not detected (see coverage gaps).

**CO-2: The guard cannot be weakened by what it inspects**
- [code] CO-2.1 Given a pull request that adds an exception for its own finding, Customs ignores that exception, still exits with 1 and reports CUS-G1.
- [code] CO-2.2 Given a pull request that raises `fail_on` in `customs.toml` and adds a High finding, Customs applies the base branch setting, exits with 1 and reports CUS-G1 on `customs.toml`.
- [code] CO-2.3 Given a pull request that changes a file in `.github/workflows/`, Customs reports CUS-G1 on that file, including when no other file in the pull request is inspected.
- [code] CO-2.4 Given a pull request that changes `agent.yaml`, the mandate, Customs reports CUS-G1 on that file, so the reviewer sees that the agent's own rules are being changed.
  Limitation, stated honestly: CUS-G1 is Medium, so it informs the reviewer but does not block. Blocking such changes relies on the code owner rule and branch protection described in the README, which are GitHub settings outside Customs.

**CO-3: No silent pass, and every finding is traceable**
- [code] CO-3.1 Given a full scan of an empty folder, Customs reports NOT ASSESSED and exits with 2.
- [code] CO-3.2 Given a target whose files are all excluded, Customs reports NOT ASSESSED and exits with 2.
- [code] CO-3.3 Given a scan that inspects no files, Customs exits with 0 only when `--allow-empty` is passed explicitly, and then reports NOTHING INSPECTED, never CLEARED.
- [code] CO-3.4 Given any run, the summary states how many files were inspected and the blocking severity.
- [code] CO-3.5 Given a pull request that changes only files outside the inspected types (for example a Python script), Customs reports NOT ASSESSED, names the files it did not inspect, and exits with 2.
  History, stated honestly: until 17 November 2026 such a pull request was reported as CLEARED with "inspected 0 file(s)" and a green check. A script containing override wording passed this way in a manual run that day. The behaviour was changed on the same day.
- [llm] CO-3.6 Given the output of one run, a reader can tell from the output alone how many files were inspected, what the result was (CLEARED, BLOCKED, NOT ASSESSED or NOTHING INSPECTED) and why, without rerunning Customs.
- [code] CO-3.7 Given a pull request that adds or changes no files at all (for example one that only deletes files), Customs reports NOTHING INSPECTED and exits with 0, because there is nothing to inspect.

**CO-4: Exceptions are controlled**
- [code] CO-4.1 Given a valid exception, Customs applies it and keeps the accepted finding in the report, with its justification.
- [code] CO-4.2 Given an exception without a justification, Customs ignores it, reports a warning and still blocks.
- [code] CO-4.3 Given an exception whose expiry date has passed, Customs ignores it, reports a warning and still blocks.
- [code] CO-4.4 Given an exception without an approver, Customs ignores it, reports a warning and still blocks.

## 4. Good output and never do

| # | A correct output MUST contain | # | Customs must NEVER |
|---|---|---|---|
| M-1 | ✓ [code] For every finding: the rule, the severity, the file and the line (0 when the finding is about the whole file). | N-1 | ✕ [code] Report CLEARED on any scan that inspected no files. |
| M-2 | ✓ [code] One result per run, with the exit code to match: CLEARED (0), BLOCKED (1), NOT ASSESSED (2), or NOTHING INSPECTED (0, only when allowed or when nothing was added or changed). | N-2 | ✕ [code] Read its settings or exception list from the contribution under inspection. |
| M-3 | ✓ [code] Every accepted finding, with the justification and approver of the exception that accepted it. | N-3 | ✕ [code] Import a network library or call a model. |
| M-4 | ✓ [code] A warning for every exception that was ignored, saying why. | N-4 | ✕ [code] Run any command other than `git`, or execute content it inspects. |
| | | N-5 | ✕ [llm] Present a CLEARED result as proof that the content is safe or approved. |

## 5. Coverage gaps

- **Code-only pull requests now fail the Customs check (CO-3.5).** This is the intended effect of "no silent pass", but it means a pull request that changes only scripts shows a red Customs check, in this repository too. Repositories where that is routine can pass `--allow-empty`, which reports NOTHING INSPECTED instead. The trade-off should be reviewed after a few weeks of use.
- **Repositories using the reusable workflow keep the old behaviour until a new release is tagged.** The workflow is fetched from a tagged release (`@v1`), so the change in CO-3.5 reaches them only after the maintainers tag a new release.
- **Pattern matching, not understanding.** Rephrased instructions, and languages other than English and Dutch, are not detected. Customs supports a human reviewer and does not replace one.
- **It reads text and does not run code.** A script that looks harmless but behaves badly when run will pass. Script review needs separate tooling.
- **It inspects the repository, not what an agent reads later.** Auditee documents, emails and web pages opened at run time need a separate guard.
- **Changes to the guard inform but do not block (CO-2.3, CO-2.4).** Blocking depends on branch protection and code owners being set in GitHub. Customs cannot verify that these settings are on.
- **Tested on challenge examples only.** Customs has not yet been tuned against every SAAF repository, so false positive and false negative rates on real content are unknown.
- **Repository-level gaps.** None known. Dependencies are declared in requirements.txt (standard library only; tomli on Python before 3.11), and the workflows pin every GitHub action to a full commit SHA.

## 6. Status and validation

Each criterion runs with `python3 -I scripts/run_criterion.py <test name>`: exit 0 pass, 1 fail, 2 not assessed. A ☐ criterion has no test yet and counts as not assessed, never as passed.

| Criterion | Test | Verified? | Evidence |
|---|---|---|---|
| CO-1.1 | `python3 -I scripts/run_criterion.py test_poisoned_contribution_is_blocked` | ☑ | `test_poisoned_contribution_is_blocked` |
| CO-1.2 | `python3 -I scripts/run_criterion.py test_tag_characters_are_decoded` | ☑ | `test_tag_characters_are_decoded` |
| CO-1.3 | `python3 -I scripts/run_criterion.py test_english_override test_dutch_override` | ☑ | `test_english_override`, `test_dutch_override` |
| CO-1.4 | `python3 -I scripts/run_criterion.py test_download_and_run` | ☑ | `test_download_and_run` |
| CO-1.5 | `python3 -I scripts/run_criterion.py test_clean_skill_is_cleared_with_no_findings` | ☑ | `test_clean_skill_is_cleared_with_no_findings` |
| CO-1.6 | `python3 -I scripts/run_criterion.py test_guardrail_wording_is_not_flagged` | ☑ | `test_guardrail_wording_is_not_flagged` |
| CO-1.7 |  | ☑ | Judged pass on synthetic runs, 17 November 2026, by a judge that is not independent; see `evals/llm-check-results-2026-11-17.md` |
| CO-2.1 | `python3 -I scripts/run_criterion.py test_contribution_cannot_approve_its_own_exception` | ☑ | `test_contribution_cannot_approve_its_own_exception` |
| CO-2.2 | `python3 -I scripts/run_criterion.py test_contribution_cannot_loosen_settings_for_itself` | ☑ | `test_contribution_cannot_loosen_settings_for_itself` |
| CO-2.3 | `python3 -I scripts/run_criterion.py test_workflow_change_is_reported` | ☑ | `test_workflow_change_is_reported` |
| CO-2.4 | `python3 -I scripts/run_criterion.py test_mandate_change_is_reported` | ☑ | `test_mandate_change_is_reported` (gap found by the team's proof run on 17 November 2026: agent.yaml was missing from the control files) |
| CO-3.1 | `python3 -I scripts/run_criterion.py test_empty_folder_is_not_assessed` | ☑ | `test_empty_folder_is_not_assessed` |
| CO-3.2 | `python3 -I scripts/run_criterion.py test_target_that_is_fully_excluded_is_not_assessed` | ☑ | `test_target_that_is_fully_excluded_is_not_assessed` |
| CO-3.3 | `python3 -I scripts/run_criterion.py test_allow_empty_clears_an_empty_scan test_allowed_empty_scan_says_nothing_inspected_not_cleared` | ☑ | `test_allow_empty_clears_an_empty_scan`, `test_allowed_empty_scan_says_nothing_inspected_not_cleared` |
| CO-3.4 | `python3 -I scripts/run_criterion.py test_summary_states_files_inspected_and_threshold` | ☑ | `test_summary_states_files_inspected_and_threshold` |
| CO-3.5 | `python3 -I scripts/run_criterion.py test_change_to_uninspected_files_only_is_not_assessed` | ☑ | `test_change_to_uninspected_files_only_is_not_assessed` |
| CO-3.6 |  | ☑ | Judged pass on synthetic runs, 17 November 2026, by a judge that is not independent; see `evals/llm-check-results-2026-11-17.md` |
| CO-3.7 | `python3 -I scripts/run_criterion.py test_pull_request_that_only_deletes_files_is_not_blocked` | ☑ | `test_pull_request_that_only_deletes_files_is_not_blocked` |
| CO-4.1 | `python3 -I scripts/run_criterion.py test_valid_exception_is_applied_and_kept_visible` | ☑ | `test_valid_exception_is_applied_and_kept_visible` |
| CO-4.2 | `python3 -I scripts/run_criterion.py test_exception_without_justification_is_ignored` | ☑ | `test_exception_without_justification_is_ignored` |
| CO-4.3 | `python3 -I scripts/run_criterion.py test_expired_exception_is_ignored` | ☑ | `test_expired_exception_is_ignored` |
| CO-4.4 | `python3 -I scripts/run_criterion.py test_exception_without_approver_is_ignored` | ☑ | `test_exception_without_approver_is_ignored` |
| M-1 | `python3 -I scripts/run_criterion.py test_every_finding_names_rule_severity_file_and_line` | ☑ | `test_every_finding_names_rule_severity_file_and_line` |
| M-2 | `python3 -I scripts/run_criterion.py test_result_word_matches_exit_code test_allowed_empty_scan_says_nothing_inspected_not_cleared` | ☑ | `test_result_word_matches_exit_code`, `test_allowed_empty_scan_says_nothing_inspected_not_cleared` |
| M-3 | `python3 -I scripts/run_criterion.py test_valid_exception_is_applied_and_kept_visible test_accepted_finding_records_approver` | ☑ | `test_valid_exception_is_applied_and_kept_visible`, `test_accepted_finding_records_approver` |
| M-4 | `python3 -I scripts/run_criterion.py test_exception_without_justification_is_ignored test_expired_exception_is_ignored test_exception_without_approver_is_ignored` | ☑ | `test_exception_without_justification_is_ignored`, `test_expired_exception_is_ignored`, `test_exception_without_approver_is_ignored` |
| N-1 | `python3 -I scripts/run_criterion.py test_empty_folder_is_not_assessed test_target_that_is_fully_excluded_is_not_assessed test_change_to_uninspected_files_only_is_not_assessed test_allowed_empty_scan_says_nothing_inspected_not_cleared` | ☑ | `test_empty_folder_is_not_assessed`, `test_target_that_is_fully_excluded_is_not_assessed`, `test_change_to_uninspected_files_only_is_not_assessed`, `test_allowed_empty_scan_says_nothing_inspected_not_cleared` |
| N-2 | `python3 -I scripts/run_criterion.py test_contribution_cannot_approve_its_own_exception test_contribution_cannot_loosen_settings_for_itself` | ☑ | `test_contribution_cannot_approve_its_own_exception`, `test_contribution_cannot_loosen_settings_for_itself` |
| N-3 | `python3 -I scripts/run_criterion.py test_scanner_imports_no_network_library` | ☑ | `test_scanner_imports_no_network_library` |
| N-4 | `python3 -I scripts/run_criterion.py test_scanner_runs_only_git` | ☑ | `test_scanner_runs_only_git` |
| N-5 |  | ☑ | Judged pass on synthetic runs, 17 November 2026, by a judge that is not independent; see `evals/llm-check-results-2026-11-17.md` |

## 7. Observability

Each run prints a summary and every finding to the console, can write a JSON and a Markdown report (`--json`, `--markdown`), and in GitHub Actions adds a summary table to the run page and marks each finding on the changed line of the pull request. There is no record of runs beyond the GitHub Actions logs, and no view across repositories of what Customs blocked or accepted. Customs makes no model calls, so model tracing does not apply; the three `[llm]` criteria can still be scored by running the checks in `llm_checks.yaml` against saved reports.
