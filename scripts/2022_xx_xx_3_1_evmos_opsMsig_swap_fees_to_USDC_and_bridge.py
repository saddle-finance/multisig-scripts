import this
from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    MULTISIG_ADDRESSES,
    OPS_MULTISIG_ADDRESSES,
    EVMOS_CELER_LIQUIDITY_BRIDGE,
    EVMOS_CELER_LIQUIDITY_BRIDGE_ABI,
)
from fee_distro_helpers import (
    token_addresses
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract, chain
from scripts.utils import confirm_posting_transaction, convert_fees_to_USDC_saddle, bridge_usdc_to_mainnet
from brownie import history


TARGET_NETWORK = "EVMOS"


def main():
    """This script claims admin fees from all Evmos pools, then converts them to ceUSDC and sends them to Mainnet"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    ops_multisig = ApeSafe(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url='https://safe.evmos.org/'
    )

    # Run any pending transactions before simulating any more transactions
    # ops_multisig.preview_pending()

    convert_fees_to_USDC_saddle(ops_multisig, CHAIN_IDS[TARGET_NETWORK])

    # bridge USDC to mainnet Saddle multisig
    bridge_usdc_to_mainnet(ops_multisig, CHAIN_IDS[TARGET_NETWORK])

    # combine history into multisend txn
    # TODO: set 'safe_nonce'
    safe_tx = ops_multisig.multisend_from_receipts()
    safe_nonce = 0

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    # ops_multisig.preview(safe_tx)
    for tx in history:
        tx.info()
    confirm_posting_transaction(ops_multisig, safe_tx)
