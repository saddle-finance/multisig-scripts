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


def main():
    """
    Updates Arbitrum pool and minichef parameters on Arbitrum network
    https://snapshot.org/#/saddlefinance.eth/proposal/0xe32db5de6b40e46617ea2e39552d8a1f1485bc86eeb2fa7bc89205f2156c0939

    """

    TARGET_NETWORK = "OPTIMISM"

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

    # 38.33% for Optimism: FraxBP
    assert minichef.lpToken(1) == "0xf74ebe6e5586275dc4CeD78F5DBEF31B1EfbE7a5"
    minichef.set(1, 3833, ZERO_ADDRESS, False, {"from": deployer})
    assert minichef.poolInfo(1)[2] == 3833

    # 4.93% for Optimism: Frax-optUSD
    # also needs to be added to minichef
    assert minichef.lpToken(6) == "0xc55E8C79e5A6c3216D4023769559D06fa9A7732e"
    minichef.set(6, 493, ZERO_ADDRESS, False, {"from": deployer})
    assert minichef.poolInfo(6)[2] == 493

    # 4.93% for Optimism: Frax-USDT
    assert minichef.lpToken(3) == "0xb63d7B0D835ca6eFf89ab774498ed6dD0D71e93e"
    minichef.set(3, 493, ZERO_ADDRESS, False, {"from": deployer})
    assert minichef.poolInfo(3)[2] == 493

    # 4.93% for Optimism: Frax-SUSD
    assert minichef.lpToken(4) == "0x205c9B8c1fCa803B779b1eB4B887Aa0E00FE629F"
    minichef.set(4, 493, ZERO_ADDRESS, False, {"from": deployer})
    assert minichef.poolInfo(4)[2] == 493

    # 0.02% for Optimism: optUSD
    assert minichef.lpToken(5) == "0xcCf860874cbF2d615192a4C4455580B4d622D3B9"
    minichef.set(5, 2, ZERO_ADDRESS, False, {"from": deployer})
    assert minichef.poolInfo(5)[2] == 2

    # 0.00% for Optimism: optSaddle3pool - FRAX
    assert minichef.lpToken(2) == "0xfF5fa61Eb9b5cDD63bdFa16EF029d5313457925A"
    minichef.set(2, 0, ZERO_ADDRESS, False, {"from": deployer})
    assert minichef.poolInfo(2)[2] == 0

    # Total allocation is 53.14% for Arbitrum

    assert minichef.totalAllocPoint() == 5314

    new_rate = math.floor(SIDECHAIN_TOTAL_EMISSION_RATE * 5314 / 10000)
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
