from ape_safe import ApeSafe
from brownie import Contract, accounts, network

from helpers import (
    CHAIN_IDS,
    DEPLOYER_ADDRESS,
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
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url="https://safe-transaction-mainnet.safe.global",
    )
    sdl = multisig.contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    sdl_vesting_contract_proxy = multisig.contract(
        SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]
    )

    # Claim SDL from vesting contract
    sdl_vesting_contract_proxy.release()

    # Send needed SDL to Minichefs
    sidechain_minichef_debt = 1_000_000e18  # 1M SDL is owed to optimism & arbitrum

    # L2 Minichefs (optimism & arbitrum)
    sdl_balance = sdl.balanceOf(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])
    sdl.transfer(DEPLOYER_ADDRESS, sidechain_minichef_debt)
    assert sdl_balance > sdl.balanceOf(
        MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]]
    ), "SDL not sent to deployer"

    target_addresses = [
        "0xC7B2F1a2D0838370f88a2FD5c2E3F64D8aF89a18",  # Art
        "0xd17c31796d3Cb41d9d211904780320C4be286172",  # Sandra
    ]
    for vesting_address in target_addresses:
        vesting_contract = Contract.from_abi(
            "Vesting",
            vesting_address,
            VESTING_ABI,
            multisig.account,
        )
        vesting_contract.release()
        vesting_contract.changeBeneficiary(INCITE_MULTISIG_ADDRESS)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 74

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
