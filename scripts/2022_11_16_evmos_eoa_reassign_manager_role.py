from brownie import Contract, accounts, history, network

from helpers import (CHAIN_IDS, DEPLOYER_ADDRESS, MASTER_REGISTRY_ADDRESSES,
                     MINICHEF_ADDRESSES, OPS_MULTISIG_ADDRESSES)
from scripts.utils import convert_string_to_bytes32

TARGET_NETWORK = "EVMOS"


def main():
    """
    Move the manager roles of below contracts from deployer EOA to 2/3 ops multisig
    * Minichef
    * MasterRegistry
    * PoolRegistry
    * PermissionlessDeployer
    """
    print(f"You are using the '{network.show_active()}' network")
    assert network.chain.id == CHAIN_IDS[TARGET_NETWORK], f"Not on {TARGET_NETWORK}"
    deployer = accounts.load("deployer")

    ops_multisig_address = OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]

    # Transfer Minichef ownership to ops multisig
    minichef = Contract(
        MINICHEF_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]], owner=deployer)
    minichef.transferOwnership(
        ops_multisig_address, True, False)

    # Replace MasterRegistry manager with ops multisig
    master_registry = Contract(
        MASTER_REGISTRY_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]], owner=deployer
    )

    manager_role = master_registry.SADDLE_MANAGER_ROLE()
    master_registry.grantRole(manager_role, ops_multisig_address)
    master_registry.revokeRole(manager_role, DEPLOYER_ADDRESS)

    admin_role = master_registry.DEFAULT_ADMIN_ROLE()
    master_registry.grantRole(admin_role, ops_multisig_address)
    master_registry.revokeRole(admin_role, DEPLOYER_ADDRESS)

    # Replace PoolRegistry admin and manager with ops multisig
    pool_registry = Contract(master_registry.resolveNameToLatestAddress(
        convert_string_to_bytes32("PoolRegistry")), owner=deployer)

    manager_role = pool_registry.SADDLE_MANAGER_ROLE()
    pool_registry.grantRole(manager_role, ops_multisig_address)
    pool_registry.revokeRole(manager_role, DEPLOYER_ADDRESS)

    approved_owner_role = pool_registry.SADDLE_APPROVED_POOL_OWNER_ROLE()
    pool_registry.grantRole(approved_owner_role, ops_multisig_address)
    pool_registry.revokeRole(approved_owner_role, DEPLOYER_ADDRESS)

    community_manager_role = pool_registry.COMMUNITY_MANAGER_ROLE()
    pool_registry.grantRole(community_manager_role, ops_multisig_address)
    pool_registry.revokeRole(community_manager_role, DEPLOYER_ADDRESS)

    admin_role = pool_registry.DEFAULT_ADMIN_ROLE()
    pool_registry.grantRole(admin_role, ops_multisig_address)
    pool_registry.revokeRole(admin_role, DEPLOYER_ADDRESS)

    # Find Permissionless deployer
    permissionless_deployer = Contract(
        master_registry.resolveNameToLatestAddress(
            convert_string_to_bytes32("PermissionlessDeployer")
        ),
        owner=deployer,
    )

    # Replace manager
    manager_role = permissionless_deployer.SADDLE_MANAGER_ROLE()
    permissionless_deployer.grantRole(manager_role, ops_multisig_address)
    permissionless_deployer.revokeRole(manager_role, DEPLOYER_ADDRESS)

    # Replace admin
    admin_role = permissionless_deployer.DEFAULT_ADMIN_ROLE()
    permissionless_deployer.grantRole(admin_role, ops_multisig_address)
    permissionless_deployer.revokeRole(admin_role, DEPLOYER_ADDRESS)

    for tx in history:
        tx.info()
    return
