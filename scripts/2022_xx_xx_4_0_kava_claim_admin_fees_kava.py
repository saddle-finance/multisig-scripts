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

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
    )
    ops_multisig_address = OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]

    # Run any pending transactions before simulating any more transactions
    # multisig.preview_pending()

    claim_admin_fees(multisig, CHAIN_IDS[TARGET_NETWORK])

    # combine history into multisend txn
    # TODO: set 'safe_nonce'
    safe_tx = multisig.multisend_from_receipts()
    safe_nonce = 0

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    multisig.preview(safe_tx)
    confirm_posting_transaction(multisig, safe_tx)
