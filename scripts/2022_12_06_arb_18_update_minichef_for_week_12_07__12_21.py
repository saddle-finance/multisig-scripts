import math

from ape_safe import ApeSafe
from brownie import ZERO_ADDRESS, accounts, network

from helpers import (
    CHAIN_IDS,
    MINICHEF_ADDRESSES,
    MULTISIG_ADDRESSES,
    SIDECHAIN_TOTAL_EMISSION_RATE,
)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "ARBITRUM"


def main():
    """
    Updates minichef parameters on Arbitrum network for week 12/06 - 12/21
    Vote: https://snapshot.org/#/saddlefinance.eth/proposal/0x020e0a773444a8fe0b9b44336387a76f7befb1e4158cb83d3133fb8c9132c7c9
    """

    print(f"You are using the '{network.show_active()}' network")
    assert (
        network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    ), f"Not on {TARGET_NETWORK} network"

    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url="https://safe-transaction-arbitrum.safe.global",
    )

    ##### Update Minichef weights #####

    minichef = multisig.contract(MINICHEF_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    # mass update pools to checkpoint existing stakers
    pids = [1, 2, 3, 4, 5, 6, 7, 8]
    minichef.massUpdatePools(pids)

    # 0.00% for saddleArbUSD
    assert minichef.lpToken(1) == "0xc969dD0A7AB0F8a0C5A69C0839dB39b6C928bC08"
    if minichef.poolInfo(1)[2] != 0:
        minichef.set(1, 0, ZERO_ADDRESS, False)

    # 0.00% USDs-saddleArbUSDv2
    assert minichef.lpToken(2) == "0xa815b134294580692482E321dD1A191aC1454192"
    if minichef.poolInfo(2)[2] != 0:
        minichef.set(2, 0, ZERO_ADDRESS, False)

    # 37.51% saddleFraxBP
    assert minichef.lpToken(3) == "0x896935B02D3cBEb152192774e4F1991bb1D2ED3f"
    if minichef.poolInfo(3)[2] != 3751:
        minichef.set(3, 3751, ZERO_ADDRESS, False)

    # 5.00% saddleFraxUSDT
    assert minichef.lpToken(4) == "0x166680852ae9Dec3d63374c5eBf89E974448BFE9"
    if minichef.poolInfo(4)[2] != 500:
        minichef.set(4, 500, ZERO_ADDRESS, False)

    # 4.0% saddleFraxUSDs
    assert minichef.lpToken(5) == "0x1e491122f3C096392b40a4EA27aa1a29360d38a1"
    if minichef.poolInfo(5)[2] != 400:
        minichef.set(5, 400, ZERO_ADDRESS, False)

    # 0.00% saddleArbUSD (0, because duplicate)
    assert minichef.lpToken(6) == "0xc969dD0A7AB0F8a0C5A69C0839dB39b6C928bC08"
    if minichef.poolInfo(6)[2] != 0:
        minichef.set(6, 0, ZERO_ADDRESS, False)

    # 0.00% saddleArbUSDv2
    assert minichef.lpToken(7) == "0x0a20c2FFa10cD43F67D06170422505b7D6fC0953"
    if minichef.poolInfo(7)[2] != 0:
        minichef.set(7, 0, ZERO_ADDRESS, False)

    # 1.00% saddleArbUSX-FRAXBP
    assert minichef.lpToken(8) == "0x721DaC7d5ACc8Aa62946fd583C1F999e1570b97D"
    if minichef.poolInfo(8)[2] != 100:
        minichef.set(8, 100, ZERO_ADDRESS, False)

    # Total allocation is 47.51% for Arbitrum
    assert minichef.totalAllocPoint() == 4751

    new_rate = math.floor(SIDECHAIN_TOTAL_EMISSION_RATE * 4751 / 10000)
    minichef.setSaddlePerSecond(new_rate)

    assert minichef.saddlePerSecond() == new_rate

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 18

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
