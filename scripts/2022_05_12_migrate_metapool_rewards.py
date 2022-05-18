from helpers import CHAIN_IDS, LP_MIGRATOR_ADDRESSES, MINICHEF_ADDRESSES, MULTISIG_ADDRESSES, DISPERSE_APP_ADDRESSES
from ape_safe import ApeSafe
from brownie import accounts, network, web3, utils
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

    # Add new rewards for the meta pools
    # tbtc v3 meta pool lp token
    minichef.add(25, "0xA2E81Eb93F0F9814ae9A3bea2D2A63408f2709C1",
                 "0x0000000000000000000000000000000000000000")
    # susd v3 meta pool lp token
    minichef.add(50, "0x444F94460a641429CDa4e38E02E51642Cc38276A",
                 "0x0000000000000000000000000000000000000000")
    # wcusd v3 meta pool lp token
    minichef.add(2, "0x0dB8b09c13FE21913faF463274cE8e0a51719f16",
                 "0x0000000000000000000000000000000000000000")

    # Add new migration data for the meta pools
    # Users are able to use the migrator contract to send in their old LP token for the new ones.

    # tbtc metapool migration data
    migrator.addMigrationData(
        # oldPoolAddress
        "0xA0b4a2667dD60d5CdD7EcFF1084F0CeB8dD84326",
        [
            # newPoolAddress
            "0xfa9ED0309Bf79Eb84C847819F0B3CB84F6d351Af",
            # oldPoolLPTokenAddress
            "0x3f2f811605bC6D701c3Ad6E501be13461c560320",
            # newPoolLPTokenAddress
            "0xA2E81Eb93F0F9814ae9A3bea2D2A63408f2709C1",
            # tokens
            [
                "0x18084fbA666a33d37592fA2633fD49a74DD93a88",
                "0xF32E91464ca18fc156aB97a697D6f8ae66Cd21a3"
            ]
        ],
        # shouldOverwrite
        False
    )

    # susd metapool migration data
    migrator.addMigrationData(
        "0x824dcD7b044D60df2e89B1bB888e66D8BCf41491",
        [
            "0x4568727f50c7246ded8C39214Ed6FF3c157f080D",
            "0xb6214a9d18f5Bf34A23a355114A03bE4f7D804fa",
            "0x444F94460a641429CDa4e38E02E51642Cc38276A",
            [
                "0x57Ab1ec28D129707052df4dF418D58a2D46d5f51",
                "0x5f86558387293b6009d7896A61fcc86C17808D62"
            ]
        ],
        False
    )

    # wcusd metapool migration data
    migrator.addMigrationData(
        "0xc02D481B52Ae04Ebc76a8882441cfAED45eb8342",
        [
            "0xB62222B941e9B652BE3632EEa062cb0ff66b1d1c",
            "0x5F7872490a9B405946376dd40fCbDeF521F13e3f",
            "0x0dB8b09c13FE21913faF463274cE8e0a51719f16",
            [
                "0xad3e3fc59dff318beceaab7d00eb4f68b1ecf195",
                "0x5f86558387293b6009d7896A61fcc86C17808D62"
            ]
        ],
        False
    )

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()

    # sign with private key
    safe_tx.sign(deployer.private_key)
    # multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
