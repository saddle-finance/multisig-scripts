from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    META_SWAP_DEPOSIT_ABI,
    MULTISIG_ADDRESSES,
    OPS_MULTISIG_ADDRESSES,
    SWAP_ABI,
    META_SWAP_ABI,
    ENG_EOA_ADDRESS, 
    INCITE_MULTISIG_ADDRESS,                 
    MULTISIG_ADDRESSES, SDL_ADDRESSES,
    SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS,
    SDL_MINTER_ADDRESS, VESTING_ABI
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract, chain
from scripts.utils import confirm_posting_transaction, claim_admin_fees
from brownie import history


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

    ### Claim admin fees from all pools and send them to ops multisig
    claim_admin_fees(multisig, CHAIN_IDS[TARGET_NETWORK])


    ### Refill minter with SDL
    sdl = multisig.get_contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    sdl_vesting_contract_proxy = multisig.get_contract(
        SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]
    )

    # Claim SDL from vesting contract
    sdl_vesting_contract_proxy.release()

    # Sanity check for SDL balance in multisig
    sdl_balance = sdl.balanceOf(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])
    print(f"SDL balance in multisig before transfer: {sdl_balance / 1e18}")

    # Transfer SDL such that multisig has extra room with 500k SDL
    sdl.transfer(
        SDL_MINTER_ADDRESS[CHAIN_IDS["MAINNET"]], 1_500_000 * 1e18)

    # Sanity check for SDL balance in multisig
    sdl_balance = sdl.balanceOf(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])
    print(f"SDL balance in multisig after transfer: {sdl_balance / 1e18}")

    # combine history into multisend txn
    # TODO: set 'safe_nonce'
    safe_tx = multisig.multisend_from_receipts()
    safe_nonce = 86

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    # multisig.preview(safe_tx)
    for tx in history:
        tx.info()
    confirm_posting_transaction(multisig, safe_tx)
