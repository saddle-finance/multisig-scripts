
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
    1. Kills old fUSDC RootGaugeV2
    2. Adds new fUSDC RootGaugeV3
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
    fUSDC_gaugeV2 = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "RootGauge_42161_CommunityfUSDCPoolLPTokenV2", multisig.account
    )
    fUSDC_gaugeV3 = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "RootGauge_42161_CommunityfUSDCPoolLPTokenV3", multisig.account
    )

    # kill old gauge
    fUSDC_gaugeV2.set_killed(True)

    # add fUSDC gauge to gauge controller
    gauge_controller.add_gauge(fUSDC_gaugeV3.address, 0, 0)

    # Combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 95  # uncomment if you want to use a specific nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)