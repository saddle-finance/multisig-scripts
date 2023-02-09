from ape_safe import ApeSafe
from brownie import Contract, accounts, network

from helpers import (
    CHAIN_IDS,
    MULTISIG_ADDRESSES,
    SDL_ADDRESSES,
    SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS,
)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "ARBITRUM"


def main():
    """
    Unpause USDs pools following USDs hack
    """

    print(f"You are using the '{network.show_active()}' network")
    assert network.chain.id == CHAIN_IDS[TARGET_NETWORK], f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url="https://safe-transaction-mainnet.safe.global",
    )

    pools_to_unpause = [
        "0xa5bD85ed9fA27ba23BfB702989e7218E44fd4706",  # FRAXBP/USDs metapool
        "0x5dD186f8809147F96D3ffC4508F3C82694E58c9c"  # Arb USDv2/USDs metapool
    ]

    for pool_address in pools_to_unpause:
        pool = Contract.from_explorer(pool_address)
        pool.unpause()
        assert pool.paused() == False

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 25

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
