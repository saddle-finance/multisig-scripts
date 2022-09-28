import math

from ape_safe import ApeSafe
from brownie import Contract, accounts, network
from helpers import CHAIN_IDS, DEPLOYER_ADDRESS, GAUGE_ABI, GAUGE_CONTROLLER_ADDRESS, MINICHEF_ADDRESSES, MULTISIG_ADDRESSES, OPTIMISM_STANDARD_BRIDGE, SDL_ADDRESSES, SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS, SDL_MINTER_ADDRESS

from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():
    """
    Send 1MM SDL to deployer account for manual bridging to Arbitrum for a token swap with L2DAO
    Vote: https://snapshot.org/#/saddlefinance.eth/proposal/0xb2ccd63569c46f58b00ad9b3dda46ce6a5bd5dc7a5009854e7181d2f14325062
    """

    print(f"You are using the '{network.show_active()}' network")
    assert network.chain.id == CHAIN_IDS[TARGET_NETWORK], f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    sdl = multisig.contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    amount_to_transfer = 1_000_000 * 1e18

    current_deployer_balance = sdl.balanceOf(DEPLOYER_ADDRESS)

    sdl.transfer(DEPLOYER_ADDRESS, amount_to_transfer)

    new_deployer_balance = sdl.balanceOf(DEPLOYER_ADDRESS)
    assert (new_deployer_balance - current_deployer_balance == amount_to_transfer), "did not transfer correct amount"

    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 66

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
