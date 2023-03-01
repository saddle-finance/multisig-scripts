from helpers import (
    CHAIN_IDS,
    OPS_MULTISIG_ADDRESSES,
)
from ape_safe import ApeSafe
from brownie import accounts, network
from scripts.utils import confirm_posting_transaction, buy_weth_with_usdc_sushi, swap_curve
from brownie import history


TARGET_NETWORK = "MAINNET"


def main():
    """This script buys WETH with half of the Ops-multisig's USDC balance"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"

    ops_multisig = ApeSafe(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    )

    # swap remaining USDT from last step to USDC using curve
    CURVE_3POOL_MAINNET = "0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7"
    swap_curve(
        ops_multisig, 
        CHAIN_IDS[TARGET_NETWORK],
        CURVE_3POOL_MAINNET, 
        False,
        2,
        1,
        468291048
    )

    # buy WETH with half of the Ops-multisig's USDC balance
    buy_weth_with_usdc_sushi(
        ops_multisig, 
        CHAIN_IDS[TARGET_NETWORK],
        price_impact_factor = 1.45
    )

    # TODO: set 'safe_nonce'
    safe_tx = ops_multisig.multisend_from_receipts()
    safe_nonce = 2

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    # ops_multisig.preview(safe_tx)
    for tx in history:
        tx.info()
    confirm_posting_transaction(ops_multisig, safe_tx)
