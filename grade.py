#! /usr/bin/env python3

import json
from os import path
import pprint
import sys
import subprocess
import textwrap

HERE = path.dirname(path.realpath(__file__))


def main():
    if len(sys.argv) < 2 or sys.argv[1] == "--help":
        print("Usage example:")
        print("    ./grade.py python my_solution.py")
        return

    # Generate test input.
    input_json = subprocess.run(
        [sys.executable, path.join(HERE, "generate_input.py")],
        stdout=subprocess.PIPE,
        check=True,
    ).stdout
    input_obj = json.loads(input_json)

    # Run the provided Python solution with the test input from above to
    # generate expected output.
    expected_output_json = subprocess.run(
        [sys.executable, path.join(HERE, "solution_py", "solution.py")],
        input=input_json,
        stdout=subprocess.PIPE,
        check=True,
    ).stdout
    expected_output_obj = json.loads(expected_output_json)

    # Run the solution we're grading with the same input.
    your_command = sys.argv[1:]
    your_output_json = subprocess.run(
        sys.argv[1:],
        input=input_json,
        stdout=subprocess.PIPE,
        check=True,
    ).stdout
    try:
        your_output_obj = json.loads(your_output_json)
    except json.decoder.JSONDecodeError:
        print("Your solution isn't valid JSON.")
        return 1

    # Compare the answers
    any_incorrect = False
    for problem in input_obj:
        if problem not in your_output_obj:
            print(f"{problem} missing")
            any_incorrect = True
        elif your_output_obj[problem] == expected_output_obj[problem]:
            print(f"{problem} correct")
        else:

            def pretty_print(obj):
                pp = pprint.PrettyPrinter(indent=4)
                print(textwrap.indent(pp.pformat(obj), " " * 4))

            print(f"{problem} incorrect")
            print("randomized input:")
            pretty_print(input_obj[problem])
            print("expected output:")
            pretty_print(expected_output_obj[problem])
            print("your output:")
            pretty_print(your_output_obj[problem])
            any_incorrect = True
    if not any_incorrect:
        print("Well done!")
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
