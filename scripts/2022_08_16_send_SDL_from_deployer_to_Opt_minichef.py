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

    # ~184.7k SDL (-1000 that was used for the test transaction)
    amount_to_send = 184672878613986966513520 - 1000
    # amount_to_send = 1000  # testing
    assert (sdl.balanceOf(deployer.address) >= amount_to_send)

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

    # combine history into multisend txn
    # safe_tx = multisig.multisend_from_receipts()
    # safe_tx.safe_nonce = 0

    # sign with private key
    # safe_tx.sign(deployer.private_key)
    # multisig.preview(safe_tx)

    # confirm_posting_transaction(multisig, safe_tx)

    # combine history into multisend txn
    # safe_tx = multisig.multisend_from_receipts()
    # safe_tx.safe_nonce = 46

    # sign with private key
    # safe_tx.sign(deployer.private_key)
    # multisig.preview(safe_tx)

    # confirm_posting_transaction(multisig, safe_tx)
