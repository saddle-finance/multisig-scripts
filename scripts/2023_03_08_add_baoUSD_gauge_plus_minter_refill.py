
from ape_safe import ApeSafe
from brownie import Contract, accounts, network, history

from helpers import (CHAIN_IDS, ENG_EOA_ADDRESS, INCITE_MULTISIG_ADDRESS,
                     MULTISIG_ADDRESSES, SDL_ADDRESSES,
                     SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS,
                     SDL_MINTER_ADDRESS, VESTING_ABI, get_contract_from_deployment,
                     get_deployment_details)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():
    """
    1. Add baoUSD LiqV5 gauge to gauge controller
    2. Send 1.5mm SDL to Minter contract proactively
    """

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
    )

    gauge_controller = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "GaugeController", multisig.account    
    )
    
    # add baoUSD gauge to gauge controller
    gauges = [
        "LiquidityGaugeV5_SaddleFraxBPBaoUSDMetaPoolLPToken"
    ]

    for name in gauges:
        address, abi = get_deployment_details(CHAIN_IDS["MAINNET"], name)
        gauge_controller.add_gauge(address, 0, 0)

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

    # Transfer 1.5mm SDL to minter
    sdl.transfer(
        SDL_MINTER_ADDRESS[CHAIN_IDS["MAINNET"]], 1_500_000 * 1e18)

    # Sanity check for SDL balance in multisig
    sdl_balance = sdl.balanceOf(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])
    print(f"SDL balance in multisig after transfer: {sdl_balance / 1e18}")
    # Combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 87

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    #multisig.preview(safe_tx)

    for tx in history:
        tx.info()
    confirm_posting_transaction(multisig, safe_tx)
