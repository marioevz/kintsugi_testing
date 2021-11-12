#!/usr/bin/env python3
import re
from os import path

# Geth Client Specific Methods
def port_num() -> int:
    return 8550

def prepare_genesis(config) -> dict:
    genesis = config["genesis"]
    new_genesis = {
        "name": "TheMerge_Devnet",
        "engine": {
            "clique": {
                "params": {
                    "period": 5,
                    "epoch": 30000
                }
            }
        },
        "params": {
            "gasLimitBoundDivisor": "0x400",
            "accountStartNonce": "0x0",
            "maximumExtraDataSize": "0x20",
            "minGasLimit": "0x1388",
            "networkID": genesis["config"]["chainId"],
            "eip150Transition": "0x0",
            "eip155Transition": "0x0",
            "eip158Transition": "0x0",
            "eip160Transition": "0x0",
            "eip161abcTransition": "0x0",
            "eip161dTransition": "0x0",
            "eip140Transition": "0x0",
            "eip211Transition": "0x0",
            "eip214Transition": "0x0",
            "eip658Transition": "0x0",
            "eip145Transition": "0x0",
            "eip1014Transition": "0x0",
            "eip1052Transition": "0x0",
            "eip1283Transition": "0x0",
            "eip1283DisableTransition": "0x0",
            "eip152Transition": "0x0",
            "eip1108Transition": "0x0",
            "eip1344Transition": "0x0",
            "eip1884Transition": "0x0",
            "eip2028Transition": "0x0",
            "eip2200Transition": "0x0",
            "eip2565Transition": "0x0",
            "eip2929Transition": "0x0",
            "eip2930Transition": "0x0",
            "eip1559Transition": "0x0",
            "eip3198Transition": "0x0",
            "eip3529Transition": "0x0",
            "eip3541Transition": "0x0"
        },
        "genesis": {
            "seal": {
                "ethereum": {
                    "nonce":    genesis["nonce"],
                    "mixHash":  genesis["mixHash"]
                }
            },
            "difficulty":       genesis["difficulty"],
            "author":           genesis["coinbase"],
            "timestamp":        genesis["timestamp"],
            "parentHash":       genesis["parentHash"],
            "extraData":        genesis["extraData"],
            "gasLimit":         genesis["gasLimit"],
            "baseFeePerGas":    genesis["baseFeePerGas"]
        },
        "accounts": genesis["alloc"] if "alloc" in genesis else None
    }
    if not "client_working_path" in config:
        raise Exception("Client requires working path")

    if not "tc_name" in config:
        raise Exception("Client requires test case name")
    config["genesis"] = new_genesis
    config["genesis_path"] = '' # path.join(config["client_working_path"], "configs", f"{config['tc_name']}.cfg")

def prepare_init_command(config) -> list[str]:
    return None

def prepare_start_command(config) -> list[str]:
    if not "client_binary" in config:
        raise Exception("Config missing client_binary")
    if not "data_dir_path" in config:
        raise Exception("Config missing data_dir_path")
    if not "tc_name" in config:
        raise Exception("Client requires test case name")
    if not "genesis_path" in config:
        raise Exception("Config missing genesis_path")

    comm = [config['client_binary'], 'run', '-c', 'Release', '--',
    #         '--config', config["tc_name"], '--datadir', config["data_dir_path"]]
            '--config', 'themerge_kintsugi_testvectors', '--Init.ChainSpecPath', config["genesis_path"], '--datadir', config["data_dir_path"]]

    return comm


def detect_start(proc) -> bool:
    
    start_detected = False
    while not start_detected:
        line = proc.stdout.readline().strip()
        print(line)
        if not line:
            break
        m = re.search(r'Nethermind initialization completed', line)
        if m:
            print(f"Client start detected.")
            start_detected = True
    
    return start_detected
