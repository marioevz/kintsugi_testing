#!/usr/bin/env python3
import re

# Client specific messages:
MESSAGES = {
    'ExtraData_TooLong':            'invalid extradata length: 33',
    'UnknownHeader':                'unknown header',
    'FinalizedBlockHash_TooShort':  'invalid argument 0: hex string has length 62, want 64 for common.Hash',
    'FinalizedBlockHash_TooLong':   'invalid argument 0: hex string has length 66, want 64 for common.Hash',
    'FinalizedBlockHash_Odd':       'invalid argument 0: json: cannot unmarshal hex string of odd length into Go struct field ForkchoiceStateV1.finalizedBlockHash of type common.Hash',
    'FinalizedBlockHash_Prefix':    'invalid argument 0: json: cannot unmarshal hex string without 0x prefix into Go struct field ForkchoiceStateV1.finalizedBlockHash of type common.Hash',
    'HeadBlockHash_TooShort':       'invalid argument 0: hex string has length 62, want 64 for common.Hash',
    'HeadBlockHash_TooLong':        'invalid argument 0: hex string has length 66, want 64 for common.Hash',
    'HeadBlockHash_Odd':            'invalid argument 0: json: cannot unmarshal hex string of odd length into Go struct field ForkchoiceStateV1.headBlockHash of type common.Hash',
    'HeadBlockHash_Prefix':         'invalid argument 0: json: cannot unmarshal hex string without 0x prefix into Go struct field ForkchoiceStateV1.headBlockHash of type common.Hash',
    'SafeBlockHash_TooShort':       'invalid argument 0: hex string has length 62, want 64 for common.Hash',
    'SafeBlockHash_TooLong':        'invalid argument 0: hex string has length 66, want 64 for common.Hash',
    'SafeBlockHash_Odd':            'invalid argument 0: json: cannot unmarshal hex string of odd length into Go struct field ForkchoiceStateV1.safeBlockHash of type common.Hash',
    'SafeBlockHash_Prefix':         'invalid argument 0: json: cannot unmarshal hex string without 0x prefix into Go struct field ForkchoiceStateV1.safeBlockHash of type common.Hash',
    'Random_TooShort':              'invalid argument 1: hex string has length 62, want 64 for common.Hash',
    'Random_TooLong':               'invalid argument 1: hex string has length 66, want 64 for common.Hash',
    'Random_Odd':                   'invalid argument 1: json: cannot unmarshal hex string of odd length into Go struct field PayloadAttributesV1.random of type common.Hash',
    'Random_Prefix':                'invalid argument 1: json: cannot unmarshal hex string without 0x prefix into Go struct field PayloadAttributesV1.random of type common.Hash',
    'FeeRecipient_TooShort':        'invalid argument 1: hex string has length 38, want 40 for common.Address',
    'FeeRecipient_TooLong':         'invalid argument 1: hex string has length 42, want 40 for common.Address',
    'FeeRecipient_Odd':             'invalid argument 1: json: cannot unmarshal hex string of odd length into Go struct field PayloadAttributesV1.feeRecipient of type common.Address',
    'FeeRecipient_Prefix':          'invalid argument 1: json: cannot unmarshal hex string without 0x prefix into Go struct field PayloadAttributesV1.feeRecipient of type common.Address',
    'Timestamp_Prefix':             'invalid argument 1: json: cannot unmarshal hex string without 0x prefix into Go struct field PayloadAttributesV1.timestamp of type hexutil.Uint64',
    'Timestamp_LeadingZeros':       'invalid argument 1: json: cannot unmarshal hex number with leading zero digits into Go struct field PayloadAttributesV1.timestamp of type hexutil.Uint64',
    'Timestamp_Empty':              'invalid argument 1: json: cannot unmarshal hex string "0x" into Go struct field PayloadAttributesV1.timestamp of type hexutil.Uint64',
    'ParentHash_TooShort':          'invalid argument 1: hex string has length 62, want 64 for common.Hash',
    'ParentHash_TooLong':           'invalid argument 1: hex string has length 66, want 64 for common.Hash',
    'ParentHash_Odd':               'invalid argument 1: json: cannot unmarshal hex string of odd length into Go struct field PayloadAttributesV1.parentHash of type common.Hash',
    'ParentHash_Prefix':            'invalid argument 1: json: cannot unmarshal hex string without 0x prefix into Go struct field PayloadAttributesV1.parentHash of type common.Hash',
}

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