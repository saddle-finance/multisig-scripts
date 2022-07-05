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
    # TODO: set nonce 
    safe_tx = multisig.multisend_from_receipts()
    safe_nonce = 0
    
    # check if nonce is invalid or already in use
    current_nonce = multisig.contract(multisig.address).nonce()
    pending_nonce = multisig.pending_nonce()
    
    if safe_nonce < current_nonce:
        print(f"Error: Your nonce ({safe_nonce}) is already used. " + 
            f"Please use a nonce greater equal {current_nonce}.")
        return  
    if safe_nonce < pending_nonce:
        if (input(f"There is already a pending transaction at nonce {safe_nonce}. " + 
            "Are you sure you want to use duplicate nonce for this submission? [y/N]")) == "N":
            return
    elif safe_nonce > pending_nonce:
        if (input(f"Your nonce ({safe_nonce}) is greater than current pending nonce " + 
            f"({pending_nonce}). Tx won't execute until intermediate nonces have " + 
            "been used. Are you sure you want to post submission? [y/N]")) == "N":
            return

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)
    confirm_posting_transaction(multisig, safe_tx)