import math

from ape_safe import ApeSafe
from brownie import ZERO_ADDRESS, Contract, accounts, history, network

from helpers import (
    CHAIN_IDS,
    FIRST_WEEK_HALVED_SIDECHAIN_TOTAL_EMISSION_RATE,
    GNOSIS_SAFE_BASE_URLS,
    MINICHEF_ADDRESSES,
    OPS_MULTISIG_ADDRESSES,
    SIDECHAIN_TOTAL_EMISSION_RATE,
)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "OPTIMISM"


def main():
    """
    Half reward emission rate as per below sip.
    Vote: https://snapshot.org/#/saddlefinance.eth/proposal/0xfbc83d80649b7f7cd4e0c430e90b412cfdea9c85e8584245247ef05b14eeaf7b
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

    # Calculate new saddle per second on Optimism
    new_rate = math.floor(
        FIRST_WEEK_HALVED_SIDECHAIN_TOTAL_EMISSION_RATE * 5310 / 10000
    )
    batch_calldata.append(minichef.setSaddlePerSecond.encode_input(new_rate))

    # Execute batch call
    minichef.batch(batch_calldata, True)

    assert minichef.saddlePerSecond() == new_rate

    print(f"New MiniChef rate on {TARGET_NETWORK} is {new_rate}")

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 4

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
