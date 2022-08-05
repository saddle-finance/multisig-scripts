from array import array
from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, OWNERS, GNOSIS_SAFE_ABI, intersection
from ape_safe import ApeSafe
from brownie import accounts, network, Contract

from scripts.utils import confirm_posting_transaction


def main():
    """Update a vesting contract's ownership to company multisig"""

    TARGET_NETWORK = "EVMOS"

    print(f"You are using the '{network.show_active()}' network")
    assert (
        network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    ), f"Not on {TARGET_NETWORK} network"

    deployer = accounts.load("deployer")  # prompts for password

    # base_url added as by default no optimism support
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url="https://transaction.safe.evmos.org/",
    )

    # safe_contract = Contract.from_explorer(
    #     MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    # )
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

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 0

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
