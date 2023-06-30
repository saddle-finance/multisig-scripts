from ape_safe import ApeSafe
from brownie import accounts, network

from helpers import (CHAIN_IDS, MULTISIG_ADDRESSES, SDL_ADDRESSES,
                     SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS,
                     get_contract_from_deployment)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():
    """
    Send SDL to Minter contract and execute SIP-53, lowering the emission rate
    """

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"

    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    )
    sdl = multisig.get_contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    sdl_vesting_contract_proxy = multisig.get_contract(
        SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]
    )

    # Claim SDL from vesting contract
    sdl_vesting_contract_proxy.release()

    minter = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "Minter", multisig.account)

    # Transfer 10M SDL to minter
    sdl.transfer(minter.address, 10_000_000 * 1e18)

    # Apply the new rate of 20M / 24 weeks
    nextWeeklyRate = (20_000_000 * 1e18) / 24
    minter.commit_next_emission(nextWeeklyRate)

    # Sanity check for SDL balance in multisig
    sdl_balance = sdl.balanceOf(multisig.address)
    print(f"SDL balance in multisig after transfer: {sdl_balance / 1e18}")

    # Combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    # safe_tx.safe_nonce = 0 # uncomment if you want to use a specific nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
