#!/usr/bin/env python
from testing_environment import TestingEnvironment
from os import path, listdir
import sys
import argparse
import json
import importlib

# Add tests directory to the path
tests_path = path.join(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))), 'tests')
sys.path.append(tests_path)

def executeTest(tc_name, config={}):

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
        print(f"WARN: Unable to find {tc} ({err}), skipping")
        return

    if not "steps" in tc:
        print(f"WARN: Test case does not contain 'steps', skipping")
        return

    tc_config = config.copy()

    if "genesis" in tc:
        tc_config['genesis'] = tc["genesis"]
    

    tc_config['tc_name'] = path.basename(tc_name)

    test_case_env = TestingEnvironment(tc_config)

    test_case_env.run()

    test_passed = True

    for i, step in enumerate(tc["steps"]):
        result, details = test_case_env.step(step)
        if result:
            print(f"SUCC: Test case={tc_name}, step={i + 1}, id={test_case_env.current_method_id}, succeeded")
        else:
            print(f"FAIL: Test case={tc_name}, step={i + 1}, id={test_case_env.current_method_id}, failed: {details}")
            test_passed = False
            break

    test_case_env.cleanup()

    return test_passed

def executeCategory(cat_name, config={}):
    if not path.isdir(path.join(tests_path, cat_name)):
        raise Exception('Invalid category name')
    print(f"Loading category {cat_name}")
    listed_dir = [x for x in listdir(path.join(tests_path, cat_name)) if not x.startswith('_')]
    results = []
    for d in [x for x in listed_dir if path.isdir(path.join(tests_path, cat_name, x))]:
        results += executeCategory(path.join(cat_name, d), config)
    for f in [x for x in listed_dir if path.isfile(path.join(tests_path, cat_name, x))]:
        results.append(executeTest(path.splitext(path.join(cat_name, f))[0], config))
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Engine test case execute.')
    parser.add_argument('test_files', metavar='test.json', type=str, nargs='+', help='Test case files to execute')
    parser.add_argument('--client', metavar='CLIENT-NAME', type=str, default='geth', help='Client to use. Default: geth')
    parser.add_argument('--client-binary', metavar='/path/to/client/bin', type=str, help='Path of the client binary. Default: $(which <CLIENT-NAME>)')
    parser.add_argument('--client-working-path', metavar='/path/to/working/dir/', type=str, help='Used for some clients for working directory.')
    parser.add_argument('--print-init-output', action='store_true', help='Print client\'s init command stdout and stderr.')
    parser.add_argument('--verbose', action='store_true', help='Instruct client to be verbose.')

    args = parser.parse_args()

    for tc_name in args.test_files:
        if path.isdir(path.join(tests_path, tc_name)):
            results = executeCategory(tc_name, config=vars(args))
            print(f"\nTest passed {sum(results)}/{len(results)}")
        else:
            executeTest(tc_name, config=vars(args))

