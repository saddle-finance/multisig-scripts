from math import ceil
from multiprocessing import pool

from ape_safe import ApeSafe
from brownie import accounts, network

from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, SDL_ADDRESSES, SDL_MINTER_ADDRESS
from scripts.utils import confirm_posting_transaction


def main():
    """Add SimpleRewarder for T to minichef"""

    print(f"You are using the '{network.show_active()}' network")

    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])
    sdl_contract = multisig.contract(SDL_ADDRESSES[CHAIN_IDS["MAINNET"]])

    # Send 3.5M SDL to SDL minter
    minter = multisig.contract(SDL_MINTER_ADDRESS[CHAIN_IDS["MAINNET"]])
    sdl_contract.transfer(minter.address, 3500000 * 1e18)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 79
    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)
    confirm_posting_transaction(multisig, safe_tx)
