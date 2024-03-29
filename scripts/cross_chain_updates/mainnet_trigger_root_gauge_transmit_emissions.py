import traceback

from brownie import Wei, accounts, history, network
from brownie.network import max_fee, priority_fee

from helpers import (CHAIN_IDS, get_contract_from_deployment,
                     get_contracts_from_deployment)

TARGET_NETWORK = "MAINNET"


def main():
    """
    Individually calls RGF.transmit_emissions() on all RootGauges on mainnet
    Also tops up RootGauges for Arbitrum that are low on ETH for bridging
    """
    print(f"You are using the '{network.show_active()}' network")
    assert (
        network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    ), f"Not on {TARGET_NETWORK} network"

    deployer_EOA = accounts.load("deployer")

    # Disable the dynamic fee settings if using ganache v6 / pre-london fork
    priority_fee("auto")
    max_fee(Wei("70 gwei"))

    # RootGaugeFactory contract
    rootGaugeFactory = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "RootGaugeFactory")

    # Get all root gauges on mainnet
    all_root_gauges = get_contracts_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "RootGauge_*")

    # Calls transmit_emissions() on the RootGaugeFactory with the root gauge addresses
    for root_gauge_name, root_gauge in all_root_gauges.items():
        try:
            # Arbitrum RootGauges need some ETH to pay the official bridge fee.
            # If root_gauge_name contains "RootGauge_42161" has less than 0.05 ETH, top upto 0.05 ETH from deployer EOA
            if f'RootGauge_{CHAIN_IDS["ARBITRUM"]}' in root_gauge_name and root_gauge.balance() < Wei("0.05 ether"):
                deployer_EOA.transfer(root_gauge, Wei("0.05 ether"))

            # Call transmit_emissions() on the root gauge.
            # Call fails in below conditions:
            # 1. If the RootGauge has no weight for the week
            # 2. If the gauge has already called transmit_emissions() for the week.
            # 3. (RootGauges for Arbitrum only) If the gauge doesn't have enough ETH to pay the bridge fee.
            rootGaugeFactory.transmit_emissions(
                root_gauge, {"from": deployer_EOA})
        except Exception as e:
            print(
                f"Failed to call transmit_emissions on {root_gauge}. Already called this week?")
            print(e)
            traceback.print_exc()

    for tx in history:
        tx.info()
    return
