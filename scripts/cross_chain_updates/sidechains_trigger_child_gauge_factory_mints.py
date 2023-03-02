

from brownie import Wei, accounts, history, network
from brownie.network import max_fee, priority_fee

from helpers import (CHAIN_IDS, get_contract_from_deployment,
                     get_contracts_from_deployment)

SUPPORTED_SIDECHAIN_NETWORKS = ["ARBITRUM", "OPTIMISM"]


def main():
    """
    Calls mint() on ChildGaugeFactory with all ChildGauge addresses

    Two things can happen here based on whether the mint() call has been called this week:

    1. If the mint has not been called this week, this mint() call will succeed by
       using AnyCall and AnyCallTranslator to trigger the matching transmit_emissions() call
       on the Mainnet.

    2. The mint has already been called this week OR if the ChildGauge contract has recieved SDL
       since the last call, the call will be successful. It attempts to
       tranfer any SDL token it has to the ChildGaugeFactory. This will allow the
       stakers to claim the SDL tokens from the ChildGaugeFactory.

       Note that even if there is no SDL token to transfer, the call will still succeed.
       This is repeatable so if bridging fails for some reason, the call can be repeated.

    Currently, we are calling transmit_emissions() on the Mainnet RootGauges individually.
    So this script should be run after all bridging from mainnet has been completed.
    """
    print(f"You are using the '{network.show_active()}' network")

    # Check if this network is running on a supported sidechain network
    # If so, set variable target_network to the matching network name
    target_network = None
    for network_name in SUPPORTED_SIDECHAIN_NETWORKS:
        if network.chain.id == CHAIN_IDS[network_name]:
            target_network = network_name
            break

    # If target_network is not set, then this network is not supported
    assert (
        target_network is not None
    ), f"Not on a supported sidechain network: {SUPPORTED_SIDECHAIN_NETWORKS}"

    deployer_EOA = accounts.load("deployer")

    # Disable the dynamic fee settings if using ganache v6 / pre-london fork
    if network.chain.id == CHAIN_IDS["ARBITRUM"]:
        priority_fee("auto")
        max_fee(Wei("15 gwei"))

    # List of calls to be used for Multicall3
    multicall3 = get_contract_from_deployment(
        CHAIN_IDS[target_network], "Multicall3")
    muticall3_calls = []

    # ChildGaugeFactory contract
    childGaugeFactory = get_contract_from_deployment(
        CHAIN_IDS[target_network], "ChildGaugeFactory")

    # Get all child gauges on this network
    all_child_gauges = get_contracts_from_deployment(
        CHAIN_IDS[target_network], "ChildGauge_*")

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
