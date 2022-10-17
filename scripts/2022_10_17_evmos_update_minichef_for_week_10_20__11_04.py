import math

from brownie import ZERO_ADDRESS, Contract, accounts, history, network
from helpers import CHAIN_IDS, MINICHEF_ADDRESSES, SIDECHAIN_TOTAL_EMISSION_RATE

TARGET_NETWORK = "EVMOS"


def main():
    """
    Updates Evmos pool and minichef parameters on Evmos network for week 10/20 - 11/04
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

    # add saddleCelarUSDTPool to minichef with 0.00%
    minichef.add(0, "0xfd9c6a9cAf5A884C76Ea802A2634Fb914D1Bc022", ZERO_ADDRESS)
    assert minichef.lpToken(7) == "0xfd9c6a9cAf5A884C76Ea802A2634Fb914D1Bc022"

    # mass update pools to checkpoint existing stakers
    pids = [1]
    minichef.massUpdatePools(pids)

    # 0.00% for Evmos: Frax3Pool (outdated should always be 0)
    assert minichef.lpToken(1) == "0xf74ebe6e5586275dc4CeD78F5DBEF31B1EfbE7a5"
    minichef.set(1, 0, ZERO_ADDRESS, False)
    assert minichef.poolInfo(1)[2] == 0

    # Total allocation is 52.48% for Arbitrum
    assert minichef.totalAllocPoint() == 0

    new_rate = math.floor(SIDECHAIN_TOTAL_EMISSION_RATE * 0 / 10000)
    minichef.setSaddlePerSecond(new_rate)
    applied_saddle_per_second = minichef.saddlePerSecond()
    assert applied_saddle_per_second == new_rate

    print(f"New MiniChef rate on {TARGET_NETWORK} is {applied_saddle_per_second}")

    for tx in history:
        tx.info()
    return
