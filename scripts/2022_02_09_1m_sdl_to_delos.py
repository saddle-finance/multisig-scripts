from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, SDL_ADDRESSES, DELO_MULTISIG_ADDRESSES
from ape_safe import ApeSafe
from brownie import accounts, network

from scripts.utils import confirm_posting_transaction

def main():
    """Pursuant to SIP-4, send 1M $SDL to Delos multisig"""

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer") # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    delos_multisig = DELO_MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]]
    sdl_contract = multisig.contract(SDL_ADDRESSES[CHAIN_IDS["MAINNET"]])
    receipt = sdl_contract.transfer(delos_multisig, 1_000_000 * 1e18)

     # combine history into multisend txn
    safe_tx = multisig.tx_from_receipt(receipt)
    safe_tx.safe_nonce = 23

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
