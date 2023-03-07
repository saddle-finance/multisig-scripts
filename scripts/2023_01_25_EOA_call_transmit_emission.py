import csv

from brownie import ZERO_ADDRESS, Contract, Wei, accounts, history, network
from brownie.network import max_fee, priority_fee

from helpers import (CHAIN_IDS, MULTISIG_ADDRESSES,
                     get_contract_from_deployment,
                     get_contracts_from_deployment)

TARGET_NETWORK = "MAINNET"


def main():
    """
    Individually calls RGF.transmit_emissions() on Optimism RootGauges on mainnet
    """
    print(f"You are using the '{network.show_active()}' network")
    assert (
        network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    ), f"Not on {TARGET_NETWORK} network"

    deployer_EOA = accounts.load("deployer")
    priority_fee("auto")
    max_fee(17000000000)

    # RootGaugeFactory contract
    rootGaugeFactory = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "RootGaugeFactory")

    # Get all root gauges for optimism network on mainnet
    opt_root_gauges = get_contracts_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "RootGauge_10_*")

    # Calls mint() on the ChildGaugeFactory with the child gauge addresses
    # Encode the call data for Multicall3
    for child_gauge in opt_root_gauges.values():
        try:
            rootGaugeFactory.transmit_emissions(
                child_gauge, {"from": deployer_EOA})
        except:
            print(
                f"Failed to call transmit_emissions on {child_gauge}. Already called this week?")

    for tx in history:
        tx.info()
    return
