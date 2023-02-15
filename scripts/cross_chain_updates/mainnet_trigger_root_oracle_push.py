import csv

from brownie import Wei, accounts, history, network
from brownie.network import max_fee, priority_fee

from helpers import CHAIN_IDS, get_contract_from_deployment

TARGET_NETWORK = "MAINNET"

SIDECHAIN_CHAIN_IDS = [CHAIN_IDS["ARBITRUM"], CHAIN_IDS["OPTIMISM"]]


def main():
    """
    Read veSDL holders from csv and push their balances to the RootOracle
    This will use AnyCall to push the balances to the ChildOracles on the sidechains.
    veSDL.csv should be updated before running this script.

    Ideally veSDL.csv should only contain the new veSDL activity since the last time this script was run.
    """
    print(f"You are using the '{network.show_active()}' network")
    assert (
        network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    ), f"Not on {TARGET_NETWORK} network"

    deployer_EOA = accounts.load("deployer")

    # Disable the dynamic fee settings if using ganache v6 / pre-london fork
    priority_fee("auto")
    max_fee(Wei("25 gwei"))

    root_oracle = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "RootOracle")
    voting_escrow = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "VotingEscrow")

    # Read all veSDL holders from csv into a set
    historical_veSDL_holders = set()

    # Read latest veSDL holders from csv into a set
    with open('csv/veSDL.csv', mode='r') as f:
        reader = csv.DictReader(f, delimiter=',')
        for n, row in enumerate(reader):
            if not n:  # skip header
                continue
            historical_veSDL_holders.add(row['wallet'])

    # Create a list with addresses with positive veSDL balances only
    current_veSDL_holders = []

    for holder in historical_veSDL_holders:
        current_balance = voting_escrow.balanceOf(holder)
        print(f"{holder}: {current_balance} veSDL")
        if current_balance > 0:
            current_veSDL_holders.append(holder)

    # Bridge info for veSDL holders
    calls = []

    for chain_id in SIDECHAIN_CHAIN_IDS:
        for veSDL_holder in current_veSDL_holders:
            calls.append([
                root_oracle.address,
                root_oracle.push.encode_input(chain_id, veSDL_holder)
            ])

    # Use Multicall3 to push balances to the sidechains
    multicall3 = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "Multicall3")

    multicall3.aggregate(calls, {"from": deployer_EOA})

    for tx in history:
        tx.info()
    return
