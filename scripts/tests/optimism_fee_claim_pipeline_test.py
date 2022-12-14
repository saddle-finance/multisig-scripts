from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    MULTISIG_ADDRESSES,
    OPS_MULTISIG_ADDRESSES,
    OPTIMISM_STANDARD_BRIDGE,
    OPTIMISM_L2_STANDARD_BRIDGE_ABI

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
from brownie import Contract, history


TARGET_NETWORK = "OPTIMISM"


def main():
    """
    This tests fee claiming and bridging on Optimism
    """

    ############# 2022_xx_xx_1_0_opt_claim_admin_fees.py ##############

    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url="https://safe-transaction-optimism.safe.global",
    )

    claim_admin_fees(multisig, CHAIN_IDS[TARGET_NETWORK])

    ############# 2022_xx_xx_2_1_opt_opsMsig_swap_fees_to_USDC.py ##############

    ops_multisig = ApeSafe(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url="https://safe-transaction-optimism.safe.global",
    )

    # convert fees to USDC
    convert_fees_to_USDC_saddle(ops_multisig, CHAIN_IDS[TARGET_NETWORK])

    bridge_usdc_to_mainnet(ops_multisig, CHAIN_IDS[TARGET_NETWORK])

    for tx in history:
        tx.info()
