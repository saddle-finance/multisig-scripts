from ape_safe import ApeSafe
from brownie import Contract, accounts, chain, history, network

from helpers import (CHAIN_IDS, ENG_EOA_ADDRESS, ERC20_ABI,
                     INCITE_MULTISIG_ADDRESS, META_SWAP_ABI,
                     META_SWAP_DEPOSIT_ABI, MULTISIG_ADDRESSES,
                     OPS_MULTISIG_ADDRESSES, SDL_ADDRESSES,
                     SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS,
                     SDL_MINTER_ADDRESS, SWAP_ABI, VESTING_ABI)
from scripts.utils import claim_admin_fees, confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():
    """
    This script 
    - claims admin fees from all Mainnet pools and sends them to Operations Multisig
    - refills minter
    """

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
    )

    # Claim admin fees from all pools and send them to ops multisig
    claim_admin_fees(multisig, CHAIN_IDS[TARGET_NETWORK])

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    # multisig.preview(safe_tx)
    for tx in history:
        tx.info()
    confirm_posting_transaction(multisig, safe_tx)
