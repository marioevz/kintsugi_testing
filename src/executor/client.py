#!/usr/bin/env python3
import sys
import shutil
import subprocess
import requests
import json
from tempfile import mkstemp
from os import remove
from os.path import isfile

# Import clients
from clients import geth, nethermind

SUPPORTED_CLIENTS = {
    'geth':         geth,
    'nethermind':   nethermind,
}

def write_genesis(config) -> str:
    if not "genesis_path" in config or not config["genesis_path"]:
        (_, config["genesis_path"]) = mkstemp(suffix='.json')
    with open(config["genesis_path"], 'w') as f:
        json.dump(config["genesis"], f)

class Client:
    # Instance variables
    client_name     = ''
    client_methods  = None
    node_process    = None
    config          = None

    def __init__(self, config):
        self.config = config
        if not 'client' in config or not config['client']:
            config['client'] = 'geth'
        if not config['client'] in SUPPORTED_CLIENTS:
            raise Exception(f'Client {config["client"]} not supported')
        self.client_name = config['client']
        if not 'client_binary' in config or not config['client_binary']:
            config['client_binary'] = shutil.which(config['client'])
        self.client_methods = SUPPORTED_CLIENTS[config['client']]

        self.client_methods.prepare_genesis(config)
        write_genesis(config)

        init_command = self.client_methods.prepare_init_command(self.config)

        if init_command:

            if config['print_init_output']:
                subprocess.run(init_command, stderr=sys.stderr, stdout=sys.stdout)
            else:
                p = subprocess.Popen(init_command,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        encoding='utf8')
                p.communicate()
        
        print("Client init done.")
    
    def wait_start(self, timeout=10):
        if not self.node_process:
            raise Exception('Node process does not exist')
        self.client_methods.detect_start(self.node_process)
    
    def get_message(self, keyword):
        if not keyword in self.client_methods.MESSAGES:
            return None
        return self.client_methods.MESSAGES[keyword]
    
    def start(self):
        cwd = self.config["client_working_path"] if "client_working_path" in self.config else None
        self.node_process = subprocess.Popen(self.client_methods.prepare_start_command(self.config),
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE,
                                                encoding='utf8',
                                                cwd=cwd)
        self.wait_start()
    
    def send(self, header=None, payload={}) -> dict:
        port_num = self.client_methods.port_num()
        url = f'http://localhost:{port_num}/'
        if header is None:
            header = {"Content-Type": "application/json"}
        r = None
        try:
            r = requests.post(url, json=payload, headers=header, timeout=10)
        except requests.exceptions.ReadTimeout:
            print(f'Request ({json.dumps(payload)}) timeout')
            return {'message': 'Timeout (Payload={json.dumps(payload)})'}, False
        resp = json.loads(r.text)
        if 'result' in resp:
            return resp['result'], False
        if 'error' in resp:
            return resp['error'], True
        return resp, True

    def stop(self):
        self.node_process.terminate()
        if "genesis_path" in self.config and self.config["genesis_path"] and isfile(self.config["genesis_path"]):
            remove(self.config["genesis_path"])
