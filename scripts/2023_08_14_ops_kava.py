from ape_safe import ApeSafe
from brownie import Contract, accounts, chain, history, network

from helpers import (CHAIN_IDS, ENG_EOA_ADDRESS, ERC20_ABI,
                     INCITE_MULTISIG_ADDRESS, META_SWAP_ABI,
                     META_SWAP_DEPOSIT_ABI, MULTISIG_ADDRESSES,
                     OPS_MULTISIG_ADDRESSES, SDL_ADDRESSES,
                     SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS,
                     SDL_MINTER_ADDRESS, SWAP_ABI, VESTING_ABI,
                     get_contract_from_deployment)
from scripts.utils import (claim_admin_fees, confirm_posting_transaction,
                           pause_all_pools)

TARGET_NETWORK = "KAVA"


def main():
    """
    Pauses permissionless deployer contract
    """

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    deployer = accounts.load("deployer")

    permissionless_deployer_contract = get_contract_from_deployment(
        CHAIN_IDS[TARGET_NETWORK], "PermissionlessDeployer", deployer
    )

    # Pause permissionless deployer by setting target addresses to zero
    DEAD_ADDRESS = "0x000000000000000000000000000000000000dead"
    permissionless_deployer_contract.setTargetSwap(DEAD_ADDRESS)
    permissionless_deployer_contract.setTargetMetaSwap(DEAD_ADDRESS)
    permissionless_deployer_contract.setTargetMetaSwapDeposit(DEAD_ADDRESS)
    permissionless_deployer_contract.setTargetLPToken(DEAD_ADDRESS)

    # # combine history into multisend txn
    # safe_tx = ops_multisig.multisend_from_receipts()

    # # sign with private key
    # safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    # # multisig.preview(safe_tx)
    # for tx in history:
    #     tx.info()
    # confirm_posting_transaction(ops_multisig, safe_tx)
