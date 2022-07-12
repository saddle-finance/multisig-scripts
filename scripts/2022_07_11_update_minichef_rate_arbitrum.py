from helpers import CHAIN_IDS, MINICHEF_ADDRESSES, MULTISIG_ADDRESSES
from ape_safe import ApeSafe
from brownie import ZERO_ADDRESS, Contract, accounts, network

from scripts.utils import confirm_posting_transaction, fetch_current_nonce


def main():
    """
    Updates Arbitrum pool and minichef parameters
    Existing pools' admin fees are updated to 50% of the total swap fee
    Minichef rate and allocpoint are updated to match Snapshot results
    """

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["ARBITRUM"]])

    minichef = multisig.contract(MINICHEF_ADDRESSES[CHAIN_IDS["ARBITRUM"]])

    pool_addrs = [
        "0xBea9F78090bDB9e662d8CB301A00ad09A5b756e9",  # arbUSDPool
        "0xfeEa4D1BacB0519E8f952460A70719944fe56Ee0",  # arbUSDPoolv2
        "0x5dD186f8809147F96D3ffC4508F3C82694E58c9c",  # usdsMetaPool
    ]

    for pool_addr in pool_addrs:
        pool = multisig.contract(pool_addr)
        pool.setAdminFee("5000000000")  # .5 x 10**10, set to 50% of swap fee
        # check that admin fee was set
        assert(pool.swapStorage()[5] == "5000000000")

    # 50.21% for Arbitrum: FraxBP
    minichef.add(
        5021, "0x896935b02d3cbeb152192774e4f1991bb1d2ed3f", ZERO_ADDRESS)
    # 49.79% for Arbitrum: FraxBP-USDT
    minichef.add(
        4979, "0x166680852ae9dec3d63374c5ebf89e974448bfe9", ZERO_ADDRESS)

    # Remove SDL rewards for nUSD pool and USDs meta pool
    minichef.set(1, 0, ZERO_ADDRESS, False)
    minichef.set(2, 0, ZERO_ADDRESS, False)

    # 59,300 SDL/day
    new_rate = 686342592592592592
    minichef.setSaddlePerSecond(new_rate)

    assert(minichef.totalAllocPoint() == 10000)
    assert(minichef.saddlePerSecond() == new_rate)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.current_nonce = fetch_current_nonce(multisig)
    safe_tx.safe_nonce = 3

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx, False)

    confirm_posting_transaction(multisig, safe_tx)
