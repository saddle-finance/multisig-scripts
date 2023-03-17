from ape_safe import ApeSafe
from brownie import Contract, accounts, network

from helpers import (ALCX_ADDRESSES, CHAIN_IDS, DEPLOYER_ADDRESS, GAUGE_ABI,
                     GAUGE_CONTROLLER_ADDRESS, HEDGEY_OTC, MULTISIG_ADDRESSES,
                     SDL_ADDRESSES, SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():
    """
    Create a token swap with BAO <> SDL on Hedgey OTC for 1_000_000 BAO <> 1_000_000 SDL
    """

    print(f"You are using the '{network.show_active()}' network")
    assert network.chain.id == CHAIN_IDS[TARGET_NETWORK], f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    hedgey_otc = multisig.get_contract(HEDGEY_OTC[CHAIN_IDS[TARGET_NETWORK]])
    sdl = multisig.get_contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    sdl_vesting_contract_proxy = multisig.get_contract(
        SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]
    )

    # BAO token address and multisig
    BAO_ADDRESS = "0xce391315b414d4c7555956120461d21808a69f3a"
    BAO_MULTISIG = "0x3dFc49e5112005179Da613BdE5973229082dAc35"

    # Claim SDL from vesting contract
    sdl_vesting_contract_proxy.release()

    # Approve SDL to be used by hedgey OTC contract
    sdl.approve(hedgey_otc.address, 1_000_000e18)

    # Create deal on Hedgey OTC for 1_000_000 BAO <> 1_000_000 SDL
    hedgey_otc.create(
        sdl.address,
        BAO_ADDRESS,
        1_000_000e18,  # 1M SDL
        1_000_000e18,  # min
        1e18,  # price BAO per SDL
        1679976000,  # maturity date 	Tue Mar 28 2023 04:00:00 GMT+0000
        0,  # unlock date, 0 to enable immediate unlock
        BAO_MULTISIG  # bao dev multisig
    )

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
