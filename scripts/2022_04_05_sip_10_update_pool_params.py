from helpers import CHAIN_IDS, MULTISIG_ADDRESSES
from ape_safe import ApeSafe
from datetime import datetime, timedelta
from brownie import accounts, network

from scripts.utils import confirm_posting_transaction


def main():
    """Ramps A param for select pools as per SIP-10"""
    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer")
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    pools_to_future_a = {
        "0xa6018520EAACC06C30fF2e1B3ee2c7c22e64196a": 480,  # SaddleALETHPool
        "0xdf3309771d2BF82cb2B6C56F9f5365C8bD97c4f2": 800,  # SaddleBTCPoolV2
        "0xaCb83E0633d6605c5001e2Ab59EF3C745547C8C7": 800,  # SaddleUSDPoolV2
    }
    now = datetime.now()
    # @dev delta must be min 14 days. Add a couple days buffer for multisig to sign.
    now_plus_17_days = now + timedelta(days=17)
    now_plus_17_days_seconds = int(
        (now_plus_17_days - datetime(1970, 1, 1)).total_seconds()
    )
    for pool_addr, A in pools_to_future_a.items():
        contract = multisig.contract(pool_addr)
        contract.rampA(A, now_plus_17_days_seconds)
        if pool_addr == "0xaCb83E0633d6605c5001e2Ab59EF3C745547C8C7":
            contract.setSwapFee(3e6)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 26

    # sign with private key
    safe_tx.sign(deployer.private_key)
    # multisig.preview(safe_tx) # preview appears to be broken

    confirm_posting_transaction(multisig, safe_tx)
