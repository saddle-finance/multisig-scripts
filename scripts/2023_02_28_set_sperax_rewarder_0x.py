from helpers import CHAIN_IDS, OPS_MULTISIG_ADDRESSES, MINICHEF_ADDRESSES
from ape_safe import ApeSafe
from brownie import accounts, network, ZERO_ADDRESS
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "ARBITRUM"
def main():
    """DESCRIPTION OF WHAT THIS SCRIPT DOES"""

    print(f"You are using the '{network.show_active()}' network")
    assert(network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    # Run any pending transactions before simulating any more transactions
    multisig.preview_pending()

    minichef = multisig.get_contract(MINICHEF_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    minichef.set(5, 0, ZERO_ADDRESS, True)


    # combine history into multisend txn
    # TODO: set 'safe_nonce'
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 4

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key) # prompts for password
    multisig.preview(safe_tx)
    confirm_posting_transaction(multisig, safe_tx)
