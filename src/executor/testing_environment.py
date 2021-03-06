#!/usr/bin/env python3
from typing import Union, Tuple
from tempfile import TemporaryDirectory
from client import Client
import re

### General config constants

# If true, when the expected response has a null value in any key, the key can be absent and the response will still pass.
NULL_VALUE_EQ_ABSENT_KEY = True

class TestingEnvironment:
    data_dir            = None
    current_method_id   = 0
    responses           = []

    def __init__(self, config) -> None:
        # Prepare data_dir
        self.data_dir = TemporaryDirectory()
        config['data_dir_path'] = self.data_dir.name
        # Init client
        self.client = Client(config)
        
    def run(self) -> None:
        self.client.start()
    
    def send(self, header=None, payload={}) -> None:
        return self.client.send(header, payload)

    def parse_payload_id(self, command):
        index = -1
        if len(command.split()) > 1:
            index = int(command.split()[1])
        return self.responses[index]["payloadId"]

    def pre_process_payload(self, payload):
        if type(payload) is dict:
            for k in payload.keys():
                payload[k] = self.pre_process_payload(payload[k])
        elif type(payload) is list:
            for i, el in enumerate(payload):
                payload[i] = self.pre_process_payload(el)
        elif type(payload) is str:
            if payload.startswith(':payloadId'):
                return self.parse_payload_id(payload)

        return payload
    
    def post_process_response(self, response, expected):
        return response
    
    def check_regex(self, resp, expect):
        pattern = expect[4:]
        if not re.match(pattern, resp):
            return f"{pattern} doesn't match {resp}"
        return None
    
    def check_message(self, resp, expect):
        message_keyword = expect.split()[1]
        message_pattern = self.client.get_message(message_keyword)
        if message_pattern is None:
            return f"Message {message_keyword} is not defined for client '{self.client.client_name}'"
        if message_pattern != resp:
            return f'"{message_pattern}" doesn\'t match "{resp}"'
        return None
    
    def check_expect_diff(self, k_route, resp, expect) -> Union[None, str]:

        if type(resp) != type(expect):
            return f"{'/'.join(k_route)} has unexpected type, {type(resp)}"

        if type(resp) is dict:
            diff_keys = resp.keys() ^ expect.keys()
            if diff_keys:
                if not NULL_VALUE_EQ_ABSENT_KEY:
                    return f'Conflicting keys: {resp.keys() ^ expect.keys()}, {resp}'
                for dk in diff_keys:
                    if dk in expect and expect[dk] is None:
                        continue
                    return f'Conflicting keys: {resp.keys() ^ expect.keys()}, {resp}'
            diffs = []
            for k in resp.keys():
                diff = self.check_expect_diff(k_route + [k], resp[k], expect[k])
                if diff:
                    diffs.append(diff)
            if diffs:
                return '\n'.join(diffs)
        elif type(expect) is str and expect.startswith(':re '):
            res = self.check_regex(resp, expect)
            if res:
                return f'{"/".join(k_route)}, {res}'
        elif type(expect) is str and expect.startswith(':message '):
            res = self.check_message(resp, expect)
            if res:
                return f'{"/".join(k_route)}, {res}'
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

        try:
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
                    return False, f'\'expect\' doesn\'t match response:\n{diff}'
            
            elif "expectError" in step:
                if not err:
                    return False, f'Client succeeded unexpectedly: {resp}/{step["expectError"]}'

                resp = self.post_process_response(resp, step["expectError"])

                diff = self.check_expect_diff(["expectError"], resp, step["expectError"])

                if diff:
                    return False, f'\'expectError\' doesn\'t match response: {diff}'
        except Exception:
            pass
        finally:
            self.responses.append(resp)

        return True, "Success"

    def cleanup(self) -> None:
        self.client.stop()
        self.data_dir.cleanup()