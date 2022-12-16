from ape_safe import ApeSafe
from brownie import accounts, network

from helpers import (
    CHAIN_IDS,
    DELO_MULTISIG_ADDRESSES,
    MULTISIG_ADDRESSES,
    SDL_ADDRESSES,
)
from scripts.utils import confirm_posting_transaction


def main():
    """
    Pursuant to SIP-45, send 1.5M $SDL to Delos multisig
    SIP-45: https://snapshot.org/#/saddlefinance.eth/proposal/0xca65737dc3c6115e80321e922dfec12f5d738f45f633d8029577b55d4498ace2
    """

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]],
        base_url="https://safe-transaction-mainnet.safe.global",
    )

    delos_multisig = DELO_MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]]
    sdl_contract = multisig.contract(SDL_ADDRESSES[CHAIN_IDS["MAINNET"]])
    sdl_contract.transfer(delos_multisig, 1_500_000 * 1e18)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 77

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
