import csv

from brownie import Contract, accounts, history, network
from brownie.network import max_fee, priority_fee

from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, get_contract_from_deployment

TARGET_NETWORK = "MAINNET"


def main():
    """
    Move any permissions from the EOAs to Saddle multisig
    """
    print(f"You are using the '{network.show_active()}' network")
    assert (
        network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    ), f"Not on {TARGET_NETWORK} network"

    deployer_EOA = accounts.load("deployer")
    priority_fee("auto")
    max_fee(15000000000)

    root_oracle = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "RootOracle")
    voting_escrow = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "VotingEscrow")

    chain_ids = [CHAIN_IDS["ARBITRUM"], CHAIN_IDS["OPTIMISM"]]

    # Read all veSDL holders from csv into a set
    historical_veSDL_holders = set()

    with open('csv/veSDL.csv', mode='r') as f:
        reader = csv.DictReader(f, delimiter=',')
        for n, row in enumerate(reader):
            if not n:  # skip header
                continue
            historical_veSDL_holders.add(row['wallet'])

    # Create a list with addresses with positive veSDL balance
    current_veSDL_holders = []

    for holder in historical_veSDL_holders:
        current_balance = voting_escrow.balanceOf(holder)
        print(f"{holder}: {current_balance} veSDL")
        if current_balance > 0:
            current_veSDL_holders.append(holder)

    # Bridge info for veSDL holders
    calls = []

    for chain_id in chain_ids:
        for veSDL_holder in current_veSDL_holders:
            calls.append([
                root_oracle.address,
                root_oracle.push.encode_input(chain_id, veSDL_holder)
            ])

    print(calls)

    multicall = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "Multicall3")

    multicall.aggregate(calls, {"from": deployer_EOA})

    for tx in history:
        tx.info()
    return
