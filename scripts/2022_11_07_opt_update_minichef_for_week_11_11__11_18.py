import math

from brownie import ZERO_ADDRESS, Contract, accounts, history, network
from helpers import CHAIN_IDS, MINICHEF_ADDRESSES, SIDECHAIN_TOTAL_EMISSION_RATE

TARGET_NETWORK = "OPTIMISM"


def main():
    """
    Updates minichef parameters on Optimism network for week 11/11 - 11/18
    Vote: https://snapshot.org/#/saddlefinance.eth/proposal/0x4ae8365b6ea6420a92b4b06810c3e193961035ebbde803de48a030d7906744fd
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

    # Prepare an array of calldata to execute using batch function
    batch_calldata = []

    # Mass update pools to checkpoint existing stakers
    pids = [1, 2, 3, 4, 5, 7]
    batch_calldata.append(minichef.massUpdatePools.encode_input(pids))

    # 34.81% for Optimism: FraxBP
    assert minichef.lpToken(1) == "0xf74ebe6e5586275dc4CeD78F5DBEF31B1EfbE7a5"
    if minichef.poolInfo(1)[2] != 3481:
        batch_calldata.append(minichef.set.encode_input(1, 3481, ZERO_ADDRESS, False))

    # 4.57% for Optimism: frax-optUSD
    assert minichef.lpToken(2) == "0xfF5fa61Eb9b5cDD63bdFa16EF029d5313457925A"
    if minichef.poolInfo(2)[2] != 457:
        batch_calldata.append(minichef.set.encode_input(2, 457, ZERO_ADDRESS, False))

    # 2.74% for Optimism: Frax-USDT
    assert minichef.lpToken(3) == "0xb63d7B0D835ca6eFf89ab774498ed6dD0D71e93e"
    if minichef.poolInfo(3)[2] != 274:
        batch_calldata.append(minichef.set.encode_input(3, 274, ZERO_ADDRESS, False))

    # 4.56% for Optimism: Frax-SUSD
    assert minichef.lpToken(4) == "0x205c9B8c1fCa803B779b1eB4B887Aa0E00FE629F"
    if minichef.poolInfo(4)[2] != 456:
        batch_calldata.append(minichef.set.encode_input(4, 456, ZERO_ADDRESS, False))

    # 0.01% for Optimism: optUSD
    assert minichef.lpToken(5) == "0xcCf860874cbF2d615192a4C4455580B4d622D3B9"
    if minichef.poolInfo(5)[2] != 1:
        batch_calldata.append(minichef.set.encode_input(5, 1, ZERO_ADDRESS, False))

    # Should always be 0.00% for pid 6.
    # This is not a LP token address. Pool address was added by mistake.
    assert minichef.lpToken(6) == "0xc55E8C79e5A6c3216D4023769559D06fa9A7732e"
    assert minichef.poolInfo(6)[2] == 0

    # 2.12% for Optimism: saddleOptUSX-FRAXBP
    assert minichef.lpToken(7) == "0xf349fB2b5eD45864e1d9ad34a483Eb37aC6e0034"
    if minichef.poolInfo(7)[2] != 212:
        batch_calldata.append(minichef.set.encode_input(7, 212, ZERO_ADDRESS, False))

    # Calculate new saddle per second on Optimism
    new_rate = math.floor(SIDECHAIN_TOTAL_EMISSION_RATE * 4881 / 10000)
    batch_calldata.append(minichef.setSaddlePerSecond.encode_input(new_rate))

    # Execute batch call
    minichef.batch(batch_calldata, True)

    # Check state variables are updated correctly
    assert minichef.poolInfo(1)[2] == 3481
    assert minichef.poolInfo(2)[2] == 457
    assert minichef.poolInfo(3)[2] == 274
    assert minichef.poolInfo(4)[2] == 456
    assert minichef.poolInfo(5)[2] == 1
    assert minichef.poolInfo(6)[2] == 0
    assert minichef.poolInfo(7)[2] == 212
    assert minichef.totalAllocPoint() == 4881
    assert minichef.saddlePerSecond() == new_rate

    print(f"New MiniChef rate on {TARGET_NETWORK} is {new_rate}")

    for tx in history:
        tx.info()
    return
