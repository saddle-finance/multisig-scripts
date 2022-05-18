from helpers import CHAIN_IDS, LP_MIGRATOR_ADDRESSES, MINICHEF_ADDRESSES, MULTISIG_ADDRESSES, DISPERSE_APP_ADDRESSES, SDL_ADDRESSES
from ape_safe import ApeSafe
from brownie import accounts, network, web3, utils
from eth_utils import to_wei

from scripts.utils import confirm_posting_transaction


def main():
    """Remove SimpleRewarder for the paused tbtc meta pool PID in minichef"""

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    minichef = multisig.contract(MINICHEF_ADDRESSES[CHAIN_IDS["MAINNET"]])
    sdl = multisig.contract(SDL_ADDRESSES[CHAIN_IDS["MAINNET"]])

    # Set rewards to oudated pool lp tokens to 0
    # outdated tbtc meta pool
    minichef.set(5, 0, "0x0000000000000000000000000000000000000000", True)
    # top up SDL minichef rewards
    sdl.transfer(MINICHEF_ADDRESSES[CHAIN_IDS["MAINNET"]], 6_250_000 * 1e18)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 33

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
