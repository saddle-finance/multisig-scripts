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

    # Send other tokens to ops multisig
    tokens_to_transfer = [
        "0xdBdb4d16EdA451D0503b854CF79D55697F90c8DF",  # ALCX
        "0xCe391315b414D4c7555956120461D21808A69F3A",  # Bao
        "0x5fAa989Af96Af85384b8a938c2EdE4A7378D9875",  # GAL
        "0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F",  # SNX
    ]

    safe_tx = multisig.multisend_from_receipts()

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    # multisig.preview(safe_tx)
    for tx in history:
        tx.info()
    confirm_posting_transaction(multisig, safe_tx)
