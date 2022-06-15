from helpers import (
    CHAIN_IDS,
    MULTISIG_ADDRESSES,
    SDL_ADDRESSES,
    SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS,
    JUMP_RECEIVER_ADDRESS,
)
from ape_safe import ApeSafe
from brownie import accounts, network

from scripts.utils import confirm_posting_transaction


def main():
    """Send 19,999,999 $SDL to Jump"""

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    jump_receiver = JUMP_RECEIVER_ADDRESS[CHAIN_IDS["MAINNET"]]
    sdl_contract = multisig.contract(SDL_ADDRESSES[CHAIN_IDS["MAINNET"]])
    sdl_vesting_contract_proxy = multisig.contract(
        SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS[CHAIN_IDS["MAINNET"]]
    )
    sdl_transfer_amount = 19_999_999 * 1e18
    sdl_contract.addToAllowedList([jump_receiver])

    # release vested tokens to deployer account
    sdl_vesting_contract_proxy.release()

    # transfer sdl to jump
    sdl_contract.transfer(jump_receiver, sdl_transfer_amount)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 37

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
