from helpers import ChainId, MultisigAddresses
from ape_safe import ApeSafe
from brownie import accounts, network

from scripts.utils import confirm_posting_transaction

def main():
    """ADDS DELOS MULTISIG TO SDL APPROVED TRANSFEREES LIST"""

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer") # prompts for password
    multisig = ApeSafe(MultisigAddresses[ChainId["MAINNET"]])

    delos_multisig = "0x03D319a9921474B9cdE1fff1DBaFba778f9eFEb0"
    SDLcontract = multisig.contract("0xf1Dc500FdE233A4055e25e5BbF516372BC4F6871")
    reciept = SDLcontract.addToAllowedList([delos_multisig])

     # combine history into multisend txn
    safe_tx = multisig.tx_from_receipt(reciept)
    safe_tx.safe_nonce = 21
    
    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
