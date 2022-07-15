from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, VESTING_ABI
from ape_safe import ApeSafe
from brownie import accounts, network, Contract
import datetime

from scripts.utils import confirm_posting_transaction, fetch_current_nonce


def main():
    """Release tokens and shift beneficiary for vesting contract of outgoing employee"""

    print(f"You are using the '{network.show_active()}' network")

    if datetime.datetime.now() < datetime.datetime(2022, 7, 15):
        print("Too early to execute, returning")
        return

    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    vesting_contract = Contract.from_abi(
        "Vesting",
        "0x85f99b73d0edd9cDb3462C94Ebe4c5758684BDf1",
        VESTING_ABI,
        multisig.account,
    )
    vesting_contract.release()
    vesting_contract.changeBeneficiary(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
