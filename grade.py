#! /usr/bin/env python3

import json
import sys
import textwrap
import traceback
from nacl.exceptions import CryptoError
from nacl.secret import SecretBox


def eprint(s, end="\n"):
    print(s, file=sys.stderr, end=end)


def check_equality(_, expected, submitted):
    if expected == submitted:
        return (True, "")
    else:
        return (False, f"expected: {repr(expected)}, submitted: {repr(submitted)}")


def main():
    if len(sys.argv) != 4:
        eprint("Usage: grade.py <inputs> <expected> <submitted>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        inputs_obj = json.load(f)

    with open(sys.argv[2]) as f:
        expected_obj = json.load(f)

    with open(sys.argv[3]) as f:
        submitted_obj = json.load(f)

    assert type(inputs_obj) == dict, "expected_obj is not a dictionary"
    assert type(expected_obj) == dict, "expected_obj is not a dictionary"
    assert type(submitted_obj) == dict, "submitted_obj is not a dictionary"

    problem_objects = []
    for problem in expected_obj:
        problem_object = {"name": problem, "max_score": 1, "score": 0}
        check_fn = check_equality
        if problem not in submitted_obj:
            correct = False
            error = f"{problem} is missing"
        else:
            try:
                correct, error = check_fn(
                    inputs_obj[problem],
                    expected_obj[problem],
                    submitted_obj[problem],
                )
            except Exception:
                correct = False
                error = traceback.format_exc().strip()
        if correct:
            problem_object["score"] = 1
            eprint(f"{problem}: ok")
        else:
            eprint(f"{problem}: incorrect")
            eprint(textwrap.indent(error, "    "))
        problem_objects.append(problem_object)

    output = {
        "stdout_visibility": "visible",
        "tests": problem_objects,
    }
    json.dump(output, sys.stdout, indent="  ")
    print()


if __name__ == "__main__":
    main()
