from helpers import CHAIN_IDS, LP_MIGRATOR_ADDRESSES, MINICHEF_ADDRESSES, MULTISIG_ADDRESSES, DISPERSE_APP_ADDRESSES
from ape_safe import ApeSafe
from brownie import accounts, network, web3
from eth_utils import to_wei

from scripts.utils import confirm_posting_transaction


def main():
    """Change Minichef rewards from old pools to new pools. Add the new pools to the migrator contract."""

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    minichef = multisig.contract(MINICHEF_ADDRESSES[CHAIN_IDS["MAINNET"]])
    migrator = multisig.contract(LP_MIGRATOR_ADDRESSES[CHAIN_IDS["MAINNET"]])

    # Set rewards to oudated pool lp tokens to 0
    # outdated tbtc meta pool
    minichef.set(5, 0, "0x0000000000000000000000000000000000000000", False)
    # outdated susd meta pool
    minichef.set(6, 0, "0x0000000000000000000000000000000000000000", False)
    # outdated wcusd meta pool
    minichef.set(7, 0, "0x0000000000000000000000000000000000000000", False)

    # TODO: update lp token addresses with production addresses
    # Add new rewards for the meta pools
    minichef.add(25, "tbtc meta pool v3 lp token address",
                 "0x0000000000000000000000000000000000000000")
    minichef.add(50, "susd meta pool v3 lp token address",
                 "0x0000000000000000000000000000000000000000")
    minichef.add(2, "wcusd meta pool v3 lp token address",
                 "0x0000000000000000000000000000000000000000")

    migration_data_abi = {
        "MigrationData": {
            "newPoolAddress": "address",
            "oldPoolLPTokenAddress": "address",
            "newPoolLPTokenAddress": "address",
            "tokens": "address[]"
        }
    }

    # TODO: update new pool addresses with production addresses
    # Add new migration data for the meta pools
    # Users are able to use the migrator contract to convert their old LP token to the new ones.
    migrator.addMigrationData("0x824dcD7b044D60df2e89B1bB888e66D8BCf41491", web3.eth.abi.encodeParameter(migration_data_abi, {
        "newPoolAddress": "0x0000000000000000000000000000000000000000",
        "oldPoolLPTokenAddress": "0xb6214a9d18f5Bf34A23a355114A03bE4f7D804fa",
        "newPoolLPTokenAddress": "0x0000000000000000000000000000000000000000",
        "tokens": ["0x57Ab1ec28D129707052df4dF418D58a2D46d5f51", "0x5f86558387293b6009d7896A61fcc86C17808D62"]
    }))
    migrator.addMigrationData("0xA0b4a2667dD60d5CdD7EcFF1084F0CeB8dD84326", web3.eth.abi.encodeParameter(migration_data_abi, {
        "newPoolAddress": "0x0000000000000000000000000000000000000000",
        "oldPoolLPTokenAddress": "0x3f2f811605bC6D701c3Ad6E501be13461c560320",
        "newPoolLPTokenAddress": "0x0000000000000000000000000000000000000000",
        "tokens": ["0x18084fbA666a33d37592fA2633fD49a74DD93a88", "0xF32E91464ca18fc156aB97a697D6f8ae66Cd21a3"]
    }))
    migrator.addMigrationData("0xc02D481B52Ae04Ebc76a8882441cfAED45eb8342", web3.eth.abi.encodeParameter(migration_data_abi, {
        "newPoolAddress": "0x0000000000000000000000000000000000000000",
        "oldPoolLPTokenAddress": "0x5F7872490a9B405946376dd40fCbDeF521F13e3f",
        "newPoolLPTokenAddress": "0x0000000000000000000000000000000000000000",
        "tokens": ["0xad3e3fc59dff318beceaab7d00eb4f68b1ecf195", "0x5f86558387293b6009d7896A61fcc86C17808D62"]
    }))

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
