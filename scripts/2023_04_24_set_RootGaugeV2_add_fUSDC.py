
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

    gauge_controller = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "GaugeController", multisig.account
    )
    root_gauge_factory = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "RootGaugeFactory", multisig.account
    )
    root_gaugeV2_implementation = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "RootGaugeV2", multisig.account
    )

    sdl = multisig.get_contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    sdl_vesting_contract_proxy = multisig.get_contract(
        SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]
    )

    # Claim SDL from vesting contract
    sdl_vesting_contract_proxy.release()

    # Sanity check for SDL balance in multisig
    sdl_balance = sdl.balanceOf(multisig.address)
    print(f"SDL balance in multisig before transfer: {sdl_balance / 1e18}")

    # Transfer 1.5M SDL, weekly amount to Minter
    sdl.transfer(SDL_MINTER_ADDRESS[CHAIN_IDS["MAINNET"]], 1_500_000 * 1e18)

    # Sanity check for SDL balance in multisig
    sdl_balance = sdl.balanceOf(multisig.address)
    print(f"SDL balance in multisig after transfer: {sdl_balance / 1e18}")

    # set root gauge implementation
    root_gauge_factory.set_implementation(root_gaugeV2_implementation.address)

    # deploy fUSDC gauge
    # ethers.utils.keccak256(ethers.utils.formatBytes32String("fUSDC-USDC poolV2"))
    registryNameToSalt = "0x1f8f6a8a01c5b62778eeab7f342d60fcf69ff477bd14114f0c8cfcb8589a5bf6"
    deploy_tx = root_gauge_factory.deploy_gauge(
        CHAIN_IDS["ARBITRUM"],
        registryNameToSalt,
        "CommunityfUSDCPoolLPTokenV2"
    )
    fUSDC_gauge_address = deploy_tx.events['DeployedGauge']['_gauge']

    # add fUSDC gauge to gauge controller
    gauge_controller.add_gauge(fUSDC_gauge_address, 0, 0)

    # Combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    # safe_tx.safe_nonce = 0 # uncomment if you want to use a specific nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
