#!/usr/bin/env python
from testing_environment import TestingEnvironment
from os import path
import sys
import argparse
import json
import importlib

# Add tests directory to the path
tests_path = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'tests')
sys.path.append(tests_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Engine test case execute.')
    parser.add_argument('test_files', metavar='test.json', type=str, nargs='+', help='Test case files to execute')
    parser.add_argument('--client', metavar='CLIENT-NAME', type=str, default='geth', help='Client to use. Default: geth')
    parser.add_argument('--client-path', metavar='/path/to/client', type=str, help='Path of the client binary. Default: $(which <CLIENT-NAME>)')

    args = parser.parse_args()

    for tc_name in args.test_files:
        print(f"Loading {tc_name}")

        tc = None
        err = None
        if path.isfile(path.join(tests_path, tc_name + '.json')):
            try:
                with open(path.join(tests_path, tc_name + '.json'), 'r') as f:
                    tc = json.load(f)
            except Exception as ex:
                err = ex
        else:
            try:
                # Try to load as package
                imported_tc = importlib.import_module(name=tc_name)
                tc = {}
                tc['genesis'] = imported_tc.genesis
                tc['steps'] = imported_tc.steps
            except Exception as ex:
                err = ex

        if not tc or err:
            print(f"WARN: Unable to load {tc} ({err}), skipping")
            continue

        if not "steps" in tc:
            print(f"WARN: Test case does not contain 'steps', skipping")
            continue

        test_case_env = TestingEnvironment(client=args.client, client_path=args.client_path)

        if "genesis" in tc:
            test_case_env.init(tc["genesis"])

        test_case_env.run()

        for id, step in enumerate(tc["steps"]):
            result, details = test_case_env.step(step)
            if result:
                print(f"SUCC: Test case {tc_name}, step {id + 1} succeeded")
            else:
                print(f"FAIL: Test case {tc_name}, step {id + 1} failed: {details}")
                break

        test_case_env.cleanup()
