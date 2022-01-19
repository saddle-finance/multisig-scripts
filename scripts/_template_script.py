from helpers import ChainId, MultisigAddresses
from ape_safe import ApeSafe
import os

def main():
    """DESCRIPTION OF WHAT THIS SCRIPT DOES"""
    multisig = ApeSafe(MultisigAddresses[ChainId.MAINNET])

    """build txn here"""

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()

    # sign with private key
    safe_tx.sign(os.environ.get("DEPLOYER_PRIVATE_KEY"))
    multisig.preview(safe_tx)

    # post to network
    multisig.post_transaction(safe_tx)

if __name__ == "__main__":
    main()
