from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, GAUGE_CONTROLLER_ADDRESS
from ape_safe import ApeSafe
from brownie import accounts, network
from scripts.utils import confirm_posting_transaction


def main():
    """This script enables on-chain voting on the gauge controller"""

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    # Run any pending transactions before simulating any more transactions
    multisig.preview_pending()

    gauge_controller = multisig.contract(
        GAUGE_CONTROLLER_ADDRESS[CHAIN_IDS["MAINNET"]])

    # enable voting on the gauge controller
    gauge_controller.set_voting_enabled(True)

    # combine history into multisend txn
    # TODO: set 'safe_nonce'
    safe_tx = multisig.multisend_from_receipts()
    safe_nonce = 0

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)
    confirm_posting_transaction(multisig, safe_tx)
