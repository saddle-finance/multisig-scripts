from ape_safe import ApeSafe
from brownie import Contract, accounts, network

from helpers import (CHAIN_IDS, DEPLOYER_ADDRESS, GNOSIS_SAFE_ABI,
                     MASTER_REGISTRY_ADDRESSES, MULTISIG_ADDRESSES,
                     OPS_MULTISIG_ADDRESSES, OWNERS, intersection)
from scripts.utils import (confirm_posting_transaction,
                           convert_string_to_bytes32)

TARGET_NETWORK = "OPTIMISM"


def main():
    """
    Replace an inactive signer with a new one. Adds another signer.

    Move the manager roles of below contracts from deployer EOA to 2/3 ops multisig
    * MasterRegistry
    * PoolRegistry
    * PermissionlessDeployer
    """
    print(f"You are using the '{network.show_active()}' network")
    assert network.chain.id == CHAIN_IDS[TARGET_NETWORK], f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url="https://safe-transaction-optimism.safe.global",
        multisend="0x998739BFdAAdde7C933B942a68053933098f9EDa"
    )

    # Remove 1 signer, add 2 signers
    safe_contract = Contract.from_abi(
        "Gnosis Safe",
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        GNOSIS_SAFE_ABI,
        multisig.account,
    )
    Kain_Warwick = "0x5b97680e165b4dbf5c45f4ff4241e85f418c66c2"

    # prev owner(pointer), old owner, new owner
    # note* owners are in a different order than mainnet
    safe_contract.swapOwner(OWNERS[7], Kain_Warwick, OWNERS[5])

    safe_contract.addOwnerWithThreshold(OWNERS[0], 3)
    new_owners = safe_contract.getOwners()

    # check owner list contains expected addresses
    assert len(intersection(new_owners, OWNERS)) == 0

    # Replace deployer EOA with a 2/3 ops multisig as manager
    master_registry = multisig.contract(
        MASTER_REGISTRY_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    ops_multisig_address = OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]

    manager_role = master_registry.SADDLE_MANAGER_ROLE()
    master_registry.grantRole(manager_role, ops_multisig_address)
    master_registry.revokeRole(manager_role, DEPLOYER_ADDRESS)

    # Find pool registry
    pool_registry = multisig.contract(
        master_registry.resolveNameToLatestAddress(
            convert_string_to_bytes32("PoolRegistry")
        )
    )

    # Revoke admin role from deployer
    admin_role = pool_registry.DEFAULT_ADMIN_ROLE()
    pool_registry.revokeRole(admin_role, DEPLOYER_ADDRESS)

    # Replace deployer EOA with a 2/3 ops multisig as manager
    manager_role = pool_registry.SADDLE_MANAGER_ROLE()
    pool_registry.grantRole(manager_role, ops_multisig_address)
    pool_registry.revokeRole(manager_role, DEPLOYER_ADDRESS)

    community_manager_role = pool_registry.COMMUNITY_MANAGER_ROLE()
    pool_registry.grantRole(community_manager_role, ops_multisig_address)
    pool_registry.revokeRole(community_manager_role, DEPLOYER_ADDRESS)

    # Find Permissionless deployer
    permissionless_deployer = multisig.contract(
        master_registry.resolveNameToLatestAddress(
            convert_string_to_bytes32("PermissionlessDeployer")
        )
    )

    # Replace manager
    manager_role = permissionless_deployer.SADDLE_MANAGER_ROLE()
    permissionless_deployer.grantRole(manager_role, ops_multisig_address)
    permissionless_deployer.revokeRole(manager_role, DEPLOYER_ADDRESS)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 0

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    # multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
