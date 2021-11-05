#!/usr/bin/env python
from testing_environment import TestingEnvironment
import argparse
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Engine test case execute.')
    parser.add_argument('test_files', metavar='test.json', type=str, nargs='+', help='Test case files to execute')
    parser.add_argument('--client', metavar='CLIENT-NAME', type=str, default='geth', help='Client to use. Default: geth')
    parser.add_argument('--client-path', metavar='/path/to/client', type=str, help='Path of the client binary. Default: $(which <CLIENT-NAME>)')

    args = parser.parse_args()

    for test_file_path in args.test_files:
        print(f"Loading {test_file_path}")

        tc = None
        err = None
        try:
            with open(test_file_path, 'r') as f:
                tc = json.load(f)
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
                print(f"SUCC: Test case {test_file_path} step {id} succeeded")
            else:
                print(f"FAIL: Test case {test_file_path} step {id} failed: {details}")
                break

        test_case_env.cleanup()
