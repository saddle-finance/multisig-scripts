import math

from ape_safe import ApeSafe
from brownie import ZERO_ADDRESS, Contract, accounts, history, network

from helpers import (
    CHAIN_IDS,
    MINICHEF_ADDRESSES,
    OPS_MULTISIG_ADDRESSES,
    SIDECHAIN_TOTAL_EMISSION_RATE,
)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "OPTIMISM"


def main():
    """
    Updates minichef parameters on Optimism network for week 11/21 - 12/07
    Vote: https://snapshot.org/#/saddlefinance.eth/proposal/0x508226028d3a401df05f84aa4f6292f5dde8db55d5aa10804f73794a02dbf5f0
    """
    print(f"You are using the '{network.show_active()}' network")
    assert (
        network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    ), f"Not on {TARGET_NETWORK} network"

    deployer = accounts.load("deployer")  # prompts for password

    ##### Update Minichef weights #####
    multisig = ApeSafe(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url="https://safe-transaction-optimism.safe.global",
    )

    minichef = multisig.contract(MINICHEF_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    # Prepare an array of calldata to execute using batch function
    batch_calldata = []

    # Mass update pools to checkpoint existing stakers
    pids = [1, 2, 3, 4, 5, 7]
    batch_calldata.append(minichef.massUpdatePools.encode_input(pids))

    # 38.20% for Optimism: FraxBP
    assert minichef.lpToken(1) == "0xf74ebe6e5586275dc4CeD78F5DBEF31B1EfbE7a5"
    if minichef.poolInfo(1)[2] != 3820:
        batch_calldata.append(minichef.set.encode_input(1, 3820, ZERO_ADDRESS, False))

    # 4.92% for Optimism: frax-optUSD
    assert minichef.lpToken(2) == "0xfF5fa61Eb9b5cDD63bdFa16EF029d5313457925A"
    if minichef.poolInfo(2)[2] != 492:
        batch_calldata.append(minichef.set.encode_input(2, 492, ZERO_ADDRESS, False))

    # 2.95% for Optimism: Frax-USDT
    assert minichef.lpToken(3) == "0xb63d7B0D835ca6eFf89ab774498ed6dD0D71e93e"
    if minichef.poolInfo(3)[2] != 295:
        batch_calldata.append(minichef.set.encode_input(3, 295, ZERO_ADDRESS, False))

    # 4.93% for Optimism: Frax-SUSD
    assert minichef.lpToken(4) == "0x205c9B8c1fCa803B779b1eB4B887Aa0E00FE629F"
    if minichef.poolInfo(4)[2] != 493:
        batch_calldata.append(minichef.set.encode_input(4, 493, ZERO_ADDRESS, False))

    # 0.00% for Optimism: optUSD
    assert minichef.lpToken(5) == "0xcCf860874cbF2d615192a4C4455580B4d622D3B9"
    if minichef.poolInfo(5)[2] != 0:
        batch_calldata.append(minichef.set.encode_input(5, 0, ZERO_ADDRESS, False))

    # Should always be 0.00% for pid 6.
    # This is not a LP token address. Pool address was added by mistake.
    assert minichef.lpToken(6) == "0xc55E8C79e5A6c3216D4023769559D06fa9A7732e"
    assert minichef.poolInfo(6)[2] == 0

    # 1.98% for Optimism: saddleOptUSX-FRAXBP
    assert minichef.lpToken(7) == "0xf349fB2b5eD45864e1d9ad34a483Eb37aC6e0034"
    if minichef.poolInfo(7)[2] != 198:
        batch_calldata.append(minichef.set.encode_input(7, 198, ZERO_ADDRESS, False))

    # Calculate new saddle per second on Optimism
    new_rate = math.floor(SIDECHAIN_TOTAL_EMISSION_RATE * 4881 / 10000)
    batch_calldata.append(minichef.setSaddlePerSecond.encode_input(new_rate))

    # Execute batch call
    minichef.batch(batch_calldata, True)

    # Check state variables are updated correctly
    assert minichef.poolInfo(1)[2] == 3820
    assert minichef.poolInfo(2)[2] == 492
    assert minichef.poolInfo(3)[2] == 295
    assert minichef.poolInfo(4)[2] == 493
    assert minichef.poolInfo(5)[2] == 0
    assert minichef.poolInfo(6)[2] == 0
    assert minichef.poolInfo(7)[2] == 198
    assert minichef.totalAllocPoint() == 5298
    assert minichef.saddlePerSecond() == new_rate

    print(f"New MiniChef rate on {TARGET_NETWORK} is {new_rate}")

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 0

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
