#!/usr/bin/env python3
"""Run the test(s) behind one audit criterion and exit 0 / 1 / 2.

    python3 -I scripts/run_criterion.py test_poisoned_contribution_is_blocked
    python3 -I scripts/run_criterion.py test_english_override test_dutch_override

Run it from the repo root. Bare test names are looked up in tests/.

Exit 0  pass: every named test ran and passed.
Exit 1  fail: at least one named test ran and failed.
Exit 2  not assessed: a test could not be found or loaded, errored, was
        skipped, or nothing ran at all. Never reported as a pass.

Standard library only, so it adds no dependency.
"""
import os
import sys
import unittest

PASS, FAIL, NOT_ASSESSED = 0, 1, 2


def main(names):
    sys.path.insert(0, os.getcwd())
    if not names:
        print("NOT ASSESSED: no test named", file=sys.stderr)
        return NOT_ASSESSED
    try:
        if all("." not in n for n in names):
            found = {}
            def walk(s):
                for t in s:
                    if isinstance(t, unittest.TestSuite):
                        walk(t)
                    else:
                        found.setdefault(t.id().rsplit(".", 1)[-1], []).append(t)
            walk(unittest.defaultTestLoader.discover("tests"))
            missing = [n for n in names if n not in found]
            if missing:
                print(f"NOT ASSESSED: no test named {missing}", file=sys.stderr)
                return NOT_ASSESSED
            suite = unittest.TestSuite(t for n in names for t in found[n])
        else:
            suite = unittest.defaultTestLoader.loadTestsFromNames(names)
    except Exception as error:
        print(f"NOT ASSESSED: cannot load {names}: {error}", file=sys.stderr)
        return NOT_ASSESSED
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if result.testsRun == 0 or result.errors or result.skipped:
        print(f"NOT ASSESSED: ran {result.testsRun}, errors {len(result.errors)}, "
              f"skipped {len(result.skipped)}", file=sys.stderr)
        return NOT_ASSESSED
    if result.failures or result.unexpectedSuccesses:
        return FAIL
    return PASS


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
