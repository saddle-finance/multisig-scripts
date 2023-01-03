from datetime import datetime, timedelta

from ape_safe import ApeSafe
from brownie import accounts, network

from helpers import CHAIN_IDS, MULTISIG_ADDRESSES
from scripts.utils import confirm_posting_transaction, fetch_current_nonce


def main():
    """Ramps A param for select pools as per SIP-46:
    https://snapshot.org/#/saddlefinance.eth/proposal/0xe894884108944bf43cd403b9cbc3493c879f601da37ae59f9b27dd52282d8d86
    """
    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer")
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    pools_to_future_a = {
        "0x13Cc34Aa8037f722405285AD2C82FE570bfa2bdc": 1500,  # SaddleFraxBPPool
        "0x69baA0d7c2e864b74173922Ca069Ac79d3be1556": 400,  # SaddleFraxsUSDPool
        "0xC765Cd3d015626244AD63B5FB63a97c5634643b9": 400,  # SaddleFraxUSDTPool
    }
    now = datetime.now()
    # @dev delta must be min 14 days. Add a week buffer for multisig to sign.
    now_plus_21_days = now + timedelta(days=21)
    now_plus_21_days_seconds = int(
        (now_plus_21_days - datetime(1970, 1, 1)).total_seconds()
    )
    for pool_addr, A in pools_to_future_a.items():
        contract = multisig.contract(pool_addr)
        contract.rampA(A, now_plus_21_days_seconds)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.current_nonce = fetch_current_nonce(multisig)
    safe_tx.safe_nonce = 79

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx, False)

    confirm_posting_transaction(multisig, safe_tx)
