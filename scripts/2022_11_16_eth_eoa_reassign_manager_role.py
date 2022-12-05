from brownie import Contract, accounts, history, network

from helpers import CHAIN_IDS, OPS_MULTISIG_ADDRESSES

TARGET_NETWORK = "MAINNET"


def main():
    """
    Move the manager roles of below contracts from deployer EOA to 2/3 ops multisig
    * SmartWalletChecker
    """
    print(f"You are using the '{network.show_active()}' network")
    assert network.chain.id == CHAIN_IDS[TARGET_NETWORK], f"Not on {TARGET_NETWORK}"
    deployer = accounts.load("deployer")
    smart_wallet_checker = Contract(
        "0x4C6A2bE3D64048a0624568F91720a8f3884eBfd8", owner=deployer)

    smart_wallet_checker.transferOwnership(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    for tx in history:
        tx.info()
    return
