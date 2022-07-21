from helpers import CHAIN_IDS, MULTISIG_ADDRESSES
from ape_safe import ApeSafe
from brownie import accounts, network
from scripts.utils import confirm_posting_transaction

def main():
    """DESCRIPTION OF WHAT THIS SCRIPT DOES"""

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer") # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])
   
    """
   
    Build your txn here
   
    """

    # combine history into multisend txn
    # TODO: set 'safe_nonce' 
    safe_tx = multisig.multisend_from_receipts()
    safe_nonce = 0
    
    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)
    confirm_posting_transaction(multisig, safe_tx)