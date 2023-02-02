import math

from ape_safe import ApeSafe
from brownie import ZERO_ADDRESS, Contract, accounts, history, network

from helpers import (CHAIN_IDS, GAUGE_CONTROLLER_ADDRESS,
                     GNOSIS_SAFE_BASE_URLS, MINICHEF_ADDRESSES,
                     MULTISIG_ADDRESSES, SIDECHAIN_TOTAL_EMISSION_RATE,
                     get_contract_from_deployment, get_deployment_details)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():
    """
    Adds root gauges to the gauge controller
    Accept any ownerships that are pending
    """
    print(f"You are using the '{network.show_active()}' network")
    assert (
        network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    ), f"Not on {TARGET_NETWORK} network"

    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
                       GNOSIS_SAFE_BASE_URLS[CHAIN_IDS[TARGET_NETWORK]])

    gauge_controller = multisig.contract(
        GAUGE_CONTROLLER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]
    )

    # Add all root gauges to gauge controller
    root_gauges = [
        "RootGauge_10_SaddleFRAXBPPoolLPToken",
        "RootGauge_10_SaddleFRAXUSDTMetaPoolLPToken",
        "RootGauge_10_SaddleFRAXsUSDMetaPoolLPToken",
        "RootGauge_10_SaddleOptFRAXMetaPoolLPToken",
        "RootGauge_10_SaddleOptUSDPoolLPToken",
        "RootGauge_10_SaddleUSXFRAXBPMetaPoolLPToken",
        "RootGauge_42161_SaddleArbUSDPoolLPToken",
        "RootGauge_42161_SaddleArbUSDPoolV2LPToken",
        "RootGauge_42161_SaddleArbUSDSMetaPoolLPToken",
        "RootGauge_42161_SaddleFRAXBPPoolLPToken",
        "RootGauge_42161_SaddleFRAXUSDTMetaPoolLPToken",
        "RootGauge_42161_SaddleFRAXUSDsMetaPoolLPToken",
        "RootGauge_42161_SaddleUSXFRAXBPMetaPoolLPToken"
    ]

    for name in root_gauges:
        address, abi = get_deployment_details(CHAIN_IDS["MAINNET"], name)
        gauge_controller.add_gauge(address, 0, 0)

    # Accept any ownerships that are pending
    root_gauge_factory = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "RootGaugeFactory", multisig.account)
    root_oracle = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "RootOracle", multisig.account)

    root_gauge_factory.accept_transfer_ownership()
    root_oracle.acceptTransferOwnership()

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 80

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
