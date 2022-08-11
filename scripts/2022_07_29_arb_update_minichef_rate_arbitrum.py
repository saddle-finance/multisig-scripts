import math
from helpers import CHAIN_IDS, MINICHEF_ADDRESSES, MULTISIG_ADDRESSES, SIDECHAIN_TOTAL_EMISSION_RATE
from ape_safe import ApeSafe
from brownie import ZERO_ADDRESS, Contract, accounts, network

from scripts.utils import confirm_posting_transaction


def main():
    """
    Updates Arbitrum pool and minichef parameters on Arbitrum network
    https://snapshot.org/#/saddlefinance.eth/proposal/0x6989db6c9597b19377aca008f3727d5fb7a0f83772dd28455c84dc91be577edc
    """

    TARGET_NETWORK = "ARBITRUM"

    print(f"You are using the '{network.show_active()}' network")
    assert(network.chain.id ==
           CHAIN_IDS[TARGET_NETWORK]), f"Not on {TARGET_NETWORK} network"

    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    minichef = multisig.contract(MINICHEF_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    # 37.51% for Arbitrum: FraxBP
    assert(minichef.lpToken(3) == "0x896935B02D3cBEb152192774e4F1991bb1D2ED3f")
    minichef.set(3, 3751, ZERO_ADDRESS, False)
    # 5.00% for Arbitrum: FraxBP-USDT
    assert(minichef.lpToken(4) == "0x166680852ae9Dec3d63374c5eBf89E974448BFE9")
    minichef.set(4, 500, ZERO_ADDRESS, False)
    # 5.00% for Arbitrum: FraxBP-USDs
    minichef.add(
        500, "0x1e491122f3C096392b40a4EA27aa1a29360d38a1", ZERO_ADDRESS)

    # Total allocation is 47.51% for Arbitrum
    assert(minichef.totalAllocPoint() == 4751)

    new_rate = math.floor(SIDECHAIN_TOTAL_EMISSION_RATE * 4751 / 10000)
    minichef.setSaddlePerSecond(new_rate)

    assert(minichef.saddlePerSecond() == new_rate)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 4

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
