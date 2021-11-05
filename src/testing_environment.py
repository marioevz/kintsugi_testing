#!/usr/bin/env python3
from os import remove
from typing import Union
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
        self.client.init(gen_json)
        remove(gen_json)
        
    def run(self) -> None:
        self.client.start()
    
    def send(self, header=None, payload={}) -> None:
        return self.client.send(header, payload)

    def step(self, step: dict) -> Union[bool, str]:

        payload = {
                "jsonrpc":"2.0",
                "method": step["method"],
                "params": step["params"],
                "id": step["id"]
            }
        resp = self.send(payload=payload)

        if not "expect" in step:
            return False, 'Expect not in test step'

        if not step["expect"] == resp:
            return False, f'Expect doesn\'t match response: {resp}/{step["expect"]}'

        return True, "Success"

    def cleanup(self) -> None:
        self.client.stop()
        self.data_dir.cleanup()