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
    buy_weth_with_usdc,
    buy_sdl_with_usdc_sushi,
    provide_sdl_eth_lp_sushi
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

    claim_admin_fees(multisig, CHAIN_IDS[TARGET_NETWORK])

    ############# 2022_xx_xx_6_opsMsig_swap_fees_to_USDC.py #############

    ops_multisig = ApeSafe(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    )

    convert_fees_to_USDC_saddle(
        ops_multisig,
        CHAIN_IDS[TARGET_NETWORK]
    )

    convert_fees_to_USDC_curve(
        ops_multisig,
        CHAIN_IDS[TARGET_NETWORK]
    )

    convert_fees_to_USDC_uniswap(
        ops_multisig,
        CHAIN_IDS[TARGET_NETWORK],
    )

    ######## 2022_xx_xx_7_0_opsMsig_market_buy_WETH_with_USDC.py ########

    buy_weth_with_usdc(ops_multisig, CHAIN_IDS[TARGET_NETWORK])

    ######## 2022_xx_xx_7_1_opsMsig_market_buy_SDL_tranche_1.py #########

    buy_sdl_with_usdc_sushi(ops_multisig, CHAIN_IDS[TARGET_NETWORK], 4)

    ######## 2022_xx_xx_7_1_opsMsig_market_buy_SDL_tranche_2.py #########

    buy_sdl_with_usdc_sushi(ops_multisig, CHAIN_IDS[TARGET_NETWORK], 3)

    ######## 2022_xx_xx_7_1_opsMsig_market_buy_SDL_tranche_3.py #########

    buy_sdl_with_usdc_sushi(ops_multisig, CHAIN_IDS[TARGET_NETWORK], 2)

    ######## 2022_xx_xx_7_1_opsMsig_market_buy_SDL_tranche_4.py #########

    buy_sdl_with_usdc_sushi(ops_multisig, CHAIN_IDS[TARGET_NETWORK], 1)

    ######### 2022_xx_xx_8_opsMsig_LP_SDL_WETH_in_sushi_pool.py #########

    provide_sdl_eth_lp_sushi(ops_multisig, multisig, CHAIN_IDS[TARGET_NETWORK])

    for tx in history:
        tx.info()
