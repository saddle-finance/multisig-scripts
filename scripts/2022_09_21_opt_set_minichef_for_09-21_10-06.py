import json
import math

from brownie import ZERO_ADDRESS, Contract, accounts, network
from helpers import (
    CHAIN_IDS,
    MINICHEF_ABI,
    MINICHEF_ADDRESSES,
    SIDECHAIN_TOTAL_EMISSION_RATE,
)


def main():
    """
    Updates Optimism minichef parameters
    https://snapshot.org/#/saddlefinance.eth/proposal/0xd424d467ac93c89f9a856abce690577b22bc89f6472445a6f60143f16ce75ba1

    """

    TARGET_NETWORK = "OPTIMISM"

    print(f"You are using the '{network.show_active()}' network")
    assert (
        network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    ), f"Not on {TARGET_NETWORK} network"

    deployer = accounts.load("deployer")  # prompts for password

    ##### Update Minichef weights #####
    f = open("abi.json")
    j = json.load(f)
    address = MINICHEF_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    minichef = Contract.from_abi("MinichefV2", address, MINICHEF_ABI)

    pids = [1, 2, 3, 4, 5]
    minichef.massUpdatePools(pids, {"from": deployer})

    # 31.59% for Optimism: FraxBP
    assert minichef.lpToken(1) == "0xf74ebe6e5586275dc4CeD78F5DBEF31B1EfbE7a5"
    minichef.set(1, 3159, ZERO_ADDRESS, False, {"from": deployer})
    assert minichef.poolInfo(1)[2] == 3159

    # 3.90% for Optimism: Frax-optUSD
    assert minichef.lpToken(6) == "0xc55E8C79e5A6c3216D4023769559D06fa9A7732e"
    minichef.set(6, 390, ZERO_ADDRESS, False, {"from": deployer})
    assert minichef.poolInfo(6)[2] == 390

    # 12.64% for Optimism: Frax-USDT
    assert minichef.lpToken(3) == "0xb63d7B0D835ca6eFf89ab774498ed6dD0D71e93e"
    minichef.set(3, 1264, ZERO_ADDRESS, False, {"from": deployer})
    assert minichef.poolInfo(3)[2] == 1264

    # 12.64% for Optimism: Frax-SUSD
    assert minichef.lpToken(4) == "0x205c9B8c1fCa803B779b1eB4B887Aa0E00FE629F"
    minichef.set(4, 1264, ZERO_ADDRESS, False, {"from": deployer})
    assert minichef.poolInfo(4)[2] == 1264

    # 0.01% for Optimism: optUSD
    assert minichef.lpToken(5) == "0xcCf860874cbF2d615192a4C4455580B4d622D3B9"
    minichef.set(5, 1, ZERO_ADDRESS, False, {"from": deployer})
    assert minichef.poolInfo(5)[2] == 1

    # 0.00% for Optimism: optSaddle3pool - FRAX
    assert minichef.lpToken(2) == "0xfF5fa61Eb9b5cDD63bdFa16EF029d5313457925A"
    minichef.set(2, 0, ZERO_ADDRESS, False, {"from": deployer})
    assert minichef.poolInfo(2)[2] == 0

    # Total allocation is 60.78% for Optimism

    assert minichef.totalAllocPoint() == 6078

    new_rate = math.floor(SIDECHAIN_TOTAL_EMISSION_RATE * 6078 / 10000)
    # 417159027777777792
    print(new_rate)
    minichef.setSaddlePerSecond(new_rate, {"from": deployer})
    print(minichef.saddlePerSecond())
    assert minichef.saddlePerSecond() == new_rate
