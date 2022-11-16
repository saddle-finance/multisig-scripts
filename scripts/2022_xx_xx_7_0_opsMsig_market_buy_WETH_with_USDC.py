from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    OPS_MULTISIG_ADDRESSES,
    UNIV3_ROUTER_ABI,
    UNIV3_QUOTER_ABI
)
from fee_distro_helpers import (
    token_addresses_mainnet,
    UNIV3_ROUTER,
    UNIV3_QUOTER
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract, chain
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "MAINNET"


def main():
    """This script buys WETH with half of the Ops-multisig's USDC balance"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    ops_multisig = ApeSafe(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    )

    # Run any pending transactions before simulating any more transactions
    # ops_multisig.preview_pending()

    univ3_router = Contract.from_abi(
        "UniV3Router", UNIV3_ROUTER, UNIV3_ROUTER_ABI
    )
    univ3_quoter = Contract.from_abi(
        "UniV3Quoter", UNIV3_QUOTER, UNIV3_QUOTER_ABI
    )

    USDC_contract = Contract.from_abi(
        "ERC20", token_addresses_mainnet["USDC"], ERC20_ABI
    )
    WETH_contract = Contract.from_abi(
        "ERC20", token_addresses_mainnet["WETH"], ERC20_ABI
    )
    USDC_decimals = USDC_contract.decimals()
    WETH_decimals = WETH_contract.decimals()

    USDC_balance_before = USDC_contract.balanceOf(ops_multisig.address)

    token_from_address = token_addresses_mainnet["USDC"]
    token_to_address = token_addresses_mainnet["WETH"]
    fee = 500
    recipient = ops_multisig.address
    deadline = chain[chain.height].timestamp + 3600  # 1 hour
    sqrt_price_limit_X96 = 0

    # Swap ~50% of ops_multisig's USDC for WETH.
    # factor to correct for price increases of SDL through tranch buys,
    # requiring less and less SDL to provide liq in optimal ratio.

    # TODO: adjust factor before executing, s.t. minimal SDL or WETH is left
    # after LPing
    SDL_price_impact_factor = 1.3
    amount_in = USDC_contract.balanceOf(
        ops_multisig.address
    ) / 2 * SDL_price_impact_factor

    # getting min amounts
    print(
        f"Getting quote for WETH"
    )
    amount_out_min = univ3_quoter.quoteExactInputSingle(
        token_from_address,
        token_to_address,
        fee,
        amount_in,
        sqrt_price_limit_X96,
        {"from": ops_multisig.address}
    ).return_value

    # input struct for univ3 swap
    params = (
        token_from_address,
        token_to_address,
        fee,
        recipient,
        deadline,
        amount_in,
        amount_out_min,
        sqrt_price_limit_X96
    )

    # approve Univ3 router
    print(
        f"Approve UniV3 router for USDC {amount_in / (10 ** USDC_decimals)}"
    )
    USDC_contract.approve(
        UNIV3_ROUTER,
        amount_in,
        {"from": ops_multisig.address}
    )

    # swap using univ3
    print(
        f"Swap {amount_in / (10 ** USDC_decimals)} USDC for WETH on UniV3"
    )
    univ3_router.exactInputSingle(
        params,
        {"from": ops_multisig.address}
    )

    USDC_balance_after = USDC_contract.balanceOf(ops_multisig.address)

    assert (USDC_balance_after < 0.51 * USDC_balance_before * SDL_price_impact_factor and
            USDC_balance_after > 0.49 * USDC_balance_before * (1 - SDL_price_impact_factor))

    print(
        "Balances after swap:\n"
        f"USDC: {USDC_contract.balanceOf(ops_multisig.address)/ (10 ** USDC_decimals)}\n" +
        f"WETH: {WETH_contract.balanceOf(ops_multisig.address)/ (10 ** WETH_decimals)}"
    )

    # TODO: set 'safe_nonce'
    safe_tx = ops_multisig.multisend_from_receipts()
    safe_nonce = 0

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    ops_multisig.preview(safe_tx)
    confirm_posting_transaction(ops_multisig, safe_tx)
