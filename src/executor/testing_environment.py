#!/usr/bin/env python3
from os import remove
from typing import Union, Tuple
import json
from tempfile import TemporaryDirectory, mkstemp
from clients import Client

class TestingEnvironment:
    data_dir = None

    def __init__(self, client: str, client_path = '') -> None:
        self.client = Client(client, client_path)
        self.prepare_datadir()
        # self.genesis = genesis
    
    def prepare_datadir(self) -> None:
        self.data_dir = TemporaryDirectory()
        self.client.set_data_dir(self.data_dir.name)

    def write_genesis(self, genesis) -> str:
        (_, genesis_path) = mkstemp(suffix='.json')
        with open(genesis_path, 'w') as f:
            json.dump(genesis, f)
        return genesis_path
    
    def init(self, genesis) -> None:
        gen_json = self.write_genesis(genesis)
        config = {
            'genesis_path': gen_json
        }
        self.client.init(config)
        remove(gen_json)
        
    def run(self) -> None:
        self.client.start()
    
    def send(self, header=None, payload={}) -> None:
        return self.client.send(header, payload)

    def pre_process_payload(self, payload):
        return payload
    
    def post_process_response(self, response, expected):
        return response
    
    def check_expect_diff(self, resp, expect) -> Union[None, str]:
        if not type(resp) is dict or not type(expect) is dict:
            raise Exception('Invalid comparison')
        if resp.keys() ^ expect.keys():
            return f'Conflicting keys: {resp.keys() ^ expect.keys()}'
        for k in resp.keys():
            if type(resp[k]) == type(expect[k]):
                if type(resp[k]) is dict:
                    diff = self.check_expect_diff(resp[k], expect[k])
                    if diff:
                        return diff
                if expect[k] != '*' and expect[k] != resp[k]:
                    return f'{k}, "{expect[k]}" != "{resp[k]}"'
            else:
                if expect[k] == '*':
                    continue
                else:
                    return f'{k} has differing types'
        return None

    def step(self, step: dict) -> Tuple[bool, str]:

        payload = {
                "jsonrpc":"2.0",
                "method": step["method"],
                "params": step["params"],
                "id": step["id"]
            }
        resp, err = self.send(payload=self.pre_process_payload(payload))

        if not "expect" in step and not "expectError" in step:
            return False, "'expect'/'expectError' not in test step"
        
        if "expect" in step and "expectError" in step:
            return False, "'expect'/'expectError' both in test step"

        if "expect" in step:
            if err:
                return False, f'Client returned error: {resp}'

            resp = self.post_process_response(resp, step["expect"])

            diff = self.check_expect_diff(resp, step["expect"])

            if diff:
                return False, f'\'expect\' doesn\'t match response: {diff}'
        
        elif "expectError" in step:
            if not err:
                return False, f'Client succeeded unexpectedly: {resp}/{step["expectError"]}'

            resp = self.post_process_response(resp, step["expectError"])

            diff = self.check_expect_diff(resp, step["expectError"])

            if diff:
                return False, f'\'expectError\' doesn\'t match response: {diff}'

        return True, "Success"

    def cleanup(self) -> None:
        self.client.stop()
        self.data_dir.cleanup()