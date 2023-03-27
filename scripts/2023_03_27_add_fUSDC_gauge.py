
from ape_safe import ApeSafe
from brownie import Contract, accounts, network, history

from helpers import (CHAIN_IDS, ENG_EOA_ADDRESS, INCITE_MULTISIG_ADDRESS,
                     MULTISIG_ADDRESSES, SDL_ADDRESSES,
                     SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS,
                     SDL_MINTER_ADDRESS, VESTING_ABI, get_contract_from_deployment,
                     get_deployment_details)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():
    """
    1. Add fUSDC Root gauge to gauge controller
    """

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
    )

    gauge_controller = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "GaugeController", multisig.account
    )

    # add baoUSD gauge to gauge controller
    RootGauge_42161_CommunityfUSDCPoolLPToken = "0xC7ec37B1E3be755e06a729e11a76ff4259768F12"

    gauge_controller.add_gauge(RootGauge_42161_CommunityfUSDCPoolLPToken, 0, 0)

    # Combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 91

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    # multisig.preview(safe_tx)

    for tx in history:
        tx.info()
    confirm_posting_transaction(multisig, safe_tx)
