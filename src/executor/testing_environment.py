#!/usr/bin/env python3
from os import remove
from os.path import isdir
from typing import Union, Tuple
import json
from tempfile import TemporaryDirectory, mkstemp
from clients import Client

def write_genesis(genesis) -> str:
    (_, genesis_path) = mkstemp(suffix='.json')
    with open(genesis_path, 'w') as f:
        json.dump(genesis, f)
    return genesis_path
class TestingEnvironment:
    data_dir = None
    current_method_id = 0

    def __init__(self, config) -> None:
        # Prepare data_dir
        self.data_dir = TemporaryDirectory()
        config['data_dir_path'] = self.data_dir.name
        config['genesis_path'] = write_genesis(config['genesis'])
        # Init client
        self.client = Client(config)
        if 'genesis_path' in config and isdir(config['genesis_path']):
            remove(config['genesis_path'])
        
    def run(self) -> None:
        self.client.start()
    
    def send(self, header=None, payload={}) -> None:
        return self.client.send(header, payload)

    def pre_process_payload(self, payload):
        return payload
    
    def post_process_response(self, response, expected):
        return response
    
    def check_expect_diff(self, k_route, resp, expect) -> Union[None, str]:
        if expect == '*':
            return None

        if type(resp) != type(expect):
            return f"{'/'.join(k_route)} has unexpected type"

        if type(resp) is dict:
            if resp.keys() ^ expect.keys():
                return f'Conflicting keys: {resp.keys() ^ expect.keys()}'
            for k in resp.keys():
                diff = self.check_expect_diff(k_route + [k], resp[k], expect[k])
                if diff:
                    return diff
        elif resp != expect:
            return f'{"/".join(k_route)}, "{expect}" != "{resp}"'
        return None

    def step(self, step: dict) -> Tuple[bool, str]:
        id = self.current_method_id + 1
        if "id" in step:
            id = step["id"]
        payload = {
                "jsonrpc":"2.0",
                "method": step["method"],
                "params": step["params"],
                "id": id
            }
        self.current_method_id = id
        resp, err = self.send(payload=self.pre_process_payload(payload))

        if not "expect" in step and not "expectError" in step:
            return False, "'expect'/'expectError' not in test step"
        
        if "expect" in step and "expectError" in step:
            return False, "'expect'/'expectError' both in test step"

        if "expect" in step:
            if err:
                return False, f'Client returned error: {resp}'

            resp = self.post_process_response(resp, step["expect"])

            diff = self.check_expect_diff(["expect"], resp, step["expect"])

            if diff:
                return False, f'\'expect\' doesn\'t match response: {diff}'
        
        elif "expectError" in step:
            if not err:
                return False, f'Client succeeded unexpectedly: {resp}/{step["expectError"]}'

            resp = self.post_process_response(resp, step["expectError"])

            diff = self.check_expect_diff(["expectError"], resp, step["expectError"])

            if diff:
                return False, f'\'expectError\' doesn\'t match response: {diff}'

        return True, "Success"

    def cleanup(self) -> None:
        self.client.stop()
        self.data_dir.cleanup()