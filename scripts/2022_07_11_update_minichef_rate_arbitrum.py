from helpers import CHAIN_IDS, MINICHEF_ADDRESSES, MULTISIG_ADDRESSES, GAUGE_CONTROLLER_ADDRESS, GAUGE_ABI
from ape_safe import ApeSafe
from brownie import ZERO_ADDRESS, Contract, accounts, network

from scripts.utils import confirm_posting_transaction, fetch_current_nonce


def main():
    """Update Arbitrum Minichef's rates and allocpoints"""

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["ARBITRUM"]])

    minichef = multisig.contract(MINICHEF_ADDRESSES[CHAIN_IDS["ARBITRUM"]])

    # 50.21% for Arbitrum: FraxBP
    minichef.add(5021, "0x896935b02d3cbeb152192774e4f1991bb1d2ed3f", ZERO_ADDRESS)
    # 49.79% for Arbitrum: FraxBP-USDT
    minichef.add(4979, "0x166680852ae9dec3d63374c5ebf89e974448bfe9", ZERO_ADDRESS)

    # Remove SDL rewards for nUSD pool and USDs meta pool
    minichef.set(1, 0, ZERO_ADDRESS, False)
    minichef.set(2, 0, ZERO_ADDRESS, False)

    # 59,300 SDL/day
    minichef.setSaddlePerSecond(686342592592592592)

    assert(minichef.totalAllocPoint() == 10000)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.current_nonce = fetch_current_nonce(multisig)
    safe_tx.safe_nonce = 3

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
