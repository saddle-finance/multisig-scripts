from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    ARB_GATEWAY_ROUTER,
    MULTISIG_ADDRESSES,
    OPS_MULTISIG_ADDRESSES,
)
from ape_safe import ApeSafe
from scripts.utils import (
    claim_admin_fees,
    convert_fees_to_USDC_saddle,
    bridge_usdc_to_mainnet
)
from fee_distro_helpers import (
    token_addresses
)
from ape_safe import ApeSafe
from brownie import Contract
from eth_abi import encode
from brownie import history


TARGET_NETWORK = "ARBITRUM"


def main():
    """
    This tests fee claiming and bridging on Arbitrum
    """

    ############# 2022_xx_xx_1_0_arb_claim_admin_fees.py ##############

    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
    )

    claim_admin_fees(multisig, CHAIN_IDS[TARGET_NETWORK])

    ############# 2022_xx_xx_1_1_arb_opsMsig_swap_fees_to_USDC_and_bridge.py #############

    ops_multisig = ApeSafe(OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    # Run any pending transactions before simulating any more transactions
    # ops_multisig.preview_pending()

    # Arbitrum L2 gateway router
    gateway_router = ops_multisig.contract(
        ARB_GATEWAY_ROUTER[CHAIN_IDS[TARGET_NETWORK]]
    )

    # convert fees to USDC
    convert_fees_to_USDC_saddle(ops_multisig, CHAIN_IDS[TARGET_NETWORK])

    bridge_usdc_to_mainnet(ops_multisig, CHAIN_IDS[TARGET_NETWORK])

    for tx in history:
        tx.info()
