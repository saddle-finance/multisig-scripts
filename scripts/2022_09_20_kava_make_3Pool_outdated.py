import math
import json
from helpers import (
    CHAIN_IDS,
    POOL_REGISTRY_ABI,
    SWAP_FLASH_LOAN_ABI
)

# from ape_safe import ApeSafe
from brownie import ZERO_ADDRESS, Contract, accounts, network

# from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "KAVA"


def main():
    """
    - Sets the `isRemoved` flag on the registry for 3Pool pool on Kava
    - Pauses 3Pool on Kava

    """

    KAVA_POOL_REGISTRY_ADDRESS = "0x9DC37020f261758871104f9D8b87e575Ee45Bc5a"
    KAVA_3POOL_ADDRESS = "0xA500b0e1360462eF777804BCAe6CE2BfB524dD2e"

    print(f"You are using the '{network.show_active()}' network")
    assert (
        network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    ), f"Not on {TARGET_NETWORK} network"

    deployer = accounts.load("deployer")  # prompts for password

    # contracts
    pool_registry = Contract.from_abi(
        "PoolRegistry", KAVA_POOL_REGISTRY_ADDRESS, POOL_REGISTRY_ABI
    )
    pool = Contract.from_abi(
        "3Pool", KAVA_3POOL_ADDRESS, SWAP_FLASH_LOAN_ABI
    )

    # check if `isRemoved` flag is set to False beforehand
    assert pool_registry.getPoolData(KAVA_3POOL_ADDRESS)[10] == False

    # set `isRemoved` flag to True on PoolRegistry
    pool_registry.removePool(KAVA_3POOL_ADDRESS, {"from": deployer})

    # check if `isRemoved` flag is set to True
    assert pool_registry.getPoolData(KAVA_3POOL_ADDRESS)[10] == True

    # pause 3pool
    pool.pause({"from": deployer})

    # check if pool is paused
    assert pool_registry.getPaused(KAVA_3POOL_ADDRESS) == True
