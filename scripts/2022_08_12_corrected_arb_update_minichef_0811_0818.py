import math
from helpers import CHAIN_IDS, MINICHEF_ADDRESSES, MULTISIG_ADDRESSES, SIDECHAIN_TOTAL_EMISSION_RATE
from ape_safe import ApeSafe
from brownie import ZERO_ADDRESS, Contract, accounts, network

from scripts.utils import confirm_posting_transaction


def main():
    """
    Updates Arbitrum pool and minichef parameters on Arbitrum network
    https://snapshot.org/#/saddlefinance.eth/proposal/0xe32db5de6b40e46617ea2e39552d8a1f1485bc86eeb2fa7bc89205f2156c0939

    and updates Multisig signers - removing Kain
    """

    TARGET_NETWORK = "ARBITRUM"

    print(f"You are using the '{network.show_active()}' network")
    assert(network.chain.id ==
           CHAIN_IDS[TARGET_NETWORK]), f"Not on {TARGET_NETWORK} network"

    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    ##### Update Minichef weights #####

    minichef = multisig.contract(MINICHEF_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    # 0.32% for saddleArbUSD
    assert(minichef.lpToken(1) == "0xc969dD0A7AB0F8a0C5A69C0839dB39b6C928bC08")
    minichef.set(1, 32, ZERO_ADDRESS, False)

    # 0.32% USDs-saddleArbUSDv2
    assert(minichef.lpToken(2) == "0xa815b134294580692482E321dD1A191aC1454192")
    minichef.set(2, 32, "0x1e35ebF875f8A2185EDf22da02e7dBCa0F5558aB", True)

    # 35.89% saddleFraxBP
    assert(minichef.lpToken(3) == "0x896935B02D3cBEb152192774e4F1991bb1D2ED3f")
    minichef.set(3, 3589, ZERO_ADDRESS, False)

    # 5.03% saddleFraxUSDT
    assert(minichef.lpToken(4) == "0x166680852ae9Dec3d63374c5eBf89E974448BFE9")
    minichef.set(4, 503, ZERO_ADDRESS, False)

    # 5.03% saddleFraxUSDs
    assert(minichef.lpToken(5) == "0x1e491122f3C096392b40a4EA27aa1a29360d38a1")
    minichef.set(5, 503, "0x1e35ebF875f8A2185EDf22da02e7dBCa0F5558aB", True)

    # 0.00% saddleArbUSD (resetting to 0, because duplicate)
    assert(minichef.lpToken(6) == "0xc969dD0A7AB0F8a0C5A69C0839dB39b6C928bC08")
    minichef.set(6, 0, ZERO_ADDRESS, False)

    # 5.03% saddleArbUSDv2
    assert(minichef.lpToken(7) == "0x0a20c2FFa10cD43F67D06170422505b7D6fC0953")
    minichef.set(7, 32, ZERO_ADDRESS, False)

    # Total allocation is 46.91% for Arbitrum
    assert(minichef.totalAllocPoint() == 4691)

    new_rate = math.floor(SIDECHAIN_TOTAL_EMISSION_RATE * 4691 / 10000)
    minichef.setSaddlePerSecond(new_rate)

    assert(minichef.saddlePerSecond() == new_rate)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 5

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
