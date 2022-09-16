from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, SDL_ADDRESSES
from ape_safe import ApeSafe
from brownie import accounts, network
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "MAINNET"
def main():
    """Send 1.5m SDL to address for 'marketing'"""

    print(f"You are using the '{network.show_active()}' network")
    assert(network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    # Run any pending transactions before simulating any more transactions
    multisig.preview_pending()

    sdl_contract = multisig.contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    
    # SIP38: Send 1.5M SDL to MEXC for marketing
    sdl_contract.transfer("0xae8f210fd506d0b2b11cee452d42087b1dac9798", 1_500_000 * 1e18)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_nonce = 62

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key) # prompts for password
    multisig.preview(safe_tx)
    confirm_posting_transaction(multisig, safe_tx)
