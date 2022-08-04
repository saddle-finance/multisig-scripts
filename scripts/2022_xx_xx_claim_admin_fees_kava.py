from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, SWAP_ABI, KAVA_POOL_ADDRESS_TO_POOL_NAME
from ape_safe import ApeSafe
from brownie import accounts, network
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "MAINNET"


def main():
    """This script claims admin fees from all Kava pools"""

    print(f"You are using the '{network.show_active()}' network")
    assert(network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    # Run any pending transactions before simulating any more transactions
    multisig.preview_pending()

    pools = {
        "0xA500b0e1360462eF777804BCAe6CE2BfB524dD2e",  # Kava 3Pool
    }

    # execute txs for claiming admin fees
    # TODO: print out exact fee amounts that are claimable, before claiming
    for pool_address in pools:
        print(
            f"Claiming admin fees from {KAVA_POOL_ADDRESS_TO_POOL_NAME[pool_address]}")
        pool = Contract.from_abi("Swap", pool_address, SWAP_ABI)
        pool.withdrawAdminFees()

    # combine history into multisend txn
    # TODO: set 'safe_nonce'
    safe_tx = multisig.multisend_from_receipts()
    safe_nonce = 0

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    multisig.preview(safe_tx)
    confirm_posting_transaction(multisig, safe_tx)
