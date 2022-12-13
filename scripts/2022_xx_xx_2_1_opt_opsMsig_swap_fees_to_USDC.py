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
from scripts.utils import confirm_posting_transaction, convert_fees_to_USDC_saddle


TARGET_NETWORK = "OPTIMISM"


def main():
    """This script swaps admin fees to USDC and sends them to Mainnet main multisig"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    ops_multisig = ApeSafe(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url='https://safe-transaction.optimism.gnosis.io/'
    )

    convert_fees_to_USDC_saddle(ops_multisig, CHAIN_IDS[TARGET_NETWORK])

    # Run any pending transactions before simulating any more transactions
    # ops_multisig.preview_pending()

    # Optimism L2 Standard Bridge
    standard_bridge = Contract.from_abi(
        "L2StandardBridge",
        OPTIMISM_STANDARD_BRIDGE[CHAIN_IDS[TARGET_NETWORK]],
        OPTIMISM_L2_STANDARD_BRIDGE_ABI
    )

    # bridge 100% of USDC balance to mainnet main multisig
    USDC = Contract.from_abi(
        "ERC20", token_addresses[CHAIN_IDS[TARGET_NETWORK]]["USDC"], ERC20_ABI)
    amount_to_bridge = USDC.balanceOf(
        ops_multisig.address
    )

    print(
        f"Approving bridge for ${USDC.symbol()} {amount_to_bridge / (10 ** USDC.decimals())}"
    )
    # approve gateway
    USDC.approve(
        standard_bridge,
        amount_to_bridge,
        {"from": ops_multisig.address}
    )

    # send tx to bridge
    print(
        f"Bridging ${USDC.symbol()} {amount_to_bridge / (10 ** USDC.decimals())} to mainnet"
    )
    standard_bridge.withdrawTo(
        token_addresses[CHAIN_IDS[TARGET_NETWORK]]["USDC"],  # _l2token
        MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]],           # _to
        amount_to_bridge,                                   # _amount
        0,                                                  # _l1Gas
        "",                                                 # _data
        {"from": ops_multisig.address}
    )

    assert USDC.balanceOf(ops_multisig.address) == 0

    # combine history into multisend txn
    # TODO: set 'safe_nonce'
    safe_tx = ops_multisig.multisend_from_receipts()
    safe_nonce = 0

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    ops_multisig.preview(safe_tx)
    confirm_posting_transaction(ops_multisig, safe_tx)
