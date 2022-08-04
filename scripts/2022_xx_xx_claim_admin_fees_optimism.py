from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, SWAP_ABI, OPTIMISM_POOL_ADDRESS_TO_POOL_NAME
from ape_safe import ApeSafe
from brownie import accounts, network
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "MAINNET"


def main():
    """This script claims admin fees from all Optimism pools"""

    print(f"You are using the '{network.show_active()}' network")
    assert(network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    # Run any pending transactions before simulating any more transactions
    multisig.preview_pending()

    pools = {
        "0x5847f8177221268d279Cf377D0E01aB3FD993628",  # Opt USD Pool
        "0xF6C2e0aDc659007Ba7c48446F5A4e4E94dfe08b5",  # Opt FRAXBP Pool
        "0x250184dDDEC6d38E28ac12B481c9016867226E9D",  # Opt FRAXBP/sUSD Metapool
        "0xa9a84238098Dc3d1529228E6c74dBE7EbdF117a5",  # Opt FRAXBP/USDT Metapool
        "0xc55E8C79e5A6c3216D4023769559D06fa9A7732e",  # Opt USD/FRAX Metapool
    }

    # execute txs for claiming admin fees
    # TODO: print out exact fee amounts that are claimable, before claiming
    for pool_address in pools:
        print(
            f"Claiming admin fees from {OPTIMISM_POOL_ADDRESS_TO_POOL_NAME[pool_address]}")
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
