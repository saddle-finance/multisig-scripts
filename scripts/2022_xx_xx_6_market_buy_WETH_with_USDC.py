import this
from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    META_SWAP_DEPOSIT_ABI,
    MULTISIG_ADDRESSES,
    SWAP_ABI,
    META_SWAP_ABI,
    UNIV3_ROUTER_ABI,
    UNIV3_QUOTER_ABI
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract, chain
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "MAINNET"


def main():
    """This script buys WETH with half of the multisig's USDC balance"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url='https://safe-transaction.optimism.gnosis.io/'
    )

    # Run any pending transactions before simulating any more transactions
    # multisig.preview_pending()

    USDC_MAINNET = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    WETH_MAINNET = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

    UNIV3_ROUTER = "0xE592427A0AEce92De3Edee1F18E0157C05861564"
    UNIV3_QUOTER = "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6"

    univ3_router = Contract.from_abi(
        "UniV3Router", UNIV3_ROUTER, UNIV3_ROUTER_ABI
    )
    univ3_quoter = Contract.from_abi(
        "UniV3Quoter", UNIV3_QUOTER, UNIV3_QUOTER_ABI
    )

    USDC_contract = Contract.from_abi(
        "ERC20", USDC_MAINNET, ERC20_ABI
    )
    WETH_contract = Contract.from_abi(
        "ERC20", WETH_MAINNET, ERC20_ABI
    )
    USDC_decimals = USDC_contract.decimals()
    WETH_decimals = WETH_contract.decimals()

    USDC_balance_before = USDC_contract.balanceOf(multisig.address)

    token_from_address = USDC_MAINNET
    token_to_address = WETH_MAINNET
    fee = 500
    recipient = multisig.address
    deadline = chain[chain.height].timestamp + 10 * 60
    sqrt_price_limit_X96 = 0

    # swap half of multisig's USDC for WETH
    amount_in = USDC_contract.balanceOf(multisig.address) / 2

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
        {"from": multisig.address}
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
        {"from": multisig.address}
    )

    # swap using univ3
    print(
        f"Swap {amount_in / (10 ** USDC_decimals)} USDC for WETH on UniV3"
    )
    univ3_router.exactInputSingle(
        params,
        {"from": multisig.address}
    )

    USDC_balance_after = USDC_contract.balanceOf(multisig.address)

    assert (USDC_balance_after < 0.51 * USDC_balance_before and
            USDC_balance_after > 0.49 * USDC_balance_before)

    print(
        "Balances after swap:\n"
        f"USDC: {USDC_contract.balanceOf(multisig.address)/ (10 ** USDC_decimals)}\n" +
        f"WETH: {WETH_contract.balanceOf(multisig.address)/ (10 ** WETH_decimals)}"
    )

    # TODO: set 'safe_nonce'
    safe_tx = multisig.multisend_from_receipts()
    safe_nonce = 0

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    multisig.preview(safe_tx)
    confirm_posting_transaction(multisig, safe_tx)
