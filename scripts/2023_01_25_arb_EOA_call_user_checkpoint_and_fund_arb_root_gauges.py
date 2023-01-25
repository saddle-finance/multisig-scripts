import csv

from brownie import ZERO_ADDRESS, Contract, Wei, accounts, history, network
from brownie.network import max_fee, priority_fee

from helpers import (CHAIN_IDS, MULTISIG_ADDRESSES,
                     get_contract_from_deployment,
                     get_contracts_from_deployment)

TARGET_NETWORK = "ARBITRUM"


def main():
    """
    Calls mint() on ChildGaugeFactory with all ChildGauge addresses
    """
    print(f"You are using the '{network.show_active()}' network")
    assert (
        network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    ), f"Not on {TARGET_NETWORK} network"

    deployer_EOA = accounts.load("deployer")
    priority_fee("auto")
    max_fee(15000000000)

    # List of calls to be used for Multicall3
    multicall3 = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "Multicall3")
    muticall3_calls = []

    # ChildGaugeFactory contract
    childGaugeFactory = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "ChildGaugeFactory")

    # Get all child gauges on this network
    all_child_gauges = get_contracts_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "ChildGauge_*")

    # Calls mint() on the ChildGaugeFactory with the child gauge addresses
    # Encode the call data for Multicall3
    for child_gauge in all_child_gauges.values():
        muticall3_calls.append([
            childGaugeFactory.address,
            childGaugeFactory.mint.encode_input(child_gauge)
        ])

    # Call all mint() calls in one Multicall3 transaction
    multicall3.tryAggregate(False, muticall3_calls, {"from": deployer_EOA})

    for tx in history:
        tx.info()
    return
