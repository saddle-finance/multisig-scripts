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
    get_sdl_value_in_usdc_sushi
)
from brownie import history


TARGET_NETWORK = "MAINNET"


# This script concatenates all mainnet scripts (5 to 8)

def main():
    """This script claims admin fees from all Mainnet pools,
    then converts them to SDL/ETH SLP and sends it to main multisig for distribution
    Steps are:
    1. Claim admin fees on all pools
    2. Burn claimed LPs to get underlyings and send them to ops multisig
    3. Swap assets into USDC, WBTC, WETH using Saddle, if possible
    4. Swap remaining assets into USDC, using UniswapV3
    5. Buy SDL+ETH 50/50 and LP in Sushi pool
    6. Send SDL/ETH SLP to main multisig for distribution
    """

    ############# 2022_xx_xx_5_mainnet_claim_admin_fees.py ##############

    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
    )

    #claim_admin_fees(multisig, CHAIN_IDS[TARGET_NETWORK])

    ############# 2022_xx_xx_6_opsMsig_swap_fees_to_USDC.py #############

    ops_multisig = ApeSafe(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    )

    #convert_fees_to_USDC_saddle(
    #    ops_multisig,
    #   CHAIN_IDS[TARGET_NETWORK]
    #)

    #convert_fees_to_USDC_curve(
    #    ops_multisig,
    #    CHAIN_IDS[TARGET_NETWORK]
    #)

    # convert_fees_to_USDC_uniswap(
    #    ops_multisig,
    #    CHAIN_IDS[TARGET_NETWORK],
    # )

    ######## 2022_xx_xx_7_0_opsMsig_provide_LP_tranche_1.py ########
    
    price_impact_factor = 1.4

    sdl_amount = buy_sdl_with_usdc_sushi_custom_amount(
        ops_multisig,
        CHAIN_IDS[TARGET_NETWORK],
        usdc_amount = 10_000 * 1e6
    )

    usdc_to_buy_weth_with = get_sdl_value_in_usdc_sushi(
        CHAIN_IDS[TARGET_NETWORK],
        sdl_amount
    ) * price_impact_factor

    weth_amount = buy_weth_with_usdc_sushi_custom_amount(
        ops_multisig, 
        CHAIN_IDS[TARGET_NETWORK],
        usdc_amount = usdc_to_buy_weth_with 
    )

    provide_sdl_eth_lp_sushi_custom_amounts(
        ops_multisig,
        multisig,
        CHAIN_IDS[TARGET_NETWORK],
        weth_amount,
        sdl_amount,
        tolerance_factor = 0.95
    )
    
    ######## 2022_xx_xx_7_1_opsMsig_provide_LP_tranche_2.py ########

    price_impact_factor = 1.4

    sdl_amount = buy_sdl_with_usdc_sushi_custom_amount(
        ops_multisig,
        CHAIN_IDS[TARGET_NETWORK],
        usdc_amount = 10_000 * 1e6
    )

    usdc_to_buy_weth_with = get_sdl_value_in_usdc_sushi(
        CHAIN_IDS[TARGET_NETWORK],
        sdl_amount
    ) * price_impact_factor

    weth_amount = buy_weth_with_usdc_sushi_custom_amount(
        ops_multisig, 
        CHAIN_IDS[TARGET_NETWORK],
        usdc_amount = usdc_to_buy_weth_with 
    )

    provide_sdl_eth_lp_sushi_custom_amounts(
        ops_multisig,
        multisig,
        CHAIN_IDS[TARGET_NETWORK],
        weth_amount,
        sdl_amount,
        tolerance_factor = 0.5
    )

    ######## 2022_xx_xx_7_2_opsMsig_provide_LP_tranche_3.py ########

    price_impact_factor = 1.2

    sdl_amount = buy_sdl_with_usdc_sushi_custom_amount(
        ops_multisig,
        CHAIN_IDS[TARGET_NETWORK],
        usdc_amount = 10_000 * 1e6
    )

    usdc_to_buy_weth_with = get_sdl_value_in_usdc_sushi(
        CHAIN_IDS[TARGET_NETWORK],
        sdl_amount
    ) * price_impact_factor

    weth_amount = buy_weth_with_usdc_sushi_custom_amount(
        ops_multisig, 
        CHAIN_IDS[TARGET_NETWORK],
        usdc_amount = usdc_to_buy_weth_with 
    )

    provide_sdl_eth_lp_sushi_custom_amounts(
        ops_multisig,
        multisig,
        CHAIN_IDS[TARGET_NETWORK],
        weth_amount,
        sdl_amount,
        tolerance_factor = 0.95
    )

    ######## 2022_xx_xx_7_3_opsMsig_provide_LP_tranche_4.py ########

    price_impact_factor = 1.1

    sdl_amount = buy_sdl_with_usdc_sushi_custom_amount(
        ops_multisig,
        CHAIN_IDS[TARGET_NETWORK],
        usdc_amount = 10_000 * 1e6
    )

    usdc_to_buy_weth_with = get_sdl_value_in_usdc_sushi(
        CHAIN_IDS[TARGET_NETWORK],
        sdl_amount
    ) * price_impact_factor

    weth_amount = buy_weth_with_usdc_sushi_custom_amount(
        ops_multisig, 
        CHAIN_IDS[TARGET_NETWORK],
        usdc_amount = usdc_to_buy_weth_with 
    )

    provide_sdl_eth_lp_sushi_custom_amounts(
        ops_multisig,
        multisig,
        CHAIN_IDS[TARGET_NETWORK],
        weth_amount,
        sdl_amount,
        tolerance_factor = 0.95
    )

    #for tx in history:
    #    tx.info()
