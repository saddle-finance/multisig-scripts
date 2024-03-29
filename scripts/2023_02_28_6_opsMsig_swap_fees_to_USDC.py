from helpers import (
    CHAIN_IDS,
    OPS_MULTISIG_ADDRESSES,
)
from ape_safe import ApeSafe
from brownie import accounts, network
from scripts.utils import (
    confirm_posting_transaction,
    convert_fees_to_USDC_saddle,
    convert_fees_to_USDC_curve,
    convert_fees_to_USDC_uniswap
)
from brownie import history


TARGET_NETWORK = "MAINNET"


def main():
    """This script swaps all fee tokens to USDC, from Ops-Multisig"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    ops_multisig = ApeSafe(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    )

    convert_fees_to_USDC_saddle(
        ops_multisig,
        CHAIN_IDS[TARGET_NETWORK]
    )

    convert_fees_to_USDC_curve(
        ops_multisig,
        CHAIN_IDS[TARGET_NETWORK]
    )

    # convert_fees_to_USDC_uniswap(
    #    ops_multisig,
    #    CHAIN_IDS[TARGET_NETWORK]
    # )

    # combine history into multisend txn
    # TODO: set 'safe_nonce'
    safe_tx = ops_multisig.multisend_from_receipts()
    safe_nonce = 1

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    # ops_multisig.preview(safe_tx)
    for tx in history:
        tx.info()
    confirm_posting_transaction(ops_multisig, safe_tx)
