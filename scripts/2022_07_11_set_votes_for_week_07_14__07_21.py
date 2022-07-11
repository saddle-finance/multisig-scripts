from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, GAUGE_CONTROLLER_ADDRESS
from ape_safe import ApeSafe
from brownie import Contract, accounts, network

from scripts.utils import confirm_posting_transaction


def main():
    """Set Gauge weights for week 07_14_2022 -> 07_21_2022 from results of snapshot vote"""

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    # Run any pending transactions before simulating any more transactions
    multisig.preview_pending()

    gauge_controller = multisig.contract(GAUGE_CONTROLLER_ADDRESS[CHAIN_IDS["MAINNET"]])

    gauge_to_relative_weight_dict = {
        "0xB2Ac3382dA625eb41Fc803b57743f941a484e2a6": 5357,  # FRAXBP Pool
        "0xc64F8A9fe7BabecA66D3997C9d15558BF4817bE3": 2991,  # Sushi SDL/WETH
        "0x104F44551386d603217450822443456229F73aE4": 825,  # sUSDFRAX Metapool
        "0x6EC5DD7D8E396973588f0dEFD79dCA04F844d57C": 206,  # FRAXUSDT Metapool
        "0x953693DCB2E9DDC0c1398C1b540b81b63ceA5e16": 206,  # alUSDFRAX Metapool
        "0x13Ba45c2B686c6db7C2E28BD3a9E8EDd24B894eD": 206,  # Frax 3Pool
        "0x702c1b8Ec3A77009D5898e18DA8F8959B6dF2093": 206,  # Saddle D4Pool
        "0x17Bde8EBf1E9FDA85b9Bd1a104266b394E9Db33e": 2,  # Saddle s/w/renBTC Pool
        "0x3dC88ee38db8C7b6DCEB447E4348e51bd87ced93": 0,  # WCUSD Metapool
        "0x7B2025Bf8c5ee8Baad9da8C3E3Ee45E96ed8b8EA": 0,  # Saddle USD Pool
        "0x2683190e31e8ce47467c98ff1DBc018aCDD43C2f": 0,  # Saddle sUSD Metapool
        "0x8B701e9B3a1887fE9b0C7936a8233b39408e69f6": 0,  # Saddle alETH Pool
        "0xB79B4fCF7cB4A1c4064Ff5b48F71A331880ab53a": 0,  # Saddle TBTC Metapool
        "0x50d745c2a2918A47A363A2d32becd6BBC1A53ece": 0,  # Saddle USX Pool
    }

    gauge_abi = [
        {
            "stateMutability": "view",
            "type": "function",
            "name": "name",
            "inputs": [],
            "outputs": [{"name": "", "type": "string"}],
        }
    ]

    # print out details first to confirm the we are setting gauge weights correctly
    # separate printing and executing into 2 loops to avoid printing inbetween transaction logs
    for gauge in gauge_to_relative_weight_dict:
        gauge_contract = Contract.from_abi("LiqGaugeV5", gauge, gauge_abi)
        gauge_name = gauge_contract.name()
        print(
            f"Setting {gauge_name}'s weight to {gauge_to_relative_weight_dict[gauge]}"
        )

    # execute txs for setting gauge weights
    for gauge in gauge_to_relative_weight_dict:
        gauge_controller.change_gauge_weight(
            gauge, gauge_to_relative_weight_dict[gauge]
        )

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 44

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx, True, False, False)

    confirm_posting_transaction(multisig, safe_tx)
