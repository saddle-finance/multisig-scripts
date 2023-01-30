from ape_safe import ApeSafe
from brownie import Contract, accounts, network

from helpers import (CHAIN_IDS, ENG_EOA_ADDRESS, INCITE_MULTISIG_ADDRESS,
                     MULTISIG_ADDRESSES, SDL_ADDRESSES,
                     SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS,
                     SDL_MINTER_ADDRESS, VESTING_ABI)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():
    """
    Send SDL to fund minichef and minter
    """

    print(f"You are using the '{network.show_active()}' network")
    assert network.chain.id == CHAIN_IDS[TARGET_NETWORK], f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url="https://safe-transaction-mainnet.safe.global",
    )
    sdl = multisig.get_contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    sdl_vesting_contract_proxy = multisig.get_contract(
        SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]
    )

    # Claim SDL from vesting contract
    sdl_vesting_contract_proxy.release()

    # SDL debt amounts calculated via scripts in
    # https://github.com/saddle-finance/saddle-contract/blob/0bdd8be8449fbfe34bc24e21e249a839c2d01174/scripts/calculateMinterOwed.ts
    arbitrum_minichef_debt = 570866340025321219331576
    optimism_minichef_debt = 614156156080167985041548
    minter_debt = 4308778851190476172480738

    # Sanity check for SDL balance in multisig
    sdl_balance = sdl.balanceOf(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])
    print(f"SDL balance in multisig before transfer: {sdl_balance}")

    # Transfer L2 debts to EOA for manual bridging
    sdl.transfer(ENG_EOA_ADDRESS, arbitrum_minichef_debt +
                 optimism_minichef_debt)

    # Transfer minter debts
    sdl.transfer(SDL_MINTER_ADDRESS[CHAIN_IDS["MAINNET"]], minter_debt)

    # Sanity check for SDL balance in multisig
    sdl_balance = sdl.balanceOf(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])
    print(f"SDL balance in multisig after transfer: {sdl_balance}")

    # Combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 82

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
