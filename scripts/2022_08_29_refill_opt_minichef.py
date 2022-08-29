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
    assert network.chain.id == CHAIN_IDS[TARGET_NETWORK], f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    sdl = multisig.contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    optimism_L1_standard_bridge = multisig.contract(
        OPTIMISM_STANDARD_BRIDGE[CHAIN_IDS[TARGET_NETWORK]]
    )

    # 500k SDL ~= 16 days worth of emissions at 59.3k per day for side chains
    # and 53% of that for Optimism
    amount_to_send = 500_000 * 1e18
    assert (sdl.balanceOf(multisig.address) >= amount_to_send)

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

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 59

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
