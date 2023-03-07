from brownie import Contract, Wei, accounts, history, network
from brownie.network import max_fee, priority_fee

from helpers import ANYCALL_V6_ADDRESS, CHAIN_IDS, get_contract_from_deployment

SUPPORTED_NETWORKS = ["MAINNET", "OPTIMISM", "ARBITRUM"]


def main():
    """
    Fund AnyCallV6 and tops the credit upto 0.1 ETH for AnyCallTranslator

    This script is meant to be run on all supported networks. It will check
    the current budget for AnyCallTranslator on the network and top it up
    if it is less than 0.1 ETH.

    Mainnet credit is not required if we are not going to use CGF.mint()
    """
    print(f"You are using the '{network.show_active()}' network")

    target_network = None
    for network_name in SUPPORTED_NETWORKS:
        if network.chain.id == CHAIN_IDS[network_name]:
            target_network = network_name
            break

    # Disable the EOA dynamic fee settings if using ganache v6 / pre-london fork
    priority_fee("auto")
    max_fee(Wei("25 gwei"))

    assert (
        network.chain.id == CHAIN_IDS[target_network]
    ), f"Not on any of the supported networks: {SUPPORTED_NETWORKS}"

    deployer = accounts.load("deployer")

    anycall_v6 = Contract.from_explorer(ANYCALL_V6_ADDRESS)
    any_call_translator = get_contract_from_deployment(
        CHAIN_IDS[target_network], "AnyCallTranslator")

    # Get the current budget for the AnyCallTranslator on this network
    current_budget = anycall_v6.executionBudget(any_call_translator.address)
    print(
        f"Current budget for AnyCallTranslator ({any_call_translator.address}) : {current_budget / 1e18} ETH")

    # If the budget is less than 0.1e18, top it up
    if current_budget < 0.09e18:
        print("Topping up AnyCallTranslator budget for AnyCallV6")
        top_up_amount = 0.1e18 - current_budget
        anycall_v6.deposit(
            any_call_translator.address,
            {"from": deployer, "value": top_up_amount})

    for tx in history:
        tx.info()
    return
