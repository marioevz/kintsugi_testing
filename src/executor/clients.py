#!/usr/bin/env python3
import shutil
import subprocess
import re
import requests
import json
from time import sleep

class Client:
    exec_path = None
    data_dir_path = None
    node_process = None

    # Client specific methods
    def prepare_init_genesis_command(self, genesis_path) -> list[str]:
        return [self.exec_path, '--catalyst', '--datadir', self.data_dir_path, 'init', genesis_path]

    def prepare_start_command(self) -> list[str]:
        return [self.exec_path, '--catalyst', '--http', '--ws', '-http.api', "engine", '--datadir', self.data_dir_path]

    def detect_start(self, proc) -> bool:
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

    # Generic client methods

    def __init__(self, client_name, exec_path=None):
        if not exec_path:
            exec_path = shutil.which(client_name)
        self.client_name = client_name
        self.exec_path = exec_path

    def set_data_dir(self, data_dir_path):
        self.data_dir_path = data_dir_path

    def init(self, genesis_path):
        if not self.data_dir_path:
            raise Exception('datadir had not been provided')
        p = subprocess.Popen(self.prepare_init_genesis_command(genesis_path),
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE,
                                                encoding='utf8')
        p.communicate()
        print("Client init done.")
    
    def wait_start(self, timeout=10):
        if not self.node_process:
            raise Exception('Node process does not exist')
        self.detect_start(self.node_process)
    
    def start(self):
        self.node_process = subprocess.Popen(self.prepare_start_command(),
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
            sleep(60)
            return 'Timeout', False
        resp = json.loads(r.text)
        if 'result' in resp:
            return resp['result'], False
        if 'error' in resp:
            return resp['error'], True
        return resp, True

    def stop(self):
        self.node_process.terminate()
