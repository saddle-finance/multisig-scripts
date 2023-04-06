import csv

from ape_safe import ApeSafe
from brownie import ZERO_ADDRESS, Contract, Wei, accounts, history, network
from brownie.network import max_fee, priority_fee

from helpers import (CHAIN_IDS, MULTISIG_ADDRESSES,
                     get_contract_from_deployment,
                     get_contracts_from_deployment)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "ARBITRUM"


def main():
    """
    Calls mint() on ChildGaugeFactory with all ChildGauge addresses
    """
    print(f"You are using the '{network.show_active()}' network")
    assert (
        network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    ), f"Not on {TARGET_NETWORK} network"

    # deployer_EOA = accounts.load("deployer")
    priority_fee("auto")
    # max_fee(15000000000)

    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
    )

    pools = [
        "0xa5bd85ed9fa27ba23bfb702989e7218e44fd4706",
        "0x5dd186f8809147f96d3ffc4508f3c82694e58c9c",
    ]

    for pool in pools:
        poolContract = multisig.get_contract(pool)
        poolContract.pause()

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 23

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx, False)

    confirm_posting_transaction(multisig, safe_tx)
