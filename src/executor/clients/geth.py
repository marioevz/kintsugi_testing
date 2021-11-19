#!/usr/bin/env python3
import re

# Client specific messages:
MESSAGES = {
    'UnknownHeader':                'unknown header',
    'UnknownPayload':               'unknown payload',

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
    'Timestamp_Long':               'invalid argument 1: json: cannot unmarshal hex number > 64 bits into Go struct field PayloadAttributesV1.timestamp of type hexutil.Uint64',

    'BlockHash_TooLong':            'invalid argument 0: hex string has length 66, want 64 for common.Hash',                                                                                                              
    'BlockHash_Odd':                'invalid argument 0: json: cannot unmarshal hex string of odd length into Go struct field ExecutableDataV1.blockHash of type common.Hash',                                                                                                                  
    'BlockHash_Prefix':             'invalid argument 0: json: cannot unmarshal hex string without 0x prefix into Go struct field ExecutableDataV1.blockHash of type common.Hash',
    'BlockHash_TooShort':           'invalid argument 0: hex string has length 62, want 64 for common.Hash',

    'Coinbase_TooLong':             'invalid argument 0: hex string has length 42, want 40 for common.Address',
    'Coinbase_Odd':                 'invalid argument 0: json: cannot unmarshal hex string of odd length into Go struct field ExecutableDataV1.coinbase of type common.Address',
    'Coinbase_Prefix':              'invalid argument 0: json: cannot unmarshal hex string without 0x prefix into Go struct field ExecutableDataV1.coinbase of type common.Address',
    'Coinbase_TooShort':            'invalid argument 0: hex string has length 38, want 40 for common.Address',

    'ExtraData_TooLong':            'invalid extradata length: 33',
    'ExtraData_Odd':                'invalid argument 0: json: cannot unmarshal hex string of odd length into Go struct field ExecutableDataV1.extraData of type hexutil.Bytes',
    'ExtraData_Prefix':             'invalid argument 0: json: cannot unmarshal hex string without 0x prefix into Go struct field ExecutableDataV1.extraData of type hexutil.Bytes',

    'LogsBloom_TooLong':            'REPLACE',
    'LogsBloom_Odd':                'invalid argument 0: json: cannot unmarshal hex string of odd length into Go struct field ExecutableDataV1.logsBloom of type hexutil.Bytes',
    'LogsBloom_Prefix':             'invalid argument 0: json: cannot unmarshal hex string without 0x prefix into Go struct field ExecutableDataV1.logsBloom of type hexutil.Bytes',
    'LogsBloom_Short':              'REPLACE',

    'ParentHash_Exec_TooLong':      'invalid argument 0: hex string has length 66, want 64 for common.Hash',
    'ParentHash_Exec_Odd':          'invalid argument 0: json: cannot unmarshal hex string of odd length into Go struct field ExecutableDataV1.parentHash of type common.Hash',
    'ParentHash_Exec_Prefix':       'invalid argument 0: json: cannot unmarshal hex string without 0x prefix into Go struct field ExecutableDataV1.parentHash of type common.Hash',
    'ParentHash_Exec_TooShort':     'invalid argument 0: hex string has length 62, want 64 for common.Hash',

    'Random_Exec_TooLong':          'invalid argument 0: hex string has length 66, want 64 for common.Hash',
    'Random_Exec_Odd':              'invalid argument 0: json: cannot unmarshal hex string of odd length into Go struct field ExecutableDataV1.random of type common.Hash',
    'Random_Exec_Prefix':           'invalid argument 0: json: cannot unmarshal hex string without 0x prefix into Go struct field ExecutableDataV1.random of type common.Hash',
    'Random_Exec_TooShort':         'invalid argument 0: hex string has length 62, want 64 for common.Hash',

    'ReceiptRoot_TooLong':          'invalid argument 0: hex string has length 66, want 64 for common.Hash',
    'ReceiptRoot_Odd':              'invalid argument 0: json: cannot unmarshal hex string of odd length into Go struct field ExecutableDataV1.receiptRoot of type common.Hash',
    'ReceiptRoot_Prefix':           'invalid argument 0: json: cannot unmarshal hex string without 0x prefix into Go struct field ExecutableDataV1.receiptRoot of type common.Hash',
    'ReceiptRoot_TooShort':         'invalid argument 0: hex string has length 62, want 64 for common.Hash',

    'StateRoot_TooLong':            'invalid argument 0: hex string has length 66, want 64 for common.Hash',
    'StateRoot_Odd':                'invalid argument 0: json: cannot unmarshal hex string of odd length into Go struct field ExecutableDataV1.stateRoot of type common.Hash',
    'StateRoot_Prefix':             'invalid argument 0: json: cannot unmarshal hex string without 0x prefix into Go struct field ExecutableDataV1.stateRoot of type common.Hash',
    'StateRoot_TooShort':           'invalid argument 0: hex string has length 62, want 64 for common.Hash',

    'BlockNumber_Empty':            'invalid argument 0: json: cannot unmarshal hex string "0x" into Go struct field ExecutableDataV1.blockNumber of type hexutil.Uint64',
    'BlockNumber_LeadingZeros':     'invalid argument 0: json: cannot unmarshal hex number with leading zero digits into Go struct field ExecutableDataV1.blockNumber of type hexutil.Uint64',
    'BlockNumber_TooLong':          'invalid argument 0: json: cannot unmarshal hex number > 64 bits into Go struct field ExecutableDataV1.blockNumber of type hexutil.Uint64',
    'BlockNumber_Prefix':           'invalid argument 0: json: cannot unmarshal hex string without 0x prefix into Go struct field ExecutableDataV1.blockNumber of type hexutil.Uint64',
    
    'GasLimit_Empty':               'invalid argument 0: json: cannot unmarshal hex string "0x" into Go struct field ExecutableDataV1.gasLimit of type hexutil.Uint64',
    'GasLimit_LeadingZeros':        'invalid argument 0: json: cannot unmarshal hex number with leading zero digits into Go struct field ExecutableDataV1.gasLimit of type hexutil.Uint64',
    'GasLimit_TooLong':             'invalid argument 0: json: cannot unmarshal hex number > 64 bits into Go struct field ExecutableDataV1.gasLimit of type hexutil.Uint64',
    'GasLimit_Prefix':              'invalid argument 0: json: cannot unmarshal hex string without 0x prefix into Go struct field ExecutableDataV1.gasLimit of type hexutil.Uint64',

    'GasUsed_Empty':                'invalid argument 0: json: cannot unmarshal hex string "0x" into Go struct field ExecutableDataV1.gasUsed of type hexutil.Uint64',
    'GasUsed_LeadingZeros':         'invalid argument 0: json: cannot unmarshal hex number with leading zero digits into Go struct field ExecutableDataV1.gasUsed of type hexutil.Uint64',
    'GasUsed_TooLong':              'invalid argument 0: json: cannot unmarshal hex number > 64 bits into Go struct field ExecutableDataV1.gasUsed of type hexutil.Uint64',
    'GasUsed_Prefix':               'invalid argument 0: json: cannot unmarshal hex string without 0x prefix into Go struct field ExecutableDataV1.gasUsed of type hexutil.Uint64',

    'Timestamp_Exec_Empty':         'invalid argument 0: json: cannot unmarshal hex string "0x" into Go struct field ExecutableDataV1.timestamp of type hexutil.Uint64',
    'Timestamp_Exec_LeadingZeros':  'invalid argument 0: json: cannot unmarshal hex number with leading zero digits into Go struct field ExecutableDataV1.timestamp of type hexutil.Uint64',
    'Timestamp_Exec_TooLong':       'invalid argument 0: json: cannot unmarshal hex number > 64 bits into Go struct field ExecutableDataV1.timestamp of type hexutil.Uint64',
    'Timestamp_Exec_Prefix':        'invalid argument 0: json: cannot unmarshal hex string without 0x prefix into Go struct field ExecutableDataV1.timestamp of type hexutil.Uint64',

    'BaseFeePerGas_Empty':          'invalid argument 0: json: cannot unmarshal hex string "0x" into Go struct field ExecutableDataV1.baseFeePerGas of type *hexutil.Big',
    'BaseFeePerGas_LeadingZeros':   'invalid argument 0: json: cannot unmarshal hex number with leading zero digits into Go struct field ExecutableDataV1.baseFeePerGas of type *hexutil.Big',
    'BaseFeePerGas_TooLong':        'invalid argument 0: json: cannot unmarshal hex number > 256 bits into Go struct field ExecutableDataV1.baseFeePerGas of type *hexutil.Big',
    'BaseFeePerGas_Prefix':         'invalid argument 0: json: cannot unmarshal hex string without 0x prefix into Go struct field ExecutableDataV1.baseFeePerGas of type *hexutil.Big',

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