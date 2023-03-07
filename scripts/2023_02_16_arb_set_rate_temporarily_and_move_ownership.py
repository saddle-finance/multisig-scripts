import math
from datetime import datetime, timedelta

from ape_safe import ApeSafe
from brownie import ZERO_ADDRESS, Contract, accounts, network

from helpers import (CHAIN_IDS, GNOSIS_SAFE_BASE_URLS, MINICHEF_ADDRESSES,
                     MULTISIG_ADDRESSES, OPS_MULTISIG_ADDRESSES)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "ARBITRUM"


def main():
    """
    PID 3 has a rounding error that blocks pending rewards from being claimed
    In order to address this, we set the minchef's SDL per second to 2_500_000
    and PID 3 weight to 10000. This will allow the pending rewards to be claimed after 1 day.

    In order to execute this timely, we will move ownership of the minichef to the ops multisig.
    """

    print(f"You are using the '{network.show_active()}' network")
    assert (
        network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    ), f"Not on {TARGET_NETWORK} network"

    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        GNOSIS_SAFE_BASE_URLS[CHAIN_IDS[TARGET_NETWORK]],
    )
    deployer = accounts.load("deployer")

    ##### Update Minichef weights #####

    PID = 3
    NEW_ALLOC_POINT = 1000
    NEW_SDL_PER_SECOND = 2_500_000

    minichef = multisig.get_contract(
        MINICHEF_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    # Less than 1e-6 of SDL per day
    minichef.setSaddlePerSecond(NEW_SDL_PER_SECOND)

    # 0.00% saddleFraxBP
    assert minichef.lpToken(
        PID) == "0x896935B02D3cBEb152192774e4F1991bb1D2ED3f"
    if minichef.poolInfo(PID)[2] != NEW_ALLOC_POINT:
        minichef.set(PID, NEW_ALLOC_POINT, ZERO_ADDRESS, False)

    # Total allocation is 1001, 1 from placeholder and 1000 from PID 3
    assert minichef.totalAllocPoint() == NEW_ALLOC_POINT + 1
    assert minichef.saddlePerSecond() == NEW_SDL_PER_SECOND

    # Move ownership to ops multisig
    minichef.transferOwnership(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]], False, False)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 26

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
