from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, GAUGE_CONTROLLER_ADDRESS
from ape_safe import ApeSafe
from brownie import Contract, accounts, network

from scripts.utils import confirm_posting_transaction


def main():
    """Adds new alUSD gauge and sets 'is_killed' on old alUSD gauge"""

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    gauge_controller = multisig.contract(GAUGE_CONTROLLER_ADDRESS[CHAIN_IDS["MAINNET"]])

    gauge_to_relative_weight_dict = {
        "0xB2Ac3382dA625eb41Fc803b57743f941a484e2a6": 7786,
        "0xc64F8A9fe7BabecA66D3997C9d15558BF4817bE3": 1038,
        "0x104F44551386d603217450822443456229F73aE4": 447,
        "0x953693DCB2E9DDC0c1398C1b540b81b63ceA5e16": 447,
        "0x13Ba45c2B686c6db7C2E28BD3a9E8EDd24B894eD": 94,
        "0x702c1b8Ec3A77009D5898e18DA8F8959B6dF2093": 90,
        "0x6EC5DD7D8E396973588f0dEFD79dCA04F844d57C": 89,
        "0x17Bde8EBf1E9FDA85b9Bd1a104266b394E9Db33e": 6,
        "0x3dC88ee38db8C7b6DCEB447E4348e51bd87ced93": 2,
        "0x7B2025Bf8c5ee8Baad9da8C3E3Ee45E96ed8b8EA": 0,
        "0x2683190e31e8ce47467c98ff1DBc018aCDD43C2f": 0,
        "0x8B701e9B3a1887fE9b0C7936a8233b39408e69f6": 0,
        "0xB79B4fCF7cB4A1c4064Ff5b48F71A331880ab53a": 0,
    }

    for gauge in gauge_to_relative_weight_dict:
        gauge_contract = Contract(gauge)
        gauge_name = gauge_contract.name()
        print(f"Setting {gauge_name}'s weight to {gauge_to_relative_weight_dict[gauge]}")
        gauge_controller.change_gauge_weight(
            gauge, gauge_to_relative_weight_dict[gauge]
        )

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 44

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
