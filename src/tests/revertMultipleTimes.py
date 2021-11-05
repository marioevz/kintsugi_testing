#!/usr/bin/env python

# Description: Go back and forth updating the forkchoice between genesis and a new block

genesis = {
    "config": {
        "chainId": 1,
        "homesteadBlock": 0,
        "eip150Block": 0,
        "eip155Block": 0,
        "eip158Block": 0,
        "byzantiumBlock": 0,
        "constantinopleBlock": 0,
        "petersburgBlock": 0,
        "istanbulBlock": 0,
        "muirGlacierBlock": 0,
        "berlinBlock": 0,
        "londonBlock": 0,
        "clique": {
            "period": 5,
            "epoch": 30000
        },
        "terminalTotalDifficulty": 0
    },
    "nonce": "0x42",
    "timestamp": "0x0",
    "extraData": "0x0000000000000000000000000000000000000000000000000000000000000000a94f5374fce5edbc8e2a8697c15331677e6ebf0b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "gasLimit": "0x1C9C380",
    "difficulty": "0x400000000",
    "mixHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
    "coinbase": "0x0000000000000000000000000000000000000000",
    "alloc": {
        "0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b": {
                "balance": "0x6d6172697573766477000000"
        }
    },
    "number": "0x0",
    "gasUsed": "0x0",
    "parentHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
    "baseFeePerGas": "0x7"
}

genesisRevertForkChoice = {
        "method": "engine_forkchoiceUpdatedV1",
        "params": [
            {
                "headBlockHash": "0x3b8fb240d288781d4aac94d3fd16809ee413bc99294a085798a589dae51ddd4a",
                "safeBlockHash": "0x3b8fb240d288781d4aac94d3fd16809ee413bc99294a085798a589dae51ddd4a",
                "finalizedBlockHash": "0x0000000000000000000000000000000000000000000000000000000000000000"
            },
            {
                "parentHash": "0x3b8fb240d288781d4aac94d3fd16809ee413bc99294a085798a589dae51ddd4a",
                "timestamp": "0x5",
                "random": "0x0000000000000000000000000000000000000000000000000000000000000000",
                "feeRecipient": "0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b"
            }
        ],
        "id": None,
        "expect": {
            "status": "SUCCESS",
            "payloadId": "0xa247243752eb10b4"
        }
    }
payloadExecute = {
        "method": "engine_executePayloadV1",
        "params": [
            {
                "parentHash": "0x3b8fb240d288781d4aac94d3fd16809ee413bc99294a085798a589dae51ddd4a",
                "coinbase": "0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b",
                "stateRoot": "0xca3149fa9e37db08d1cd49c9061db1002ef1cd58db2210f2115c8c989b2bdf45",
                "receiptRoot": "0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421",
                "logsBloom": "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                "random": "0x0000000000000000000000000000000000000000000000000000000000000000",
                "blockNumber": "0x1",
                "gasLimit": "0x1c9c380",
                "gasUsed": "0x0",
                "timestamp": "0x5",
                "extraData": "0x",
                "baseFeePerGas": "0x7",
                "blockHash": "0x3559e851470f6e7bbed1db474980683e8c315bfce99b2a6ef47c057c04de7858",
                "transactions": []
            }
        ],
        "id": 69,
        "expect": {
            "status": "VALID",
            "latestValidHash": "0x3559e851470f6e7bbed1db474980683e8c315bfce99b2a6ef47c057c04de7858"
        }
    }

payloadGet = {
        "method": "engine_getPayloadV1",
        "params": [
            "0xa247243752eb10b4"
        ],
        "id": 68,
        "expect": {
            "parentHash": "0x3b8fb240d288781d4aac94d3fd16809ee413bc99294a085798a589dae51ddd4a",
            "coinbase": "0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b",
            "stateRoot": "0xca3149fa9e37db08d1cd49c9061db1002ef1cd58db2210f2115c8c989b2bdf45",
            "receiptRoot": "0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421",
            "logsBloom": "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            "random": "0x0000000000000000000000000000000000000000000000000000000000000000",
            "blockNumber": "0x1",
            "gasLimit": "0x1c9c380",
            "gasUsed": "0x0",
            "timestamp": "0x5",
            "extraData": "0x",
            "baseFeePerGas": "0x7",
            "blockHash": "0x3559e851470f6e7bbed1db474980683e8c315bfce99b2a6ef47c057c04de7858",
            "transactions": []
        }
    }

payloadForkChoice = {
        "method": "engine_forkchoiceUpdatedV1",
        "params": [
            {
                "headBlockHash": "0x3559e851470f6e7bbed1db474980683e8c315bfce99b2a6ef47c057c04de7858",
                "safeBlockHash": "0x3559e851470f6e7bbed1db474980683e8c315bfce99b2a6ef47c057c04de7858",
                "finalizedBlockHash": "0x3b8fb240d288781d4aac94d3fd16809ee413bc99294a085798a589dae51ddd4a"
            },
            None
        ],
        "id": 70,
        "expect": {
            "status": "SUCCESS",
            "payloadId": "0x"
        }
    }

currentId = 67
steps = []

currentId += 1
genesisRevertForkChoice["id"] = currentId
currentId += 1
payloadExecute["id"] = currentId
currentId += 1
payloadGet["id"] = currentId

steps = [genesisRevertForkChoice.copy(), payloadExecute.copy(), payloadGet.copy()]

for n in range(100):
    currentId += 1
    genesisRevertForkChoice["id"] = currentId
    currentId += 1
    payloadForkChoice["id"] = currentId
    steps += [genesisRevertForkChoice.copy(), payloadForkChoice.copy()]
