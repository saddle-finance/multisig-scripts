from helpers import (
    CHAIN_IDS,
    MULTISIG_ADDRESSES,
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract, chain
from scripts.utils import confirm_posting_transaction, claim_admin_fees
from brownie import history


TARGET_NETWORK = "KAVA"


def main():
    """This script claims admin fees from all Evmos pools, then sends it operations multisig on kava"""

    # skip until we've decided on a bridge
    return
