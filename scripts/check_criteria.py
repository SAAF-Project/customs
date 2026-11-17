#!/usr/bin/env python3
"""Run every criterion in AUDIT-CRITERIA.md and exit 0 / 1 / 2.

Reads the status table (a header with "Criterion" and "Test"). A [code] row names
its command in backticks; a row whose Test is `llm_checks.yaml` is judged by
reading, not by this run. Exit 0 when every command passes, 1 when any fails,
2 when none fails but some could not be run or name no command. Not tested is
never green. Writes the table to the GitHub job summary when run in Actions.

Parsing and verdicts follow Team Mandate's standard 03 rule (Bob's
check_standards.py proposal for the agent template).
"""
import os
import re
import shlex
import subprocess
import sys

COMMAND = re.compile(r"`([^`]+)`")
CRITERION_ID = re.compile(r"(?<![\w-])([A-Z]{1,4}-\d+(?:\.\d+)?)(?![\w-])")
LLM = ("llm_checks.yaml", "evals/llm_checks.yaml")
TIMEOUT = 600


def rows(text):
    column = None
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            column = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        lowered = [c.lower() for c in cells]
        if "criterion" in lowered and "test" in lowered:
            column = lowered.index("test")
            continue
        if column is None or column >= len(cells):
            continue
        ids = CRITERION_ID.findall(cells[0])
        if ids:
            yield ids[0], cells[column]


def run(command):
    try:
        argv = shlex.split(command)
    except ValueError:
        return None
    if argv and argv[0] in ("python", "python3"):
        argv[0] = sys.executable
    try:
        return subprocess.run(argv, capture_output=True, timeout=TIMEOUT).returncode
    except (OSError, subprocess.TimeoutExpired):
        return None


def main():
    try:
        text = open("AUDIT-CRITERIA.md", encoding="utf-8").read()
    except OSError:
        print("NOT TESTED: no AUDIT-CRITERIA.md")
        return 2
    table = ["| Criterion | Result | Test |", "|---|---|---|"]
    counts = {"pass": 0, "fail": 0, "not tested": 0, "llm": 0}
    for number, cell in rows(text):
        match = COMMAND.search(cell)
        command = match.group(1).strip() if match else ""
        if command.lower() in LLM:
            counts["llm"] += 1
            table.append(f"| {number} | judged by reading | `llm_checks.yaml` |")
            continue
        code = run(command) if command else None
        result = {0: "pass", 1: "fail"}.get(code, "not tested")
        counts[result] += 1
        table.append(f"| {number} | {result.upper()} | `{command or 'no command'}` |")
    seen = counts["pass"] + counts["fail"] + counts["not tested"]
    summary = (f"{counts['pass']} pass, {counts['fail']} fail, {counts['not tested']} not tested, "
               f"{counts['llm']} judged by reading (llm_checks.yaml).")
    print("\n".join(table + ["", summary]))
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as out:
            out.write("## Audit criteria\n\n" + "\n".join(table) + "\n\n" + summary + "\n")
    if counts["fail"]:
        return 1
    return 2 if counts["not tested"] or not seen else 0


if __name__ == "__main__":
    sys.exit(main())
