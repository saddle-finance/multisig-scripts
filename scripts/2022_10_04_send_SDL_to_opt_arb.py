import math

from ape_safe import ApeSafe
from brownie import accounts, network
from helpers import (
    CHAIN_IDS,
    MINICHEF_ADDRESSES,
    MULTISIG_ADDRESSES,
    OPTIMISM_STANDARD_BRIDGE,
    SDL_ADDRESSES,
)

from scripts.utils import bridge_to_arbitrum, bridge_to_optimism

TARGET_NETWORK = "MAINNET"


def main():
    """Sends 500k of SDL to Arbitrum & Optimism minichef"""

    print(f"You are using the '{network.show_active()}' network")

    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    deployer = accounts.load("deployer")  # prompts for password

    sdl = multisig.contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    # 500k SDL
    # amount_to_send = 500_000 * 1e18
    amount_to_send = 1 * 1e18

    starting_balance = sdl.balanceOf(deployer.address)
    assert starting_balance >= amount_to_send

    # Send to Arbitrum minichef
    bridge_to_arbitrum(
        multisig,
        sdl.address,
        amount_to_send,
    )

    assert (
        sdl.balanceOf(deployer.address) == starting_balance - amount_to_send
    ), "SDL was not sent to arbitrum"

    # starting_balance = sdl.balanceOf(deployer.address)
    # assert starting_balance >= amount_to_send

    # # Send to Optimism minichef
    # bridge_to_optimism(
    #     multisig,
    #     sdl.address,
    #     amount_to_send,
    # )

    # assert (
    #     sdl.balanceOf(deployer.address) == starting_balance - amount_to_send
    # ), "SDL was not sent to optimsim"
