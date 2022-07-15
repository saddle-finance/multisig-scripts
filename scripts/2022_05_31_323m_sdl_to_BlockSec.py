from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, SDL_ADDRESSES
from ape_safe import ApeSafe
from brownie import accounts, network

from scripts.utils import confirm_posting_transaction


def main():
    """Send SDL to BlockSec"""

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])
    sdl_contract = multisig.contract(SDL_ADDRESSES[CHAIN_IDS["MAINNET"]])
    # blocksec address, 1_323_340 SDL
    sdl_contract.transfer(
        "0x04B3f2Ac72AAD1Cdb12A4Cb516E2183F1D455442", 1_323_340 * 1e18
    )

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
