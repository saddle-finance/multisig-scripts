from ape_safe import ApeSafe
from brownie import accounts, network
from helpers import (ALCX_ADDRESSES, CHAIN_IDS, HEDGEY_OTC, MULTISIG_ADDRESSES,
                     SDL_ADDRESSES)

from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():
    """
    Set Gauge weights for week 10_20_2022 -> 10_27_2022 from results of snapshot vote
    Vote: https://snapshot.org/#/saddlefinance.eth/proposal/0x84163f92132845811159a020c4a591c009323e4f62ca8d80e02d73149be12caf
    """

    print(f"You are using the '{network.show_active()}' network")
    assert network.chain.id == CHAIN_IDS[TARGET_NETWORK], f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    hedgey_otc = multisig.contract(HEDGEY_OTC[CHAIN_IDS[TARGET_NETWORK]])
    sdl = multisig.contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    # Approve SDL to be used by hedgey OTC contract
    sdl.approve(hedgey_otc.address, 1_500_000e18)
    hedgey_otc.create(
        sdl.address,
        ALCX_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        1_500_000e18,  # 1.5M SDL
        1_500_000e18,  # min
        0.0008 * 1e18,  # price SDL per ALCX
        1667188800,  # maturity date 	Mon Oct 31 2022 04:00:00 GMT+0000
        0,  # unlock date, 0 to enable immediate unlock
        "0x9e2b6378ee8ad2A4A95Fe481d63CAba8FB0EBBF9"  # alchemix dev multisig
    )

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 70

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
