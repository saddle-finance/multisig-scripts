import math
from helpers import (
    CHAIN_IDS,
    MINICHEF_ADDRESSES,
    MULTISIG_ADDRESSES,
    SDL_ADDRESSES,
    OPTIMISM_STANDARD_BRIDGE,
    SDL_MINTER_ADDRESS
)
from ape_safe import ApeSafe
from brownie import accounts, network

from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():
    """Sends 500k SDL to Optimism minichef and 5kk SDL to minter """

    print(f"You are using the '{network.show_active()}' network")
    assert network.chain.id == CHAIN_IDS[TARGET_NETWORK], f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    sdl = multisig.contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    optimism_L1_standard_bridge = multisig.contract(
        OPTIMISM_STANDARD_BRIDGE[CHAIN_IDS[TARGET_NETWORK]]
    )

    ##### Send 500k SDL to Optimism Minichef #####

    # 500k SDL ~= 16 days worth of emissions at 59.3k per day for side chains
    # and 53% of that for Optimism
    amount_to_send = 500_000 * 1e18
    starting_balance = sdl.balanceOf(multisig.address)
    assert (starting_balance >= amount_to_send)

    # approve bridge
    sdl.approve(
        optimism_L1_standard_bridge.address,
        amount_to_send
    )

    # gas limit required to complete the deposit on L2
    l2gas = "0x1e8480"  # 2,000,000

    # Optimism bridge code https://etherscan.io/address/0x40e0c049f4671846e9cff93aaed88f2b48e527bb#code
    # send to Optimism minichef
    optimism_L1_standard_bridge.depositERC20To(
        SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],   # _l1token
        SDL_ADDRESSES[CHAIN_IDS["OPTIMISM"]],       # _l2token
        MINICHEF_ADDRESSES[CHAIN_IDS["OPTIMISM"]],  # _to
        amount_to_send,                             # _amount
        l2gas,                                      # _l2gas
        "0x",                                       # _data
    )
    assert (sdl.balanceOf(multisig.address) ==
            starting_balance - amount_to_send), "SDL was not sent"

    ##### Send 5kk SDL to Minter #####

    # Target address
    minter_address = SDL_MINTER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]

    # The amount to send to minter
    amount_to_send = 5_000_000 * 1e18
    starting_balance = sdl.balanceOf(multisig.address)
    assert (starting_balance >= amount_to_send)

    # Send sdl to minter
    sdl.transfer(minter_address, amount_to_send)

    assert (sdl.balanceOf(multisig.address) ==
            starting_balance - amount_to_send), "SDL was not sent"

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 59

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
