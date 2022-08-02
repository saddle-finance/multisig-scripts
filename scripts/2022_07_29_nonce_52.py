import math
from helpers import CHAIN_IDS, GAUGE_CONTROLLER_ADDRESS, MINICHEF_ADDRESSES, MULTISIG_ADDRESSES, SDL_ADDRESSES, SIDECHAIN_TOTAL_EMISSION_RATE, VESTING_ABI
from ape_safe import ApeSafe
from brownie import ZERO_ADDRESS, Contract, accounts, network

from scripts.utils import confirm_posting_transaction


def main():
    """
    Groups 3 scripts together in nonce 52.
    1. Update a vesting contract's ownership to company multisig
    2. Adds new FRAXUSX-metapool gauge to controller
    3. Sends SDL to deployer account for Optimism minichef
    """
    TARGET_NETWORK = "MAINNET"

    print(f"You are using the '{network.show_active()}' network")
    assert(network.chain.id ==
           CHAIN_IDS[TARGET_NETWORK]), f"Not on {TARGET_NETWORK} network"
    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    sdl = multisig.contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    ##### 1. Update a vesting contract's ownership to company multisig #####
    
    vesting_contract = Contract.from_abi(
        "Vesting",
        "0x85f99b73d0edd9cDb3462C94Ebe4c5758684BDf1",
        VESTING_ABI,
        multisig.account,
    )
    vesting_contract.changeBeneficiary("0x4ba5B41c4378966f08E3E4F7dd80840191D54C69")

    ##### 2. Adds new FRAXUSX-metapool gauge to controller #####

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

    ##### 3. Sends SDL to deployer account for Optimism minichef #####

    seconds_in_week = 60 * 60 * 24 * 7
    amount_to_send = math.floor(
        SIDECHAIN_TOTAL_EMISSION_RATE * seconds_in_week * 4998 / 10000)

    sdl.transfer(deployer.address, amount_to_send)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 52

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
