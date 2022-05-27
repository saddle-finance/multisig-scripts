from helpers import CHAIN_IDS, MINICHEF_ADDRESSES, MULTISIG_ADDRESSES, SDL_ADDRESSES
from ape_safe import ApeSafe
from brownie import accounts, network

from scripts.utils import confirm_posting_transaction


def main():
    """Add SimpleRewarder for T to minichef"""

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    minichef = multisig.contract(MINICHEF_ADDRESSES[CHAIN_IDS["MAINNET"]])
    minichef.massUpdatePools([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
    minichef.setSaddlePerSecond(1635846757684555302)
    minichef.add(
      11,
      "0x0785aDDf5F7334aDB7ec40cD785EBF39bfD91520",
      "0x0000000000000000000000000000000000000000",
    )
    minichef.set(1, 67, "0x0000000000000000000000000000000000000000", False)
    minichef.set(2, 67, "0x0000000000000000000000000000000000000000", False)
    minichef.set(3, 67, "0x0000000000000000000000000000000000000000", False)
    minichef.set(4, 67, "0x0000000000000000000000000000000000000000", False)
    minichef.set(8, 67, "0x0000000000000000000000000000000000000000", False)
    minichef.set(9, 67, "0x0000000000000000000000000000000000000000", False)
    minichef.set(10, 67, "0x0000000000000000000000000000000000000000", False)
    minichef.set(11, 68, "0x0000000000000000000000000000000000000000", False)
    minichef.updatePool(11)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)