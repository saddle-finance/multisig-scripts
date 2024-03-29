import math
from datetime import datetime, timedelta

from ape_safe import ApeSafe
from brownie import ZERO_ADDRESS, accounts, network

from helpers import (
    CHAIN_IDS,
    GNOSIS_SAFE_BASE_URLS,
    MINICHEF_ADDRESSES,
    MULTISIG_ADDRESSES,
    SIDECHAIN_TOTAL_EMISSION_RATE,
)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "ARBITRUM"


def main():
    """
    Updates minichef parameters on Arbitrum network for week 01/04 - 01/18
    Vote: https://snapshot.org/#/saddlefinance.eth/proposal/0x706a9e600d66fabe316696588dd689acb6ed01b193510effb6bf220b585ce716
    """

    print(f"You are using the '{network.show_active()}' network")
    assert (
        network.chain.id == CHAIN_IDS[TARGET_NETWORK]
    ), f"Not on {TARGET_NETWORK} network"

    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        GNOSIS_SAFE_BASE_URLS[CHAIN_IDS[TARGET_NETWORK]],
    )

    ##### Ramp a-values #####

    pools_to_future_a = {
        "0x401AFbc31ad2A3Bc0eD8960d63eFcDEA749b4849": 1000,  # SaddleFraxBPPool
        "0xa5bD85ed9fA27ba23BfB702989e7218E44fd4706": 200,  # SaddleFraxUSDsPool
        "0xf8504e92428d65E56e495684A38f679C1B1DC30b": 200,  # SaddleFraxUSDTPool
    }
    now = datetime.now()
    # @dev delta must be min 14 days. Add a week buffer for multisig to sign.
    now_plus_21_days = now + timedelta(days=21)
    now_plus_21_days_seconds = int(
        (now_plus_21_days - datetime(1970, 1, 1)).total_seconds()
    )
    for pool_addr, A in pools_to_future_a.items():
        contract = multisig.contract(pool_addr)
        contract.rampA(A, now_plus_21_days_seconds)

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

    # 37.02% saddleFraxBP
    assert minichef.lpToken(3) == "0x896935B02D3cBEb152192774e4F1991bb1D2ED3f"
    if minichef.poolInfo(3)[2] != 3702:
        minichef.set(3, 3702, ZERO_ADDRESS, False)

    # 4.93% saddleFraxUSDT
    assert minichef.lpToken(4) == "0x166680852ae9Dec3d63374c5eBf89E974448BFE9"
    if minichef.poolInfo(4)[2] != 493:
        minichef.set(4, 493, ZERO_ADDRESS, False)

    # 3.95% saddleFraxUSDs
    assert minichef.lpToken(5) == "0x1e491122f3C096392b40a4EA27aa1a29360d38a1"
    if minichef.poolInfo(5)[2] != 395:
        minichef.set(5, 395, ZERO_ADDRESS, False)

    # 0.00% saddleArbUSD (0, because duplicate)
    assert minichef.lpToken(6) == "0xc969dD0A7AB0F8a0C5A69C0839dB39b6C928bC08"
    if minichef.poolInfo(6)[2] != 0:
        minichef.set(6, 0, ZERO_ADDRESS, False)

    # 0.00% saddleArbUSDv2
    assert minichef.lpToken(7) == "0x0a20c2FFa10cD43F67D06170422505b7D6fC0953"
    if minichef.poolInfo(7)[2] != 0:
        minichef.set(7, 0, ZERO_ADDRESS, False)

    # 0.99% saddleArbUSX-FRAXBP
    assert minichef.lpToken(8) == "0x721DaC7d5ACc8Aa62946fd583C1F999e1570b97D"
    if minichef.poolInfo(8)[2] != 99:
        minichef.set(8, 99, ZERO_ADDRESS, False)

    # Total allocation is 46.89% for Arbitrum
    assert minichef.totalAllocPoint() == 4689

    new_rate = math.floor(SIDECHAIN_TOTAL_EMISSION_RATE * 4689 / 10000)
    minichef.setSaddlePerSecond(new_rate)

    assert minichef.saddlePerSecond() == new_rate

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 19

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx, False)

    confirm_posting_transaction(multisig, safe_tx)
