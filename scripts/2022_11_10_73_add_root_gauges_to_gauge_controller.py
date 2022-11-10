import math

from ape_safe import ApeSafe
from brownie import ZERO_ADDRESS, Contract, accounts, history, network
from helpers import (CHAIN_IDS, GAUGE_CONTROLLER_ADDRESS, MINICHEF_ADDRESSES,
                     MULTISIG_ADDRESSES, SIDECHAIN_TOTAL_EMISSION_RATE)

from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():
    """
    Adds root gauges to the gauge controller
    """
    print(f"You are using the '{network.show_active()}' network")
    assert (
        network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    ), f"Not on {TARGET_NETWORK} network"

    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
                       "https://safe-transaction-mainnet.safe.global")

    gauge_controller = multisig.contract(
        GAUGE_CONTROLLER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]
    )

    root_gauges = {
        "RootGauge_10_SaddleFRAXBPPoolLPToken": "0x342C6d31494ECe56D9Cabd783aB004593eeA1961",
        "RootGauge_10_SaddleFRAXUSDTMetaPoolLPToken": "0xf0a24069027cB278BFCA485216d79A50F7A18D37",
        "RootGauge_10_SaddleFRAXsUSDMetaPoolLPToken": "0x05D0B419C0186D31584CEB352dF6E860277f86ae",
        "RootGauge_10_SaddleOptFRAXMetaPoolLPToken": "0x69DCBef8c34e41684d3C6D44464F394846c03728",
        "RootGauge_10_SaddleOptUSDPoolLPToken": "0xda7655c90231a6a5720ef6108DE3426d7e870Fd9",
        "RootGauge_10_SaddleUSXFRAXBPMetaPoolLPToken": "0x44F38ee9dF2a051477da758EAfAdbfD5731BBA82",
        "RootGauge_42161_SaddleArbUSDPoolLPToken": "0x989Bf12fDA21C85860075aECE903761D8eDC8434",
        "RootGauge_42161_SaddleArbUSDPoolV2LPToken": "0x6e1af6FB2B4006603c65dD8FC7796Ccff09c86a1",
        "RootGauge_42161_SaddleArbUSDSMetaPoolLPToken": "0xCD15b091CD14E9fd9607E829ce0f7167E7BA53D3",
        "RootGauge_42161_SaddleFRAXBPPoolLPToken": "0xBBcaeA4e732173C0De28397421c17A595372C9CF",
        "RootGauge_42161_SaddleFRAXUSDTMetaPoolLPToken": "0xb306b7E9D895748A2779586C83112035D8223C7F",
        "RootGauge_42161_SaddleFRAXUSDsMetaPoolLPToken": "0x289532cA1DccE36D05e19Af468EC46fc9CB1390E",
        "RootGauge_42161_SaddleUSXFRAXBPMetaPoolLPToken": "0x0A18D5679C5c8b56Da0D87E308DB9EE2db701BaC"
    }

    for name, address in root_gauges.items():
        gauge_controller.add_gauge(address, 0, 0)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 73

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
