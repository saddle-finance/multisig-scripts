from ape_safe import ApeSafe
from brownie import Contract, accounts, network

from helpers import (
    CHAIN_IDS,
    MULTISIG_ADDRESSES,
    SWAP_FLASH_LOAN_ABI,
    META_SWAP_ABI
)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():
    """
    Pause pools containing renBTC:
    - BTCv2 pool
    - tBTCv2-BTCv2_v3 meta pool
    """

    print(f"You are using the '{network.show_active()}' network")
    assert network.chain.id == CHAIN_IDS[TARGET_NETWORK], f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url="https://safe-transaction-mainnet.safe.global",
    )

    pools_to_pause = [
        "0xfa9ED0309Bf79Eb84C847819F0B3CB84F6d351Af",   # tBTCv2-BTCv2_v3
        "0xdf3309771d2BF82cb2B6C56F9f5365C8bD97c4f2",   # BTCv2
    ]

    # tBTCv2-BTCv2_v3 metapool
    tbtc_metapool = Contract.from_abi(
        "tBTCv2-BTCv2_v3", pools_to_pause[0], META_SWAP_ABI
    )

    #  BTCv2 pool
    btcv2_pool = Contract.from_abi(
        "BTCv2", pools_to_pause[1], SWAP_FLASH_LOAN_ABI
    )

    assert tbtc_metapool.paused() == False
    assert btcv2_pool.paused() == False

    # pause pools
    tbtc_metapool.pause({"from": multisig.address})
    btcv2_pool.pause({"from": multisig.address})

    assert tbtc_metapool.paused()
    assert btcv2_pool.paused()

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 76

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
