from helpers import ChainId, MultisigAddresses
from ape_safe import ApeSafe
from brownie import accounts, network
import click

def main():
    """DESCRIPTION OF WHAT THIS SCRIPT DOES"""

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer") # prompts for password
    multisig = ApeSafe(MultisigAddresses[ChainId["MAINNET"]])

    """

    Build your txn here

    """

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()

    # sign with private key
    safe_tx.sign(deployer)
    multisig.preview(safe_tx)

   # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)
    
    # post to network
    should_execute = click.confirm("Execute multisig transaction?")
    while True:
        if should_execute:
            multisig.post_transaction(safe_tx)
            print("Multisig transaction posted to network")
            break
        else:
            should_execute = click.confirm("Execute multisig transaction?")
