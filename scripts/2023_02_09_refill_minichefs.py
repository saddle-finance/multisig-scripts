from ape_safe import ApeSafe
from brownie import Contract, accounts, network

from helpers import (
    CHAIN_IDS,
    ENG_EOA_ADDRESS,
    INCITE_MULTISIG_ADDRESS,
    MULTISIG_ADDRESSES,
    SDL_ADDRESSES,
    SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS,
    VESTING_ABI,
)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():
    """
    Send SDL to fund minichef rewards from results of snapshot vote
    Vote: https://snapshot.org/#/saddlefinance.eth/proposal/0x508226028d3a401df05f84aa4f6292f5dde8db55d5aa10804f73794a02dbf5f0
    """

    print(f"You are using the '{network.show_active()}' network")
    assert network.chain.id == CHAIN_IDS[TARGET_NETWORK], f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    sdl = multisig.get_contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    sdl_vesting_contract_proxy = multisig.get_contract(
        SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]
    )

    # Claim SDL from vesting contract
    sdl_vesting_contract_proxy.release()

    # Send needed SDL to EOA for bridging to minichefs
    arbitrum_minichef_debt = 50077104116351310467768  # SDL owed to arbitrum
    optimism_minichef_debt = 75042837369470445854120  # SDL owed to optimism
    sidechain_minichef_debt = (
        arbitrum_minichef_debt + optimism_minichef_debt
    )  # SDL owed to optimism & arbitrum

    # L2 Minichefs (optimism & arbitrum)
    sdl_balance = sdl.balanceOf(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])
    sdl.transfer(ENG_EOA_ADDRESS, sidechain_minichef_debt)
    assert sdl_balance > sdl.balanceOf(
        MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]]
    ), "SDL not sent to EOA"

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 84

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
