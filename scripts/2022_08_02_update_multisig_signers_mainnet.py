from helpers import (
    CHAIN_IDS,
    MULTISIG_ADDRESSES,
    OWNERS,
    SDL_ADDRESSES,
    SDL_MINTER_ADDRESS,
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract

from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():
    """Update a vesting contract's ownership to company multisig"""

    print(f"You are using the '{network.show_active()}' network")

    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    safe_contract = multisig.contract(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    Kain_Warwick = "0x5b97680e165b4dbf5c45f4ff4241e85f418c66c2"

    # prev owner(pointer), old owner, new owner
    safe_contract.swapOwner(OWNERS[4], Kain_Warwick, OWNERS[5])

    # new owner, threshold
    safe_contract.addOwnerWithThreshold(OWNERS[0], 3)
    assert safe_contract.getOwners() == OWNERS

    # The amount to send to minter
    amount_to_send = 5_000_000 * 1e18

    # Target address
    minter_address = SDL_MINTER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]

    # Send sdl to minter
    sdl = multisig.contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    sdl.transfer(minter_address, amount_to_send)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 54

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
