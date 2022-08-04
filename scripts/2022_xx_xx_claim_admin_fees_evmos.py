from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, SWAP_ABI, EVMOS_POOL_ADDRESS_TO_POOL_NAME
from ape_safe import ApeSafe
from brownie import accounts, network
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "MAINNET"


def main():
    """This script claims admin fees from all Evmos pools"""

    print(f"You are using the '{network.show_active()}' network")
    assert(network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    # Run any pending transactions before simulating any more transactions
    multisig.preview_pending()

    pools = {
        "0x1275203FB58Fc25bC6963B13C2a1ED1541563aF0",  # Evmos 3Pool
        "0x81272C5c573919eF0C719D6d63317a4629F161da",  # Evmos 4Pool
        "0x7003102c75587E8D29c56124060463Ef319407D0",  # Evmos BTC Pool
        "0x21d4365834B7c61447e142ef6bCf01136cBD01c6",  # Evmos Frax3Pool
        "0xdb5c5A6162115Ce9a188E7D773C4D011F421BbE5",  # Evmos tBTC Metapool
    }

    # execute txs for claiming admin fees
    # TODO: print out exact fee amounts that are claimable, before claiming
    for pool_address in pools:
        print(
            f"Claiming admin fees from {EVMOS_POOL_ADDRESS_TO_POOL_NAME[pool_address]}")
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
