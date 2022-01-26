from helpers import ChainId, MultisigAddresses
from ape_safe import ApeSafe
from brownie import accounts, network
import click

from scripts.utils import confirm_posting_transaction

def main():
    """Turns on admin fee for non-paused pools"""

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer")
    multisig = ApeSafe(MultisigAddresses[ChainId["MAINNET"]])

    pools = [
        "0xa6018520EAACC06C30fF2e1B3ee2c7c22e64196a", # SaddleALETHPool
        "0x4f6A43Ad7cba042606dECaCA730d4CE0A57ac62e", # SaddleBTCPool
        "0xdf3309771d2BF82cb2B6C56F9f5365C8bD97c4f2", # SaddleBTCPoolV2
        "0xC69DDcd4DFeF25D8a793241834d4cc4b3668EAD6", # SaddleD4Pool
        # "0x0C8BAe14c9f9BF2c953997C881BEfaC7729FD314", # SaddleSUSDMetaPool (paused)
        "0x824dcD7b044D60df2e89B1bB888e66D8BCf41491", # SaddleSUSDMetaPoolUpdated
        # "0xf74ebe6e5586275dc4CeD78F5DBEF31B1EfbE7a5", # SaddleTBTCMetaPool (paused)
        "0xA0b4a2667dD60d5CdD7EcFF1084F0CeB8dD84326", # SaddleTBTCMetaPoolUpdated
        "0x3911F80530595fBd01Ab1516Ab61255d75AEb066", # SaddleUSDPool
        "0xaCb83E0633d6605c5001e2Ab59EF3C745547C8C7", # SaddleUSDPoolV2
        # "0xdec2157831D6ABC3Ec328291119cc91B337272b5", # SaddleVETH2Pool (paused)
        # "0x3F1d224557afA4365155ea77cE4BC32D5Dae2174", # SaddleWCUSDMetaPool (paused)
        "0xc02D481B52Ae04Ebc76a8882441cfAED45eb8342", # SaddleWCUSDMetaPoolUpdated
    ]

    for pool_addr in pools:
        contract = multisig.contract(pool_addr)
        contract.setAdminFee("5000000000") # .5 x 10**10

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()

    # sign with private key
    safe_tx.safe_nonce = 19
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx, False)

    confirm_posting_transaction(multisig, safe_tx)
