from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    ARB_GATEWAY_ROUTER,
    MULTISIG_ADDRESSES,
    OPS_MULTISIG_ADDRESSES,
)
from fee_distro_helpers import (
    token_addresses
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract, chain
from scripts.utils import confirm_posting_transaction, convert_fees_to_USDC_saddle


TARGET_NETWORK = "ARBITRUM"


def main():
    """This script swaps fee tokens to USDC and bridges USDC to main multisig on Mainnet"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    ops_multisig = ApeSafe(OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    # Run any pending transactions before simulating any more transactions
    # ops_multisig.preview_pending()

    # Arbitrum L2 gateway router
    gateway_router = ops_multisig.contract(
        ARB_GATEWAY_ROUTER[CHAIN_IDS[TARGET_NETWORK]]
    )

    convert_fees_to_USDC_saddle(ops_multisig, CHAIN_IDS[TARGET_NETWORK])

    # bridging USDC to mainnet
    USDC = Contract.from_abi(
        "ERC20", token_addresses[CHAIN_IDS[TARGET_NETWORK]]["USDC"], ERC20_ABI
    )

    # bridge 100% of ops-msig USDC balance to mainnet main multisig
    amount_to_bridge = USDC.balanceOf(
        ops_multisig.address
    )

    print(
        f"Bridging ${USDC.symbol()} {amount_to_bridge / (10 ** USDC.decimals())} to mainnet main msig"
    )

    # find gateway for USDC
    token_gateway_address = gateway_router.getGateway(
        USDC.address
    )

    # approve gateway
    USDC.approve(
        token_gateway_address,
        amount_to_bridge,
        {"from": ops_multisig.address}
    )

    # bridge USDC to mainnet main msig
    gateway_router.outboundTransfer(
        token_addresses[CHAIN_IDS["MAINNET"]]["USDC"],
        MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]],  # mainnet main multisig
        amount_to_bridge,
        "0x",  # TODO: clarify what format this needs to have
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
