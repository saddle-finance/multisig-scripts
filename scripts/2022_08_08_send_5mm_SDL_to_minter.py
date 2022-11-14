from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, SDL_ADDRESSES, SDL_MINTER_ADDRESS
from ape_safe import ApeSafe
from brownie import accounts, network
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "MAINNET"


def main():
    """This script refills the Minter contract with 5mm SDL"""

    print(f"You are using the '{network.show_active()}' network")
    assert(network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    # Run any pending transactions before simulating any more transactions
    multisig.preview_pending()

    sdl = multisig.contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    # The amount to send to minter
    amount_to_send = 5_000_000 * 1e18

    # Target address
    minter_address = SDL_MINTER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]

    # Send sdl to minter
    sdl.transfer(minter_address, amount_to_send)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_nonce = 54

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    multisig.preview(safe_tx)
    confirm_posting_transaction(multisig, safe_tx)
