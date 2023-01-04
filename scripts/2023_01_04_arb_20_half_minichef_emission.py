import math

from ape_safe import ApeSafe
from brownie import accounts, network

from helpers import (
    CHAIN_IDS,
    FIRST_WEEK_HALVED_SIDECHAIN_TOTAL_EMISSION_RATE,
    GNOSIS_SAFE_BASE_URLS,
    MINICHEF_ADDRESSES,
    MULTISIG_ADDRESSES,
)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "ARBITRUM"


def main():
    """
    Half reward emission rate as per below sip.
    Vote: https://snapshot.org/#/saddlefinance.eth/proposal/0xfbc83d80649b7f7cd4e0c430e90b412cfdea9c85e8584245247ef05b14eeaf7b
    """

    print(f"You are using the '{network.show_active()}' network")
    assert (
        network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    ), f"Not on {TARGET_NETWORK} network"

    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        GNOSIS_SAFE_BASE_URLS[CHAIN_IDS[TARGET_NETWORK]],
    )

    ##### Update Minichef weights #####

    minichef = multisig.contract(MINICHEF_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    # mass update pools to checkpoint existing stakers
    pids = [1, 2, 3, 4, 5, 6, 7, 8]
    minichef.massUpdatePools(pids)

    new_rate = math.floor(
        FIRST_WEEK_HALVED_SIDECHAIN_TOTAL_EMISSION_RATE * 4689 / 10000
    )
    minichef.setSaddlePerSecond(new_rate)

    assert minichef.saddlePerSecond() == new_rate

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 20

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx, False)

    confirm_posting_transaction(multisig, safe_tx)
