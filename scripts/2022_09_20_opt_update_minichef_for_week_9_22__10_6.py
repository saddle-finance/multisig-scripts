import math
import json
from helpers import (
    CHAIN_IDS,
    MINICHEF_ADDRESSES,
    MULTISIG_ADDRESSES,
    SIDECHAIN_TOTAL_EMISSION_RATE,
)

# from ape_safe import ApeSafe
from brownie import ZERO_ADDRESS, Contract, accounts, network

# from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "OPTIMISM"


def main():
    """
    Updates Optimism pool and minichef parameters on Optimism network for week 9/22 - 10/6
    Vote: https://snapshot.org/#/saddlefinance.eth/proposal/0xd424d467ac93c89f9a856abce690577b22bc89f6472445a6f60143f16ce75ba1

    """
    print(f"You are using the '{network.show_active()}' network")
    assert (
        network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    ), f"Not on {TARGET_NETWORK} network"

    deployer = accounts.load("deployer")  # prompts for password
    # multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    ##### Update Minichef weights #####
    f = open("abi.json")
    j = json.load(f)
    address = j["address"]
    abi = j["abi"]
    minichef = Contract.from_abi("MinichefV2", address, abi)

    # minichef = Contract.from_abi(MINICHEF_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    # mass update pools to checkpoint existing stakers
    pids = [1, 2, 3, 4, 5]
    minichef.massUpdatePools(pids, {"from": deployer})

    # 31.59% for Optimism: FraxBP
    assert minichef.lpToken(1) == "0xf74ebe6e5586275dc4CeD78F5DBEF31B1EfbE7a5"
    minichef.set(1, 3159, ZERO_ADDRESS, False, {"from": deployer})
    assert minichef.poolInfo(1)[2] == 3159

    # Should always be 0.00% for pid 6
    assert minichef.lpToken(6) == "0xc55E8C79e5A6c3216D4023769559D06fa9A7732e"
    minichef.set(6, 0, ZERO_ADDRESS, False, {"from": deployer})
    assert minichef.poolInfo(6)[2] == 0

    # 12.64% for Optimism: Frax-USDT
    assert minichef.lpToken(3) == "0xb63d7B0D835ca6eFf89ab774498ed6dD0D71e93e"
    minichef.set(3, 1264, ZERO_ADDRESS, False, {"from": deployer})
    assert minichef.poolInfo(3)[2] == 1264

    # 12.64% for Optimism: Frax-SUSD
    assert minichef.lpToken(4) == "0x205c9B8c1fCa803B779b1eB4B887Aa0E00FE629F"
    minichef.set(4, 1264, ZERO_ADDRESS, False, {"from": deployer})
    assert minichef.poolInfo(4)[2] == 1264

    # 0.00% for Optimism: optUSD
    assert minichef.lpToken(5) == "0xcCf860874cbF2d615192a4C4455580B4d622D3B9"
    minichef.set(5, 1, ZERO_ADDRESS, False, {"from": deployer})
    assert minichef.poolInfo(5)[2] == 1

    # 3.90% for Optimism: frax-optUSD
    assert minichef.lpToken(2) == "0xfF5fa61Eb9b5cDD63bdFa16EF029d5313457925A"
    minichef.set(2, 390, ZERO_ADDRESS, False, {"from": deployer})
    assert minichef.poolInfo(2)[2] == 390

    # Total allocation is 52.25% for Arbitrum

    assert minichef.totalAllocPoint() == 6078

    new_rate = math.floor(SIDECHAIN_TOTAL_EMISSION_RATE * 6078 / 10000)
    print(new_rate)
    minichef.setSaddlePerSecond(new_rate, {"from": deployer})
    print(minichef.saddlePerSecond())
    assert minichef.saddlePerSecond() == new_rate

    # # combine history into multisend txn
    # safe_tx = multisig.multisend_from_receipts()
    # safe_tx.safe_nonce = 4

    # # sign with private key
    # safe_tx.sign(deployer.private_key)
    # multisig.preview(safe_tx)

    # confirm_posting_transaction(multisig, safe_tx)
