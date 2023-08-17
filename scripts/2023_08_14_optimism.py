from ape_safe import ApeSafe
from brownie import Contract, accounts, chain, history, network

from helpers import (CHAIN_IDS, ERC20_ABI, MULTISIG_ADDRESSES,
                     OPS_MULTISIG_ADDRESSES)
from scripts.utils import (claim_admin_fees, confirm_posting_transaction,
                           pause_all_pools)

TARGET_NETWORK = "OPTIMISM"


def main():
    """This script claims admin fees from all Optimism pools, then sends them to Operations Multisig on Optimism"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url='https://safe-transaction-optimism.safe.global'
    )

    # Run any pending transactions before simulating any more transactions
    # multisig.preview_pending()

    # Pause all pools
    pause_all_pools(multisig, CHAIN_IDS[TARGET_NETWORK])

    claim_admin_fees(multisig, CHAIN_IDS[TARGET_NETWORK])

    safe_tx = multisig.multisend_from_receipts()

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    # multisig.preview(safe_tx)
    for tx in history:
        tx.info()
    confirm_posting_transaction(multisig, safe_tx)
