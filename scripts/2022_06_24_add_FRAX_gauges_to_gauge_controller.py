from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, GAUGE_CONTROLLER_ADDRESS
from ape_safe import ApeSafe
from brownie import accounts, network

from scripts.utils import confirm_posting_transaction

def main():
    """Add LiqV5 gauges for mainnet FRAXBP basepool and metapools to gauge controller"""

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer") # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    gauge_controller = multisig.contract(GAUGE_CONTROLLER_ADDRESS[CHAIN_IDS["MAINNET"]])
    
    # gauges to add to gauge controller 
    # TODO: insert gauge addresses when we have them deployed
    gauge_data = {
        "SaddleFRAXBPPoolGauge" : 
            {"address" : "0x0",
             "type" : 0,
             "weight" : 0 },
        "SaddleFRAXsUSDMetaPoolGauge" : 
            {"address" : "0x0",
             "type" : 0,
             "weight" : 0 },
        "SaddleFRAXUSDTMetaPoolGauge" : 
            {"address" : "0x0",
             "type" : 0,
             "weight" : 0 },
        "SaddleFRAXalUSDMetaPoolGauge" : 
            {"address" : "0x0",
             "type" : 0,
             "weight" : 0 }
    }

    # add gauges to gauge controller
    gauge_controller.add_gauge(
        gauge_data["SaddleFRAXBPPoolGauge"]["address"],
        gauge_data["SaddleFRAXBPPoolGauge"]["type"],
        gauge_data["SaddleFRAXBPPoolGauge"]["weight"],)
    
    gauge_controller.add_gauge(
        gauge_data["SaddleFRAXsUSDMetaPoolGauge"]["address"],
        gauge_data["SaddleFRAXsUSDMetaPoolGauge"]["type"],
        gauge_data["SaddleFRAXsUSDMetaPoolGauge"]["weight"],)
    
    gauge_controller.add_gauge(
        gauge_data["SaddleFRAXUSDTMetaPoolGauge"]["address"],
        gauge_data["SaddleFRAXUSDTMetaPoolGauge"]["type"],
        gauge_data["SaddleFRAXUSDTMetaPoolGauge"]["weight"],)
    
    gauge_controller.add_gauge(
        gauge_data["SaddleFRAXalUSDMetaPoolGauge"]["address"],
        gauge_data["SaddleFRAXalUSDMetaPoolGauge"]["type"],
        gauge_data["SaddleFRAXalUSDMetaPoolGauge"]["weight"],)   

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
