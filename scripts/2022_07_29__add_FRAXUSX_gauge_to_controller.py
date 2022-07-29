from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, GAUGE_CONTROLLER_ADDRESS
from ape_safe import ApeSafe
from brownie import accounts, network

from scripts.utils import confirm_posting_transaction


def main():
    """Adds new FRAXUSX-metapool gauge to controller"""

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    gauge_controller = multisig.contract(GAUGE_CONTROLLER_ADDRESS[CHAIN_IDS["MAINNET"]])

    gauge_data = {
        "SaddleFRAXUSXMetaPoolGauge": {
            "address": "0x9585a54297beAa83F044866678b13d388D0180bf",
            "type": 0,
            "weight": 0,
        },
    }

    # add gauge to gauge controller
    gauge_controller.add_gauge(
        gauge_data["SaddleFRAXUSXMetaPoolGauge"]["address"],
        gauge_data["SaddleFRAXUSXMetaPoolGauge"]["type"],
        gauge_data["SaddleFRAXUSXMetaPoolGauge"]["weight"],
    )

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 52

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
