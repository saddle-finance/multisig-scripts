from ape_safe import ApeSafe
from brownie import Contract, accounts, network

from helpers import (CHAIN_IDS, ENG_EOA_ADDRESS, INCITE_MULTISIG_ADDRESS,
                     MULTISIG_ADDRESSES, OPS_MULTISIG_ADDRESSES, SDL_ADDRESSES,
                     SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS,
                     SDL_MINTER_ADDRESS, VESTING_ABI,
                     get_contract_from_deployment)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():
    """
    Send 1.5M SDL to Minter contract.
    Reduce Minter rate to 625_000 SDL per week according to SIP-51.
    Kill old root gauge.
    Add the new fUSDC Root Gauge to the Gauge Controller contract.
    """

    print(f"You are using the '{network.show_active()}' network")
    assert network.chain.id == CHAIN_IDS[TARGET_NETWORK], f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    )
    sdl = multisig.get_contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    sdl_vesting_contract_proxy = multisig.get_contract(
        SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]
    )
    minter = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "Minter", multisig.account)
    gauge_controller = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "GaugeController", multisig.account)
    old_root_gauge = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "RootGauge_42161_CommunityfUSDCPoolLPToken", multisig.account)
    new_root_gauge = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "RootGauge_42161_CommunityfUSDCPoolLPToken_2", multisig.account)

    # Claim SDL from vesting contract
    sdl_vesting_contract_proxy.release()

    # Sanity check for SDL balance in multisig
    sdl_balance = sdl.balanceOf(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    print(f"SDL balance in multisig before transfer: {sdl_balance / 1e18}")

    # Transfer 1.5M SDL to minter
    sdl.transfer(
        SDL_MINTER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]], 1_500_000 * 1e18)

    # Sanity check for SDL balance in multisig
    sdl_balance = sdl.balanceOf(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    print(f"SDL balance in multisig after transfer: {sdl_balance / 1e18}")

    # Reduce SDL minter rate to 15,000,000 / 24 = 625000 SDL per week
    minter.commit_next_emission(625_000 * 1e18)

    # mark root gauge as killed
    old_root_gauge.set_killed(True)

    # add new root gauge to gauge controller
    gauge_controller.add_gauge(new_root_gauge, 0, 0)

    # Combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    # safe_tx.safe_nonce = 0 # uncomment if you want to use a specific nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
