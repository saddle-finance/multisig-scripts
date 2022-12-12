from ape_safe import ApeSafe
from brownie import Contract, accounts, network

from helpers import (CHAIN_IDS, GAUGE_ABI, GAUGE_CONTROLLER_ADDRESS,
                     META_SWAP_ABI, MULTISIG_ADDRESSES, OPS_MULTISIG_ADDRESSES,
                     POOL_REGISTRY_ADDRESSES, SWAP_FLASH_LOAN_ABI, PoolType)
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
    ops_multisig = ApeSafe(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url="https://safe-transaction-mainnet.safe.global",
    )
    gauge_controller = multisig.contract(
        GAUGE_CONTROLLER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]])

    pools_to_pause = [
        "0xfa9ED0309Bf79Eb84C847819F0B3CB84F6d351Af",   # tBTCv2-BTCv2_v3
        "0xdf3309771d2BF82cb2B6C56F9f5365C8bD97c4f2",   # BTCv2
    ]

    gauges_to_remove = [
        "0x17Bde8EBf1E9FDA85b9Bd1a104266b394E9Db33e",  # BTCv2 gauge
        "0xB79B4fCF7cB4A1c4064Ff5b48F71A331880ab53a",  # tBTCv2-BTCv2_v3 gauge
    ]

    gauges_to_add = [
        # "0x",  # BTCBP gauge
        # "0x",  # BTCBP-tBTCv2 gauge
    ]

    for pool_address in pools_to_pause:
        pool = Contract.from_abi("pool", pool_address,
                                 META_SWAP_ABI, multisig.address)
        assert pool.paused() == False
        pool.pause()
        assert pool.paused() == True

    for gauge_address in gauges_to_remove:
        gauge = Contract.from_abi("gauge", gauge_address,
                                  GAUGE_ABI, multisig.address)
        gauge.set_killed(True)
        assert gauge.is_killed() == True
        gauge_controller.change_gauge_weight(gauge_address, 0)
        assert gauge_controller.get_gauge_weight(gauge_address) == 0

    for gauge_address in gauges_to_add:
        gauge = Contract.from_abi("gauge", gauge_address,
                                  GAUGE_ABI, multisig.address)
        tx = gauge_controller.add_gauge(gauge_address, 0)
        assert len(tx.events["NewGauge"]) == 1
        assert (tx.events["NewGauge"][0]["addr"] == gauge_address)

    pool_registry = ops_multisig.contract(
        POOL_REGISTRY_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    pools_to_register = [
        [
            "0x",   # pool address
            PoolType.BTC,  # pool type
            "BTC Base Pool",  # pool registry name (for display)
            "0x",  # target contract address
            "0x",  # meta swap deposit address. 0x0 if not a meta pool
            True,  # is saddle approved pool
            False,  # is removed
            False  # is gaurded
        ],
        [
            "0x",   # pool address
            PoolType.BTC,  # pool type
            "BTCBP-tBTCv2 Meta Pool",  # pool registry name (for display)
            "0x",  # target contract address
            "0x",  # meta swap deposit address. 0x0 if not a meta pool
            True,  # is saddle approved pool
            False,  # is removed
            False  # is gaurded
        ],
    ]

    for pool in pools_to_register:
        pool_registry.addPool(pool)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 76

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    # combine history into multisend txn
    ops_safe_tx = ops_multisig.multisend_from_receipts()
    ops_safe_tx.safe_nonce = 0

    # sign with private key
    ops_safe_tx.sign(accounts.load("deployer").private_key)
    ops_multisig.preview(ops_safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
    confirm_posting_transaction(ops_multisig, ops_safe_tx)
