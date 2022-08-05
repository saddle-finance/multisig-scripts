from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, OWNERS
from ape_safe import ApeSafe
from brownie import accounts, network, Contract

from scripts.utils import confirm_posting_transaction


def main():
    """Update a vesting contract's ownership to company multisig"""

    print(f"You are using the '{network.show_active()}' network")

    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    safe_contract = multisig.contract(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    Kain_Warwick = "0x5b97680e165b4dbf5c45f4ff4241e85f418c66c2"

    # prev owner(pointer), old owner, new owner
    safe_contract.swapOwner(OWNERS[4], Kain_Warwick, OWNERS[5])

    # new owner, threshold
    safe_contract.addOwnerWithThreshold(OWNERS[0], 3)
    assert safe_contract.getOwners() == OWNERS

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 54

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
