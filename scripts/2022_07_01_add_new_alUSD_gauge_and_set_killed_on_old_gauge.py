from helpers import CHAIN_IDS, MULTISIG_ADDRESSES
from ape_safe import ApeSafe
from brownie import accounts, network

from scripts.utils import confirm_posting_transaction

def main():
    """Adds new alUSD gauge and sets 'is_killed' on old alUSD gauge"""

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer") # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])
    
    OLD_ALUSD_ETH_MAINNET_METAPOOL_GAUGE_ADDRESS = "0x3b35a3f9163cf5733837c5b51b1df493c340f8e3"

    gauge_controller = multisig.contract(GAUGE_CONTROLLER_ADDRESS[CHAIN_IDS["MAINNET"]])
    old_alusd_gauge = multisig.contract(OLD_ALUSD_ETH_MAINNET_METAPOOL_GAUGE_ADDRESS)

    # new alUSD gauge to add to gauge controller 
    # TODO: insert new gauge's address
    gauge_data = {
        "SaddleFRAXalUSDMetaPoolGauge" : 
            {"address" : "0x0",
             "type" : 0,
             "weight" : 0 },
    }

    # add gauge to gauge controller
    gauge_controller.add_gauge(
        gauge_data["SaddleFRAXalUSDMetaPoolGauge"]["address"],
        gauge_data["SaddleFRAXalUSDMetaPoolGauge"]["type"],
        gauge_data["SaddleFRAXalUSDMetaPoolGauge"]["weight"]
    )

    # set 'is_killed' on old alUSD gauge
    old_alusd_gauge.set_killed(True)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 43

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
