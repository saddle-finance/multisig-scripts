import math

from ape_safe import ApeSafe
from brownie import Contract, accounts, network
from helpers import CHAIN_IDS, DEPLOYER_ADDRESS, GAUGE_ABI, GAUGE_CONTROLLER_ADDRESS, HEDGEY_OTC, MINICHEF_ADDRESSES, MULTISIG_ADDRESSES, OPTIMISM_STANDARD_BRIDGE, SDL_ADDRESSES, SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS, SDL_MINTER_ADDRESS

from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "ARBITRUM"

def main():
    """
    Set Gauge weights for week 09_29_2022 -> 10_06_2022 from results of snapshot vote
    Vote: https://snapshot.org/#/saddlefinance.eth/proposal/0xe72e59f14f4b58777587dbba098aa8ade99f265d4ed34c75d6b83d97bc705998
    """

    print(f"You are using the '{network.show_active()}' network")
    assert network.chain.id == CHAIN_IDS[TARGET_NETWORK], f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    sdl = multisig.contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    hedgey_otc = multisig.contract(HEDGEY_OTC[CHAIN_IDS[TARGET_NETWORK]])

    token_swap_amount = 1_000_000 * 1e18

    # buy L2DAO token from Hedgey OTC
    sdl.approve(hedgey_otc.address, token_swap_amount)
    hedgey_otc.buy(12, 3136561000000000000000000)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 11

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
