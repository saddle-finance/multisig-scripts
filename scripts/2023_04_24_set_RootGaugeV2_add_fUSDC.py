
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
    1. Set Implementation of RootGauge to RootGaugeV2 in RootGaugeFactory
    2. Deploy fUSDC gauge
    3. Add fUSDC gauge to GaugeController
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
    root_gauge_factory = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "RootGaugeFactory", multisig.account
    )
    root_gaugeV2_implementation = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "RootGaugeV2", multisig.account
    )

    # set root gauge implementation
    root_gauge_factory.set_implementation(root_gaugeV2_implementation.address)
    
    # deploy fUSDC gauge
    # ethers.utils.keccak256(ethers.utils.formatBytes32String("fUSDC-USDC poolV2"))
    registryNameToSalt = "0x1f8f6a8a01c5b62778eeab7f342d60fcf69ff477bd14114f0c8cfcb8589a5bf6"
    root_gauge_factory.deploy_gauge(
        CHAIN_IDS["ARBITRUM"],
        registryNameToSalt,
        "CommunityfUSDCPoolLPTokenV2"
    )
    # add fUSDC gauge to gauge controller
    address, abi = get_deployment_details(
        CHAIN_IDS["MAINNET"], "RootGauge_42161_CommunityfUSDCPoolLPTokenV2")
    gauge_controller.add_gauge(address, 0, 0)

    # Combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    # safe_tx.safe_nonce = 0 # uncomment if you want to use a specific nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
