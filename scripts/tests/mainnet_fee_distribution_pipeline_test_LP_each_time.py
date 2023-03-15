from helpers import (
    CHAIN_IDS,
    MULTISIG_ADDRESSES,
    OPS_MULTISIG_ADDRESSES
)
from ape_safe import ApeSafe
from scripts.utils import (
    claim_admin_fees,
    convert_fees_to_USDC_saddle,
    convert_fees_to_USDC_curve,
    convert_fees_to_USDC_uniswap,
    buy_weth_with_usdc_univ3,
    buy_weth_with_usdc_sushi,
    buy_sdl_with_usdc_sushi,
    provide_sdl_eth_lp_sushi,
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
    1. Buy SDL on sushi and fraxswap
    2. provide LP on sushi
    """

    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
    )

    ops_multisig = ApeSafe(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    )

    ######## 2022_xx_xx_7_0_opsMsig_provide_LP_tranche_1.py ########
    
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
        multisig,
        CHAIN_IDS[TARGET_NETWORK],
        weth_amount,
        sdl_amount,
        tolerance_factor = 0.5
    )

    ######## 2022_xx_xx_7_1_opsMsig_provide_LP_tranche_2.py ########

    ######## 2022_xx_xx_7_2_opsMsig_provide_LP_tranche_3.py ########

    ######## 2022_xx_xx_7_3_opsMsig_provide_LP_tranche_3.py ########


    #for tx in history:
    #    tx.info()
