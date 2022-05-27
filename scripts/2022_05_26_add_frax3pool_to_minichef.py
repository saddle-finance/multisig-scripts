from multiprocessing import pool
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
    pool_length = minichef.poolLength()
    pids = [x for x in range(1, pool_length)]

    # Static
    current_SDL_per_second = minichef.saddlePerSecond()
    frax3pool_SDL_per_second = (2_000_000 * 1e18) / (2 * 4 * 7 * 24 * 60 * 60)
    totalAlloc = minichef.totalAllocPoint()

    # Calculation
    new_SDL_per_second = current_SDL_per_second + frax3pool_SDL_per_second
    frax_allocation_rate = frax3pool_SDL_per_second / new_SDL_per_second
    frax_alloc = round((totalAlloc * frax_allocation_rate) / (1 - frax_allocation_rate))

    # State Change
    minichef.massUpdatePools(pids)
    minichef.setSaddlePerSecond(new_SDL_per_second)
    minichef.add(
        frax_alloc,
        "0x0785aDDf5F7334aDB7ec40cD785EBF39bfD91520",
        "0x0000000000000000000000000000000000000000",
    )

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 34

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
