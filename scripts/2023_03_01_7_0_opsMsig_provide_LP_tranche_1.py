from helpers import (
    CHAIN_IDS,
    OPS_MULTISIG_ADDRESSES,
)
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
from brownie import history


TARGET_NETWORK = "MAINNET"


def main():
    """
    1. Buy $15k total SDL on sushi and fraxswap in given ratio
    2. Buy required WETH on sushi to match SDL value for LPing
    3. Provide LP on sushi
    """

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

    # buy $15k worth of WETH and SDL each with USDC and provide LP to sushi pool
    price_impact_factor = 1.55
    total_usdc_amount_to_buy_sdl = 15_000 * 1e6
    sushi_percentage = 0.3
    fraxswap_percentage = 0.7

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
        tolerance_factor = 0.95
    )

    # TODO: set 'safe_nonce'
    safe_tx = ops_multisig.multisend_from_receipts()
    safe_nonce = 3

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    # ops_multisig.preview(safe_tx)
    for tx in history:
        tx.info()
    confirm_posting_transaction(ops_multisig, safe_tx)
