import math
from helpers import (
    CHAIN_IDS,
    MINICHEF_ADDRESSES,
    MULTISIG_ADDRESSES,
    SIDECHAIN_TOTAL_EMISSION_RATE,
)
from ape_safe import ApeSafe
from brownie import ZERO_ADDRESS, Contract, accounts, network

from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "ARBITRUM"


def main():
    """
    Updates Arbitrum minichef parameters on Arbitrum network for week 9/22 - 10/6
    Vote: https://snapshot.org/#/saddlefinance.eth/proposal/0xd424d467ac93c89f9a856abce690577b22bc89f6472445a6f60143f16ce75ba1
    """

    print(f"You are using the '{network.show_active()}' network")
    # assert (
    #     network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    # ), f"Not on {TARGET_NETWORK} network"

    # Need to specify the base URL since hardhat chain ID cannot be changed from CLI
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]], 'https://safe-transaction.arbitrum.gnosis.io')

    ##### Update Minichef weights #####

    minichef = multisig.contract(MINICHEF_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    # mass update pools to checkpoint existing stakers
    pids = [1, 2, 3, 4, 5, 6, 7]
    minichef.massUpdatePools(pids)

    # 0.05% for saddleArbUSD
    assert minichef.lpToken(1) == "0xc969dD0A7AB0F8a0C5A69C0839dB39b6C928bC08"
    minichef.set(1, 5, ZERO_ADDRESS, False)

    # 0.00% USDs-saddleArbUSDv2
    assert minichef.lpToken(2) == "0xa815b134294580692482E321dD1A191aC1454192"
    minichef.set(2, 0, ZERO_ADDRESS, False)

    # 30.25% saddleFraxBP
    assert minichef.lpToken(3) == "0x896935B02D3cBEb152192774e4F1991bb1D2ED3f"
    minichef.set(3, 3025, ZERO_ADDRESS, False)

    # 3.95% saddleFraxUSDT
    assert minichef.lpToken(4) == "0x166680852ae9Dec3d63374c5eBf89E974448BFE9"
    minichef.set(4, 395, ZERO_ADDRESS, False)

    # 3.95% saddleFraxUSDs
    assert minichef.lpToken(5) == "0x1e491122f3C096392b40a4EA27aa1a29360d38a1"
    minichef.set(5, 395, ZERO_ADDRESS, False)

    # 0.00% saddleArbUSD (0, because duplicate)
    assert minichef.lpToken(6) == "0xc969dD0A7AB0F8a0C5A69C0839dB39b6C928bC08"
    minichef.set(6, 0, ZERO_ADDRESS, False)

    # 1.00% saddleArbUSDv2
    assert minichef.lpToken(7) == "0x0a20c2FFa10cD43F67D06170422505b7D6fC0953"
    minichef.set(7, 100, ZERO_ADDRESS, False)

    # Total allocation is 39.20% for Arbitrum
    assert minichef.totalAllocPoint() == 3920

    new_rate = math.floor(SIDECHAIN_TOTAL_EMISSION_RATE * 3920 / 10000)
    print(new_rate)
    minichef.setSaddlePerSecond(new_rate)

    assert minichef.saddlePerSecond() == new_rate

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 10

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
