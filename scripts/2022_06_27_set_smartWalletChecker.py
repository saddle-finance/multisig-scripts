from helpers import (
    CHAIN_IDS,
    MULTISIG_ADDRESSES,
    SMART_WALLET_CHECKER_ADDRESSES,
    VOTING_ESCROW_ADDRESSES,
)
from ape_safe import ApeSafe
from brownie import accounts, network

from scripts.utils import confirm_posting_transaction


def main():
    """Sets VotingEscrow.checker to the address of the SmartWalletChecker contract"""

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])
    vesdl = multisig.contract(VOTING_ESCROW_ADDRESSES[CHAIN_IDS["MAINNET"]])
    smart_wallet_checker = multisig.contract(SMART_WALLET_CHECKER_ADDRESSES[CHAIN_IDS["MAINNET"]])

    vesdl.commit_smart_wallet_checker(smart_wallet_checker.address)
    vesdl.apply_smart_wallet_checker()

    safe_tx = multisig.multisend_from_receipts()

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
