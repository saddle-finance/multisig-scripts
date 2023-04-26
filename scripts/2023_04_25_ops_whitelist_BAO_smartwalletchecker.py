
from ape_safe import ApeSafe
from brownie import Contract, accounts, network, history

from helpers import (CHAIN_IDS, OPS_MULTISIG_ADDRESSES,
                     get_contract_from_deployment,)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():
    """
    1. Claims vesting SDL and refills Minter
    2. Set Implementation of RootGauge to RootGaugeV2 in RootGaugeFactory
    3. Deploy fUSDC gauge
    4. Add fUSDC gauge to GaugeController
    """

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    ops_multisig = ApeSafe(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    )

    # whitelisting wallet addresses
    smart_wallet_checker = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "SmartWalletChecker", ops_multisig.account
    )
    # BAO
    smart_wallet_checker.approveWallet(
        "0x3dfc49e5112005179da613bde5973229082dac35")

    # Combine history into multisend txn
    safe_tx = ops_multisig.multisend_from_receipts()
    # safe_tx.safe_nonce = 0 # uncomment if you want to use a specific nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    ops_multisig.preview(safe_tx)

    confirm_posting_transaction(ops_multisig, safe_tx)
