from helpers import CHAIN_IDS, MULTISIG_ADDRESSES
from ape_safe import ApeSafe
from brownie import accounts, network
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"

def main():
    """DESCRIPTION OF WHAT THIS SCRIPT DOES"""

    print(f"You are using the '{network.show_active()}' network")
    assert(network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
   
    """
   
    Build your txn here
   
    """

    # combine history into multisend txn
    # TODO: set 'safe_nonce' 
    safe_tx = multisig.multisend_from_receipts()
    safe_nonce = 0
    
    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key) # prompts for password
    multisig.preview(safe_tx)
    confirm_posting_transaction(multisig, safe_tx)