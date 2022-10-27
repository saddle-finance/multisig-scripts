import math

from brownie import ZERO_ADDRESS, Contract, accounts, history, network
from helpers import CHAIN_IDS, MINICHEF_ADDRESSES, SIDECHAIN_TOTAL_EMISSION_RATE

TARGET_NETWORK = "OPTIMISM"


def main():
    """
    Updates Optimism pool and minichef parameters on Optimism network for week 10/27 - 11/04
    Vote: https://snapshot.org/#/saddlefinance.eth/proposal/0x1856bafbeee381c68b1872954bcaf4cbc048e5c0057894947d70b5133ab16203
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

    # 35.63% for Optimism: FraxBP
    assert minichef.lpToken(1) == "0xf74ebe6e5586275dc4CeD78F5DBEF31B1EfbE7a5"
    minichef.set(1, 3563, ZERO_ADDRESS, False)
    assert minichef.poolInfo(1)[2] == 3563

    # 4.46% for Optimism: frax-optUSD
    assert minichef.lpToken(2) == "0xfF5fa61Eb9b5cDD63bdFa16EF029d5313457925A"
    minichef.set(2, 446, ZERO_ADDRESS, False)
    assert minichef.poolInfo(2)[2] == 446

    # 2.67% for Optimism: Frax-USDT
    assert minichef.lpToken(3) == "0xb63d7B0D835ca6eFf89ab774498ed6dD0D71e93e"
    minichef.set(3, 267, ZERO_ADDRESS, False)
    assert minichef.poolInfo(3)[2] == 267

    # 4.46% for Optimism: Frax-SUSD
    assert minichef.lpToken(4) == "0x205c9B8c1fCa803B779b1eB4B887Aa0E00FE629F"
    minichef.set(4, 446, ZERO_ADDRESS, False)
    assert minichef.poolInfo(4)[2] == 446

    # 0.00% for Optimism: optUSD
    assert minichef.lpToken(5) == "0xcCf860874cbF2d615192a4C4455580B4d622D3B9"
    minichef.set(5, 0, ZERO_ADDRESS, False)
    assert minichef.poolInfo(5)[2] == 0

    # Should always be 0.00% for pid 6.
    # This is not a LP token address. Pool address was added by mistake.
    assert minichef.lpToken(6) == "0xc55E8C79e5A6c3216D4023769559D06fa9A7732e"
    minichef.set(6, 0, ZERO_ADDRESS, False)
    assert minichef.poolInfo(6)[2] == 0

    # 3.65% for Optimism: saddleOptUSX-FRAXBP
    assert minichef.lpToken(7) == "0xf349fB2b5eD45864e1d9ad34a483Eb37aC6e0034"
    minichef.set(7, 365, ZERO_ADDRESS, False)
    assert minichef.poolInfo(7)[2] == 365

    # Total allocation is 50.87% for Optimsim
    assert minichef.totalAllocPoint() == 5087

    new_rate = math.floor(SIDECHAIN_TOTAL_EMISSION_RATE * 5087 / 10000)
    minichef.setSaddlePerSecond(new_rate)
    applied_saddle_per_second = minichef.saddlePerSecond()
    assert applied_saddle_per_second == new_rate

    print(f"New MiniChef rate on {TARGET_NETWORK} is {applied_saddle_per_second}")

    for tx in history:
        tx.info()
    return
