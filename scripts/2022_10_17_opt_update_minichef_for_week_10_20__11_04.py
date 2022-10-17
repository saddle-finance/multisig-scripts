import math

from brownie import ZERO_ADDRESS, Contract, accounts, history, network
from helpers import CHAIN_IDS, MINICHEF_ADDRESSES, SIDECHAIN_TOTAL_EMISSION_RATE

TARGET_NETWORK = "OPTIMISM"


def main():
    """
    Updates Optimism pool and minichef parameters on Optimism network for week 10/20 - 11/04
    Vote: https://snapshot.org/#/saddlefinance.eth/proposal/0x783103362decf36948c6cb8e1c4d74579a218c246ec8da67b517279ceb33918a
    """
    print(f"You are using the '{network.show_active()}' network")
    assert (
        network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    ), f"Not on {TARGET_NETWORK} network"

    deployer = accounts.load("deployer")  # prompts for password

    ##### Update Minichef weights #####
    minichef = Contract.from_explorer(
        MINICHEF_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]], None, deployer
    )

    # mass update pools to checkpoint existing stakers
    pids = [1, 2, 3, 4, 5, 7]
    minichef.massUpdatePools(pids)

    # 32.01% for Optimism: FraxBP
    assert minichef.lpToken(1) == "0xf74ebe6e5586275dc4CeD78F5DBEF31B1EfbE7a5"
    minichef.set(1, 3219, ZERO_ADDRESS, False)
    assert minichef.poolInfo(1)[2] == 3219

    # 3.48% for Optimism: frax-optUSD
    assert minichef.lpToken(2) == "0xfF5fa61Eb9b5cDD63bdFa16EF029d5313457925A"
    minichef.set(2, 2, ZERO_ADDRESS, False)
    assert minichef.poolInfo(2)[2] == 2

    # 8.50% for Optimism: Frax-USDT
    assert minichef.lpToken(3) == "0xb63d7B0D835ca6eFf89ab774498ed6dD0D71e93e"
    minichef.set(3, 1051, ZERO_ADDRESS, False)
    assert minichef.poolInfo(3)[2] == 1051

    # 8.49% for Optimism: Frax-SUSD
    assert minichef.lpToken(4) == "0x205c9B8c1fCa803B779b1eB4B887Aa0E00FE629F"
    minichef.set(4, 1051, ZERO_ADDRESS, False)
    assert minichef.poolInfo(4)[2] == 1051

    # 0.00% for Optimism: optUSD
    assert minichef.lpToken(5) == "0xcCf860874cbF2d615192a4C4455580B4d622D3B9"
    minichef.set(5, 385, ZERO_ADDRESS, False)
    assert minichef.poolInfo(5)[2] == 385

    # Should always be 0.00% for pid 6.
    # This is not a LP token address. Pool address was added by mistake.
    assert minichef.lpToken(6) == "0xc55E8C79e5A6c3216D4023769559D06fa9A7732e"
    minichef.set(6, 0, ZERO_ADDRESS, False)
    assert minichef.poolInfo(6)[2] == 0

    # 0.00% for Optimism: saddleOptUSX-FRAXBP
    assert minichef.lpToken(7) == "0xf349fB2b5eD45864e1d9ad34a483Eb37aC6e0034"
    minichef.set(5, 0, ZERO_ADDRESS, False)
    assert minichef.poolInfo(7)[2] == 0

    # Total allocation is 52.48% for Arbitrum
    assert minichef.totalAllocPoint() == 5708

    new_rate = math.floor(SIDECHAIN_TOTAL_EMISSION_RATE * 5708 / 10000)
    minichef.setSaddlePerSecond(new_rate)
    applied_saddle_per_second = minichef.saddlePerSecond()
    assert applied_saddle_per_second == new_rate

    print(f"New MiniChef rate on {TARGET_NETWORK} is {applied_saddle_per_second}")

    for tx in history:
        tx.info()
    return
