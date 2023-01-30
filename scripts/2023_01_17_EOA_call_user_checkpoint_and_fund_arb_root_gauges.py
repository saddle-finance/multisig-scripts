import csv

from brownie import ZERO_ADDRESS, Contract, Wei, accounts, history, network
from brownie.network import max_fee, priority_fee

from helpers import (CHAIN_IDS, MULTISIG_ADDRESSES,
                     get_contract_from_deployment,
                     get_contracts_from_deployment)

TARGET_NETWORK = "MAINNET"


def main():
    """
    Call user_checkpoint() on all RootGauges for saving gas for future user calls
    Fund Arbitrum RootGauges on mainnet with 0.1 ETH each for future user briging costs
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

    # Get all root gauges on mainnet
    all_root_gauges = get_contracts_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "RootGauge_*")

    # Call user_checkpoint on all RootGauges
    # Encode the call data for Multicall3
    for root_gauge in all_root_gauges.values():
        muticall3_calls.append([
            root_gauge.address,
            root_gauge.user_checkpoint.encode_input(deployer_EOA)
        ])

    # Call all user_checkpoint() calls in one Multicall3 transaction
    multicall3.aggregate(muticall3_calls, {"from": deployer_EOA})

    # Fund Arbitrum RootGauges on mainnet with 0.1 ETH each for future user briging costs
    # Use MultisendEther for batching
    multicall3_calls_values = []
    total_eth_to_send = 0

    arb_root_gauges = get_contracts_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "RootGauge_42161*", deployer_EOA)

    for arb_root_gauge in arb_root_gauges.values():
        multicall3_calls_values.append([
            arb_root_gauge.address,
            False,
            Wei("0.05 ether"),
            ""
        ])
        total_eth_to_send += Wei("0.05 ether")

    multicall3.aggregate3Value(multicall3_calls_values, {
        "from": deployer_EOA, "value": total_eth_to_send})

    for tx in history:
        tx.info()
    return
