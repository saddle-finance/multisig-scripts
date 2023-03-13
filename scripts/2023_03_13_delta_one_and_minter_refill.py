from ape_safe import ApeSafe
from brownie import accounts, network

from helpers import (CHAIN_IDS, MULTISIG_ADDRESSES, SDL_ADDRESSES,
                     SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS,
                     SDL_MINTER_ADDRESS)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"

DELTA_ONE_DEPLOYER = "0x3CF1287B3E23Ce21742F6118ABCFF6709724409f"


def main():
    """
    Send 750k SDL to Delta One Deployer account
    Send SDL to Minter contract proactively
    """

    print(f"You are using the '{network.show_active()}' network")
    assert network.chain.id == CHAIN_IDS[TARGET_NETWORK], f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
    )
    sdl = multisig.get_contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    sdl_vesting_contract_proxy = multisig.get_contract(
        SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]
    )

    # Claim SDL from vesting contract
    sdl_vesting_contract_proxy.release()

    # Sanity check for SDL balance in multisig
    sdl_balance = sdl.balanceOf(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])
    print(f"SDL balance in multisig before transfer: {sdl_balance / 1e18}")

    # Transfer 1.5M SDL, weekly amount to Minter
    sdl.transfer(SDL_MINTER_ADDRESS[CHAIN_IDS["MAINNET"]], 1_500_000)
    # Transfer 750k SDL to Delta One Deployer
    sdl.transfer(DELTA_ONE_DEPLOYER, 750_000)

    # Sanity check for SDL balance in multisig
    sdl_balance = sdl.balanceOf(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])
    print(f"SDL balance in multisig after transfer: {sdl_balance / 1e18}")

    # Combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
