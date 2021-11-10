#!/usr/bin/env python3
import sys
import shutil
import subprocess
import re
import requests
import json

SUPPORTED_CLIENTS = ['geth']

# Client Specific Methods
# TODO: Need to abstract these to execute custom code per client
def prepare_init_command(exec_path, data_dir_path, genesis_path, verbose=False) -> list[str]:
    comm = [exec_path, '--catalyst', '--datadir', data_dir_path]
    if verbose:
        comm += ['--verbosity', '5']
    comm += ['init', genesis_path]
    return comm

def prepare_start_command(exec_path, data_dir_path, verbose=False) -> list[str]:
    comm = [exec_path, '--catalyst', '--http', '--ws', '-http.api', "engine,eth", '--datadir', data_dir_path]
    if verbose:
        comm += ['--verbosity', '5']
    return comm

def detect_start(proc) -> bool:
    start_detected = False
    while not start_detected:
        line = proc.stderr.readline().strip()
        if not line:
            break
        m = re.search(r'HTTP server started', line)
        if m:
            print(f"Client start detected.")
            start_detected = True
    
    return start_detected

class Client:
    exec_path = None
    data_dir_path = None
    node_process = None
    verbose = False

    def __init__(self, config):
        client_name = 'geth'
        if 'client' in config:
            client_name = config['client']
        if not client_name in SUPPORTED_CLIENTS:
            raise Exception(f'Client {client_name} not supported')
        if 'client_path' in config and config['client_path']:
            exec_path = config['client_path']
        else:
            exec_path = shutil.which(client_name)
        self.client_name = client_name
        self.exec_path = exec_path
        self.data_dir_path = config['data_dir_path']
        self.verbose = False
        if 'verbose' in config and config['verbose']:
            self.verbose = True

        init_command = prepare_init_command(self.exec_path, self.data_dir_path, config['genesis_path'], self.verbose)

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
        detect_start(self.node_process)
    
    def start(self):
        self.node_process = subprocess.Popen(prepare_start_command(self.exec_path, self.data_dir_path, self.verbose),
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE,
                                                encoding='utf8')
        self.wait_start()
    
    def send(self, header=None, payload={}) -> dict:
        url = 'http://localhost:8545/'
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
