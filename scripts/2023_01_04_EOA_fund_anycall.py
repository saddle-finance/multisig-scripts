from brownie import Contract, accounts, history, network

from helpers import ANYCALL_V6_ADDRESS, CHAIN_IDS, get_contract_from_deployment

TARGET_NETWORK = "MAINNET"


def main():
    """
    Fund AnyCallV6 upto 0.1 ETH for AnyCallTranslator
    """
    print(f"You are using the '{network.show_active()}' network")
    assert (
        network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    ), f"Not on {TARGET_NETWORK} network"

    anycall_v6 = Contract.from_explorer(ANYCALL_V6_ADDRESS)

    any_call_translator = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "AnyCallTranslator")

    current_budget = anycall_v6.executionBudget(any_call_translator.address)
    print(
        f"Current budget for AnyCallTranslator ({any_call_translator.address}) : {current_budget / 1e18} ETH")

    # If the budget is less than 0.1e18, top it up
    if current_budget < 0.09e18:
        top_up_amount = 0.1e18 - current_budget
        anycall_v6.deposit(
            any_call_translator.address,
            {"from": accounts.load("deployer"), "value": top_up_amount})

    for tx in history:
        tx.info()
    return
