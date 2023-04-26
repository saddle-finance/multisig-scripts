
from ape_safe import ApeSafe
from brownie import Contract, accounts, network, history
from brownie.convert import to_bytes

from helpers import (CHAIN_IDS, ENG_EOA_ADDRESS, INCITE_MULTISIG_ADDRESS,
                     MULTISIG_ADDRESSES, SDL_ADDRESSES,
                     SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS,
                     SDL_MINTER_ADDRESS, VESTING_ABI, get_contract_from_deployment,
                     get_deployment_details)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "ARBITRUM"


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
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
    )

    child_gauge_factory = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "ChildGaugeFactory", multisig.account
    )
    communityfUSDCPoolLPToken = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "CommunityfUSDCPoolLPToken", multisig.account
    )

    # deploy fUSDC gauge
    # ethers.utils.keccak256(ethers.utils.formatBytes32String("fUSDC-USDC poolV2"))
    registryNameToSalt = "0x1f8f6a8a01c5b62778eeab7f342d60fcf69ff477bd14114f0c8cfcb8589a5bf6"

    deploy_tx = child_gauge_factory.deploy_gauge("0x055B05e9C610b9BdCb2E23C8BCb423D7D18b4cBB", "0x1f8f6a8a01c5b62778eeab7f342d60fcf69ff477bd14114f0c8cfcb8589a5bf6", "fUSDC-USDC poolV2")
    print("buh")
    print(deploy_tx)
    print("events incoming:")
    print(deploy_tx.events)
    fUSDC_gauge_address = deploy_tx.events['DeployedGauge']['_gauge']
    print(f"fUSDC gauge address: {fUSDC_gauge_address}")

