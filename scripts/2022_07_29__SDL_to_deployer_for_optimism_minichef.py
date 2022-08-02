import math
from helpers import CHAIN_IDS, MINICHEF_ADDRESSES, MULTISIG_ADDRESSES, SDL_ADDRESSES, SIDECHAIN_TOTAL_EMISSION_RATE
from ape_safe import ApeSafe
from brownie import ZERO_ADDRESS, Contract, accounts, network

from scripts.utils import confirm_posting_transaction


def main():
    """
    Sends SDL to deployer account. This will be bridged to Optimism minichef
    """
    TARGET_NETWORK = "MAINNET"

    print(f"You are using the '{network.show_active()}' network")
    assert(network.chain.id ==
           CHAIN_IDS[TARGET_NETWORK]), f"Not on {TARGET_NETWORK} network"
    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    sdl = multisig.contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    seconds_in_week = 60 * 60 * 24 * 7
    amount_to_send = math.floor(
        SIDECHAIN_TOTAL_EMISSION_RATE * seconds_in_week * 4998 / 10000)

    sdl.transfer(deployer.address, amount_to_send)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 52

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
