from ape_safe import ApeSafe
from brownie import accounts, network

from helpers import (CHAIN_IDS, DELO_MULTISIG_ADDRESSES, ENG_EOA_ADDRESS,
                     GNOSIS_SAFE_BASE_URLS, MULTISIG_ADDRESSES, SDL_ADDRESSES,
                     SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():
    """
    Pursuant to SIP-45, send 1.5M $SDL to Delos multisig
    #/saddlefinance.eth/proposal/0xca65737dc3c6115e80321e922dfec12f5d738f45f633d8029577b55d4498ace2
    SIP-45: https://snapshot.org/
    Refill Minichef rewards
    """
    print(f"You are using the '{network.show_active()}' network")
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        GNOSIS_SAFE_BASE_URLS[CHAIN_IDS[TARGET_NETWORK]],
    )

    # Claim SDL from vesting contract
    sdl_vesting_contract_proxy = multisig.contract(
        SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]
    )
    sdl_vesting_contract_proxy.release()

    # Send 1.5M SDL to Delos multisig as per SIP-45
    delos_multisig = DELO_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    sdl_contract = multisig.contract(
        SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    sdl_contract.transfer(delos_multisig, 1_500_000 * 1e18)

    # Send about 1 week worth of minichef rewards to throwaway eoa for bridging
    sdl_contract.transfer(ENG_EOA_ADDRESS, 420_000 * 1e18)

    safe_tx = multisig.multisend_from_receipts()

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
