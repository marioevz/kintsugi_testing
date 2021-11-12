#!/usr/bin/env python3
import re

# Geth Client Specific Methods
def port_num() -> int:
    return 8545

def prepare_genesis(config) -> dict:
    # Geth uses a 1:1 copy of the genesis block
    config["genesis_path"] = ''

def prepare_init_command(config) -> list[str]:
    if not "genesis_path" in config:
        raise Exception("Config missing genesis_path")
    if not "client_binary" in config:
        raise Exception("Config missing client_binary")
    if not "data_dir_path" in config:
        raise Exception("Config missing data_dir_path")
    
    comm = [config['client_binary'], '--catalyst', '--datadir', config['data_dir_path']]

    if 'verbose' in config and config['verbose']:
        comm += ['--verbosity', '5']
    
    comm += ['init', config["genesis_path"]]

    return comm

def prepare_start_command(config) -> list[str]:
    if not "client_binary" in config:
        raise Exception("Config missing client_binary")
    if not "data_dir_path" in config:
        raise Exception("Config missing data_dir_path")
    comm = [config['client_binary'], '--catalyst', '--http', '--ws', '-http.api', "engine,eth", '--datadir', config['data_dir_path']]
    if 'verbose' in config and config['verbose']:
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