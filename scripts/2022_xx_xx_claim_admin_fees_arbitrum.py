from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, SWAP_ABI, ARBITRUM_POOL_ADDRESS_TO_POOL_NAME
from ape_safe import ApeSafe
from brownie import accounts, network
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "MAINNET"


def main():
    """This script claims admin fees from all Arbitrum pools"""

    print(f"You are using the '{network.show_active()}' network")
    assert(network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    # Run any pending transactions before simulating any more transactions
    multisig.preview_pending()

    pools = {
        "0xfeEa4D1BacB0519E8f952460A70719944fe56Ee0",  # Arb USDV2 Pool
        "0x5dD186f8809147F96D3ffC4508F3C82694E58c9c",  # Arb USDS Metapool
        "0x401AFbc31ad2A3Bc0eD8960d63eFcDEA749b4849",  # Arb FRAXBP Pool
        "0xa5bD85ed9fA27ba23BfB702989e7218E44fd4706",  # Arb FRAXBP/USDS Metapool
        "0xf8504e92428d65E56e495684A38f679C1B1DC30b",  # Arb FRAXBP/USDT Metapool
    }

    # execute txs for claiming admin fees
    # TODO: print out exact fee amounts that are claimable, before claiming
    for pool_address in pools:
        print(
            f"Claiming admin fees from {ARBITRUM_POOL_ADDRESS_TO_POOL_NAME[pool_address]}")
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
