from brownie import accounts, history, network

from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, get_contract_from_deployment

TARGET_NETWORK = "MAINNET"


def main():
    """
    Move any permissions from the EOAs to Saddle multisig
    """
    print(f"You are using the '{network.show_active()}' network")
    assert (
        network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    ), f"Not on {TARGET_NETWORK} network"

    multisig_address = MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    deployer_EOA = accounts.load("deployer")
    cross_chain_deployer_EOA = accounts.load("cross_chain_deployer")

    root_gauge_factory = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "RootGaugeFactory")
    proxy_admin = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "ProxyAdmin")
    any_call_translator = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "AnyCallTranslator")
    root_oracle = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "RootOracle")
    arbitrum_bridger = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "ArbitrumBridger")
    optimism_bridger = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "OptimismBridger")

    root_gauge_factory.commit_transfer_ownership(
        multisig_address, {"from": deployer_EOA})
    proxy_admin.transferOwnership(
        multisig_address, {"from": cross_chain_deployer_EOA})
    any_call_translator.transferOwnership(
        multisig_address, {"from": deployer_EOA})
    root_oracle.commitTransferOwnership(
        multisig_address, {"from": cross_chain_deployer_EOA})
    arbitrum_bridger.transferOwnership(
        multisig_address, {"from": deployer_EOA})
    optimism_bridger.transferOwnership(
        multisig_address, {"from": deployer_EOA})

    for tx in history:
        tx.info()
    return
