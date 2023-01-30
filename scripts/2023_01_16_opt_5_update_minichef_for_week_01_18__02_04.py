import math

from ape_safe import ApeSafe
from brownie import ZERO_ADDRESS, Contract, accounts, history, network

from helpers import (
    CHAIN_IDS,
    GNOSIS_SAFE_BASE_URLS,
    MINICHEF_ADDRESSES,
    OPS_MULTISIG_ADDRESSES,
    SECOND_WEEK_HALVED_SIDECHAIN_TOTAL_EMISSION_RATE,
    SIDECHAIN_TOTAL_EMISSION_RATE,
)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "OPTIMISM"


def main():
    """
    Updates minichef parameters on Optimism network for week 01/04 - 01/18
    Vote: https://snapshot.org/#/saddlefinance.eth/proposal/0x706a9e600d66fabe316696588dd689acb6ed01b193510effb6bf220b585ce716
    """
    print(f"You are using the '{network.show_active()}' network")
    assert (
        network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    ), f"Not on {TARGET_NETWORK} network"

    ##### Update Minichef weights #####
    multisig = ApeSafe(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        GNOSIS_SAFE_BASE_URLS[CHAIN_IDS[TARGET_NETWORK]],
        multisend="0x998739BFdAAdde7C933B942a68053933098f9EDa",
    )

    minichef = multisig.contract(MINICHEF_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    # Prepare an array of calldata to execute using batch function
    batch_calldata = []

    # Mass update pools to checkpoint existing stakers
    pids = [1, 2, 3, 4, 5, 7]
    batch_calldata.append(minichef.massUpdatePools.encode_input(pids))

    # 37.49% for Optimism: FraxBP
    assert minichef.lpToken(1) == "0xf74ebe6e5586275dc4CeD78F5DBEF31B1EfbE7a5"
    if minichef.poolInfo(1)[2] != 3749:
        batch_calldata.append(minichef.set.encode_input(1, 3749, ZERO_ADDRESS, False))

    # 5.00% for Optimism: FraxBP-optUSD
    assert minichef.lpToken(2) == "0xfF5fa61Eb9b5cDD63bdFa16EF029d5313457925A"
    if minichef.poolInfo(2)[2] != 500:
        batch_calldata.append(minichef.set.encode_input(2, 500, ZERO_ADDRESS, False))

    # 3.00% for Optimism: FraxBP-USDT
    assert minichef.lpToken(3) == "0xb63d7B0D835ca6eFf89ab774498ed6dD0D71e93e"
    if minichef.poolInfo(3)[2] != 300:
        batch_calldata.append(minichef.set.encode_input(3, 300, ZERO_ADDRESS, False))

    # 5.01% for Optimism: FraxBP-SUSD
    assert minichef.lpToken(4) == "0x205c9B8c1fCa803B779b1eB4B887Aa0E00FE629F"
    if minichef.poolInfo(4)[2] != 501:
        batch_calldata.append(minichef.set.encode_input(4, 501, ZERO_ADDRESS, False))

    # 0.00% for Optimism: optUSD
    assert minichef.lpToken(5) == "0xcCf860874cbF2d615192a4C4455580B4d622D3B9"
    if minichef.poolInfo(5)[2] != 0:
        batch_calldata.append(minichef.set.encode_input(5, 0, ZERO_ADDRESS, False))

    # Should always be 0.00% for pid 6.
    # This is not a LP token address. Pool address was added by mistake.
    assert minichef.lpToken(6) == "0xc55E8C79e5A6c3216D4023769559D06fa9A7732e"
    assert minichef.poolInfo(6)[2] == 0

    # 2.00% for Optimism: saddleOptUSX-FRAXBP
    assert minichef.lpToken(7) == "0xf349fB2b5eD45864e1d9ad34a483Eb37aC6e0034"
    if minichef.poolInfo(7)[2] != 200:
        batch_calldata.append(minichef.set.encode_input(7, 200, ZERO_ADDRESS, False))

    # Calculate new saddle per second on Optimism
    new_rate = math.floor(
        SECOND_WEEK_HALVED_SIDECHAIN_TOTAL_EMISSION_RATE * 5250 / 10000
    )
    batch_calldata.append(minichef.setSaddlePerSecond.encode_input(new_rate))

    # Execute batch call
    minichef.batch(batch_calldata, True)

    # Check state variables are updated correctly
    assert minichef.poolInfo(1)[2] == 3749
    assert minichef.poolInfo(2)[2] == 500
    assert minichef.poolInfo(3)[2] == 300
    assert minichef.poolInfo(4)[2] == 501
    assert minichef.poolInfo(5)[2] == 0
    assert minichef.poolInfo(6)[2] == 0
    assert minichef.poolInfo(7)[2] == 200
    assert minichef.totalAllocPoint() == 5250
    assert minichef.saddlePerSecond() == new_rate

    print(f"New MiniChef rate on {TARGET_NETWORK} is {new_rate}")

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 5

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
