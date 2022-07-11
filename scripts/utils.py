import click
from ape_safe import ApeSafe
from gnosis.safe.safe_tx import SafeTx
from brownie import Contract

def fetch_current_nonce(safe: ApeSafe):
    # small abi of safe, only to be able to check nonce
    nonce_abi = [{
        "stateMutability": "view",
        "type": "function",
        "name": "nonce",
        "inputs": [],
        "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
        ]
    }]
    return Contract.from_abi("GnosisSafeProxy", safe.address, nonce_abi).nonce()


def confirm_posting_transaction(safe: ApeSafe, safe_tx: SafeTx):
    safe_nonce = safe_tx.safe_nonce

    current_nonce = safe_tx.current_nonce
    pending_nonce = safe.pending_nonce()
    
    # check if nonce is invalid or already in use
    if safe_nonce == 0:
        if (input("Safe nonce is set to 0. This tx will be executed using pending " + 
            f"nonce at the time of submission. Continue? [y/N]")) == "N":
            return
        else: 
            safe_tx.safe_nonce = None
    elif safe_nonce < current_nonce:
        print(f"Error: Your nonce ({safe_nonce}) is already used. " + 
            f"Please use a nonce greater equal {current_nonce}.")
        return 
    elif safe_nonce < pending_nonce:
        if (input(f"There is already a pending transaction at nonce {safe_nonce}. " + 
            "Are you sure you want to use duplicate nonce for this submission? [y/N]")) == "N":
            return
    elif safe_nonce > pending_nonce:
        if (input(f"Your nonce ({safe_nonce}) is greater than current pending nonce " + 
            f"({pending_nonce}). Tx won't execute until intermediate nonces have " + 
            "been used. Are you sure you want to post submission? [y/N]")) == "N":
            return

    should_post = click.confirm(f"Post this gnosis safe transaction to {safe.address} on {safe.base_url}?")
    while True:
        if should_post:
            safe.post_transaction(safe_tx)
            print("Transaction posted to network")
            break
        else:
            should_post = click.confirm(f"Post this gnosis safe transaction to {safe.address} on {safe.base_url}?")