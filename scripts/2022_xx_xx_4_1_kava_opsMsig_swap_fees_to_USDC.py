from scripts.utils import confirm_posting_transaction
from brownie import accounts, network, Contract, chain
from ape_safe import ApeSafe
from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    META_SWAP_DEPOSIT_ABI,
    MULTISIG_ADDRESSES,
    OPS_MULTISIG_ADDRESSES,
    SWAP_ABI,
    META_SWAP_ABI,
)
from brownie import history


TARGET_NETWORK = "KAVA"


def main():
    """This script claims admin fees from all Kava pools, then converts them to xxxx and sends them to Mainnet"""

    # skip until we've decided on a bridge
    return
