import math
from helpers import (
    CHAIN_IDS,
    MINICHEF_ADDRESSES,
    MULTISIG_ADDRESSES,
    SDL_ADDRESSES,
    OPTIMISM_STANDARD_BRIDGE
)
from ape_safe import ApeSafe
from brownie import accounts, network

from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():
    """Sends one week worth of emissions of SDL to Optimism minichef """

    print(f"You are using the '{network.show_active()}' network")

    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    deployer = accounts.load("deployer")  # prompts for password

    sdl = multisig.contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    optimism_L1_standard_bridge = multisig.contract(
        OPTIMISM_STANDARD_BRIDGE[CHAIN_IDS[TARGET_NETWORK]]
    )

    # 500k SDL
    amount_to_send = 500_000 * 1e18

    starting_balance = sdl.balanceOf(deployer.address)
    assert (starting_balance >= amount_to_send)

    # approve bridge
    sdl.approve(
        optimism_L1_standard_bridge.address,
        amount_to_send,
        {"from": deployer}
    )

    # gas limit required to complete the deposit on L2
    l2gas = "0x1e8480"  # 2,000,000

    # Optimism bride code https://etherscan.io/address/0x40e0c049f4671846e9cff93aaed88f2b48e527bb#code
    # send to Optimism minichef
    optimism_L1_standard_bridge.depositERC20To(
        SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],   # _l1token
        SDL_ADDRESSES[CHAIN_IDS["OPTIMISM"]],       # _l2token
        MINICHEF_ADDRESSES[CHAIN_IDS["OPTIMISM"]],  # _to
        amount_to_send,                             # _amount
        l2gas,                                      # _l2gas
        "0x",                                       # _data
        {"from": deployer}
    )

    assert (sdl.balanceOf(deployer.address) ==
            starting_balance - amount_to_send), "SDL was not sent"
