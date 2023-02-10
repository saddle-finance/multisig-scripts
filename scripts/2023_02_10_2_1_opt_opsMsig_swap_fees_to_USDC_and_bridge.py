from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    OPTIMISM_STANDARD_BRIDGE,
    MULTISIG_ADDRESSES,
    OPS_MULTISIG_ADDRESSES,
    OPTIMISM_L2_STANDARD_BRIDGE_ABI
)
from fee_distro_helpers import (
    token_addresses
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract, chain
from scripts.utils import confirm_posting_transaction, convert_fees_to_USDC_saddle, bridge_usdc_to_mainnet
from brownie import history


TARGET_NETWORK = "OPTIMISM"


def main():
    """This script swaps admin fees to USDC and sends them to Mainnet main multisig"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"

    ops_multisig = ApeSafe(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
    )

    # convert fees to USDC
    convert_fees_to_USDC_saddle(ops_multisig, CHAIN_IDS[TARGET_NETWORK])

    # bridge USDC to mainnet Saddle multisig
    bridge_usdc_to_mainnet(ops_multisig, CHAIN_IDS[TARGET_NETWORK])

    # combine history into multisend txn
    # TODO: set 'safe_nonce'
    safe_tx = ops_multisig.multisend_from_receipts()
    safe_nonce = 7

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    # ops_multisig.preview(safe_tx)
    for tx in history:
        tx.info()
    confirm_posting_transaction(ops_multisig, safe_tx)
