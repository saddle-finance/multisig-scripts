from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, VESTING_ABI
from ape_safe import ApeSafe
from brownie import accounts, network, Contract

from scripts.utils import confirm_posting_transaction


def main():
    """Update a vesting contract's ownership to company multisig"""

    print(f"You are using the '{network.show_active()}' network")

    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    vesting_contract = Contract.from_abi(
        "Vesting",
        "0x85f99b73d0edd9cDb3462C94Ebe4c5758684BDf1",
        VESTING_ABI,
        multisig.account,
    )
    vesting_contract.changeBeneficiary("0x4ba5B41c4378966f08E3E4F7dd80840191D54C69")

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 52

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
