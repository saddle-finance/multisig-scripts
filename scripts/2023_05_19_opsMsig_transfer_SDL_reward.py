from ape_safe import ApeSafe
from brownie import accounts, network

from helpers import (CHAIN_IDS, OPS_MULTISIG_ADDRESSES,
                     get_contract_from_deployment, get_deployment_details,
                     read_two_column_csv_to_dict)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "ARBITRUM"


def main():
    """
    Send additional SDL reward to ChildGauge_CommunityfUSDCPoolLPTokenV3 for the week of 05/19/2023
    """

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"

    ops_multisig = ApeSafe(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    )

    sdl = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "SDL", ops_multisig.account)

    child_gauge_fusdc = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "ChildGauge_CommunityfUSDCPoolLPTokenV3", ops_multisig.account)

    # Inject additional SDL reward for this epoch
    # Next mint call for this gauge will count this SDL as rewards emitted from gauge votes
    sdl.transfer(child_gauge_fusdc, 1_000_000 * 1e18 / 12)

    safe_tx = ops_multisig.multisend_from_receipts()

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    ops_multisig.preview(safe_tx)

    confirm_posting_transaction(ops_multisig, safe_tx)
