from brownie import Contract, accounts, history, network

from helpers import CHAIN_IDS, MINICHEF_ADDRESSES, OPS_MULTISIG_ADDRESSES

TARGET_NETWORK = "OPTIMISM"


def main():
    """
    Move the manager roles of below contracts from deployer EOA to 2/3 ops multisig
    * Minichef
    """
    print(f"You are using the '{network.show_active()}' network")
    assert network.chain.id == CHAIN_IDS[TARGET_NETWORK], f"Not on {TARGET_NETWORK}"
    deployer = accounts.load("deployer")
    minichef = Contract(
        MINICHEF_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]], owner=deployer)

    minichef.transferOwnership(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]], True, False)

    for tx in history:
        tx.info()
    return
