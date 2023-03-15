from helpers import (
    CHAIN_IDS,
    OPS_MULTISIG_ADDRESSES,
    ERC20_ABI
)
from fee_distro_helpers import token_addresses
from ape_safe import ApeSafe
from brownie import accounts, network
from scripts.utils import (
    confirm_posting_transaction, 
    swap_curve,
    provide_sdl_eth_lp_sushi_custom_amounts,
    buy_weth_with_usdc_sushi_custom_amount,
    buy_sdl_with_usdc_sushi_custom_amount,
    get_sdl_value_in_usdc_sushi,
    buy_sdl_with_usdc_fraxswap_custom_amount
)
from brownie import history, Contract


TARGET_NETWORK = "MAINNET"


def main():
    """
    1. Buy $40k total SDL on sushi and fraxswap in given ratio
    2. Buy required WETH on sushi to match SDL value for LPing
    3. Provide LP on sushi
    """

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"

    ops_multisig = ApeSafe(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    )

    # buy $48k worth of WETH and SDL each with USDC and provide LP to sushi pool
    price_impact_factor = 1.95
    total_usdc_amount_to_buy_sdl = 48_000 * 1e6
    sushi_percentage = 0.45
    fraxswap_percentage = 0.55

    # buy SDL on sushi
    sdl_amount = buy_sdl_with_usdc_sushi_custom_amount(
        ops_multisig,
        CHAIN_IDS[TARGET_NETWORK],
        usdc_amount = total_usdc_amount_to_buy_sdl * sushi_percentage
    )

    # buy SDL on fraxswap
    sdl_amount += buy_sdl_with_usdc_fraxswap_custom_amount(
        ops_multisig,
        CHAIN_IDS[TARGET_NETWORK],
        usdc_amount = total_usdc_amount_to_buy_sdl * fraxswap_percentage
    )

    # get how much the SDL balance after swaps is worth in USDC on sushi
    usdc_to_buy_weth_with = get_sdl_value_in_usdc_sushi(
        CHAIN_IDS[TARGET_NETWORK],
        sdl_amount
    )

    weth_amount = buy_weth_with_usdc_sushi_custom_amount(
        ops_multisig, 
        CHAIN_IDS[TARGET_NETWORK],
        usdc_amount = usdc_to_buy_weth_with * price_impact_factor
    )

    # provide LP on sushi
    provide_sdl_eth_lp_sushi_custom_amounts(
        ops_multisig,
        CHAIN_IDS[TARGET_NETWORK],
        weth_amount,
        sdl_amount,
        tolerance_factor = 0.6
    )

    USDC = Contract.from_abi(
        "USDC",token_addresses[CHAIN_IDS[TARGET_NETWORK]]["USDC"], ERC20_ABI
    )
    print(f"USDC balance: {USDC.balanceOf(ops_multisig.address)/1e6} USDC")

    # TODO: set 'safe_nonce'
    safe_tx = ops_multisig.multisend_from_receipts()
    safe_nonce = 5

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    #ops_multisig.preview(safe_tx)
    for tx in history:
        tx.info()
    confirm_posting_transaction(ops_multisig, safe_tx)
