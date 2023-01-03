from datetime import datetime, timedelta

from ape_safe import ApeSafe
from brownie import accounts, network

from helpers import (
    CHAIN_IDS,
    MULTISIG_ADDRESSES,
    SDL_ADDRESSES,
    SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS,
    SDL_MINTER_ADDRESS,
)
from scripts.utils import confirm_posting_transaction


def main():
    """Ramps A param for select pools as per SIP-46:
    https://snapshot.org/#/saddlefinance.eth/proposal/0xe894884108944bf43cd403b9cbc3493c879f601da37ae59f9b27dd52282d8d86
    """
    print(f"You are using the '{network.show_active()}' network")
    TARGET_NETWORK = "MAINNET"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    pools_to_future_a = {
        "0x13Cc34Aa8037f722405285AD2C82FE570bfa2bdc": 1500,  # SaddleFraxBPPool
        "0x69baA0d7c2e864b74173922Ca069Ac79d3be1556": 400,  # SaddleFraxsUSDPool
        "0xC765Cd3d015626244AD63B5FB63a97c5634643b9": 400,  # SaddleFraxUSDTPool
    }
    now = datetime.now()
    # @dev delta must be min 14 days. Add a week buffer for multisig to sign.
    now_plus_21_days = now + timedelta(days=21)
    now_plus_21_days_seconds = int(
        (now_plus_21_days - datetime(1970, 1, 1)).total_seconds()
    )
    for pool_addr, A in pools_to_future_a.items():
        contract = multisig.contract(pool_addr)
        contract.rampA(A, now_plus_21_days_seconds)

    # Claim SDL from vesting contract
    sdl_vesting_contract_proxy = multisig.contract(
        SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]
    )
    sdl_vesting_contract_proxy.release()
    # Send 3.5M SDL to SDL minter
    sdl_contract = multisig.contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    minter = multisig.contract(SDL_MINTER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]])
    deployer = accounts.load("deployer")

    # Minter is currently owed 5_182_645, 3_5000_000 is sent by nonce 78, sending remaining
    sdl_contract.transfer(minter.address, 1_682_646 * 1e18)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 79

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx, False)

    confirm_posting_transaction(multisig, safe_tx)
