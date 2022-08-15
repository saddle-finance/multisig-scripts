from helpers import (
    CHAIN_IDS,
    MINICHEF_ADDRESSES,
    MULTISIG_ADDRESSES,
    OWNERS,
    intersection,
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract

from scripts.utils import confirm_posting_transaction


def main():
    """
    Updates owners of the multisig (removing Kain and adding Weston and Sam),
    Updates rewarder contract of the FRAXBP-USDs pool in minichef
    """

    TARGET_NETWORK = "ARBITRUM"

    print(f"You are using the '{network.show_active()}' network")
    assert (
        network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    ), f"Not on {TARGET_NETWORK} network"

    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    safe_contract = multisig.contract(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    minichef = multisig.contract(MINICHEF_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    Kain_Warwick = "0x5b97680e165b4dbf5c45f4ff4241e85f418c66c2"

    # prev owner(pointer), old owner, new owner
    safe_contract.swapOwner(OWNERS[7], Kain_Warwick, OWNERS[5])

    # new owner, threshold
    safe_contract.addOwnerWithThreshold(OWNERS[0], 3)
    # check owner list contains expected addresses
    new_owners = safe_contract.getOwners()
    assert len(intersection(new_owners, OWNERS)) == 0

    # FRAXBP-USDs rewarder update
    SimpleRewarder_SPA2 = "0x492ebE7816B6934cc55f3001E1Ac165A6c5AfaB0"
    FraxBP_USDs = "0x1e491122f3c096392b40a4ea27aa1a29360d38a1"
    assert minichef.lpToken(5) == FraxBP_USDs  # FRAXBP-USDs Metapool
    minichef.set(5, 105, SimpleRewarder_SPA2, True)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 6

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
