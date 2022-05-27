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
    poolLength = minichef.poolLength()
    newPoolIndex = poolLength + 1
    minichef.massUpdatePools(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])

    # Static
    currentSDLPerSecond = minichef.saddlePerSecond()
    frax3poolSDLPerSecond = (2_000_000 * 1e18) / (2 * 4 * 7 * 24 * 60 * 60)
    totalAlloc = minichef.totalAllocPoint()

    # Calculation
    newSDLPerSecond = currentSDLPerSecond + frax3poolSDLPerSecond
    fraxAllocationRate = frax3poolSDLPerSecond / newSDLPerSecond
    fraxAlloc = round((totalAlloc * fraxAllocationRate) / (1 - fraxAllocationRate))
    print("fraxAlloc: ", fraxAlloc)
    print("newPoolIndex: ", newPoolIndex)

    # State Change
    minichef.setSaddlePerSecond(newSDLPerSecond)
    minichef.add(
        newPoolIndex,
        "0x0785aDDf5F7334aDB7ec40cD785EBF39bfD91520",
        "0x0000000000000000000000000000000000000000",
    )
    minichef.set(
        newPoolIndex, fraxAlloc, "0x0000000000000000000000000000000000000000", False
    )
    minichef.updatePool(newPoolIndex)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 34

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
