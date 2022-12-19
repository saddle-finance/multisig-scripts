from ape_safe import ApeSafe
from brownie import Contract, accounts, network

from helpers import (
    CHAIN_IDS,
    ENG_EOA_ADDRESS,
    INCITE_MULTISIG_ADDRESS,
    MULTISIG_ADDRESSES,
    SDL_ADDRESSES,
    SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS,
    VESTING_ABI,
)
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():
    """
    Send SDL to fund minichef rewards from results of snapshot vote
    Vote: https://snapshot.org/#/saddlefinance.eth/proposal/0x508226028d3a401df05f84aa4f6292f5dde8db55d5aa10804f73794a02dbf5f0
    """

    print(f"You are using the '{network.show_active()}' network")
    assert network.chain.id == CHAIN_IDS[TARGET_NETWORK], f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url="https://safe-transaction-mainnet.safe.global",
    )
    sdl = multisig.contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    sdl_vesting_contract_proxy = multisig.contract(
        SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]
    )

    # Claim SDL from vesting contract
    sdl_vesting_contract_proxy.release()

    # Send needed SDL to EOA for bridging to minichefs
    sidechain_minichef_debt = 625_000e18  # SDL owed to optimism & arbitrum

    # L2 Minichefs (optimism & arbitrum)
    sdl_balance = sdl.balanceOf(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])
    sdl.transfer(ENG_EOA_ADDRESS, sidechain_minichef_debt)
    assert sdl_balance > sdl.balanceOf(
        MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]]
    ), "SDL not sent to EOA"

    """Send a batch of 3.37m SDL (10%) for November 2022 to affected LPs according to https://snapshot.org/#/saddlefinance.eth/proposal/0xf27b07ef7025aa23edb2a84d56825511ea7adff8d6164cd09a23c63c42cdc01a"""

    refunds = {
        "0xa0f75491720835b36edc92d06ddc468d201e9b73": 776390.696072370,
        "0x38ee5f5a39c01cb43473992c12936ba1219711ab": 754456.504907345,
        "0x38f9abd4bd8947da035abf51fc21244108a81ca6": 566221.274418325,
        "0x0ea4a285e1353f490ec7f473ab3174cac71cf79a": 566109.967848460,
        "0x6ef3f0ff397c3de367c6ca2cc3e6b6955e7993a5": 91628.336145150,
        "0x6a73204db71f8e054bf9a0680b02ae96f700b595": 90632.813492810,
        "0x5eea118e75f247014c6d0e990f02a0c254edc852": 75659.532896138,
        "0x2b9d8f558e02753ed7d4d97dedfad662c02af3cb": 75499.281722163,
        "0x0bb31c6278d58cff41b7e8ed3b20f76424fd69ad": 75468.100767385,
        "0xc7d2a419f8f2eaa06b3811cf7faaa7440dcf96b7": 75444.289862799,
        "0xae1e5c84b73136a49efb70a15149c350015391ed": 56627.626624397,
        "0xe2d079278c0f4959199136f8db11c645d69a292b": 56617.421954215,
        "0xffd4dae0d7d8ddb6f408dca0a47763ae3a57f4ce": 31140.319080399,
        "0x9c7d894a29f97636b66dea646a1ae2f9c83a2830": 27225.314739755,
        "0x77956a9d1b9901bbe4cfc2ed37db17500fbe7b0c": 18844.064681125,
        "0x02ef8147e2d0997cca48d99f01bad846d16558fa": 15084.025493750,
        "0xc7193c01f43257f3fe4c8f86784fcaa578a9e2b1": 12069.479584750,
        "0xd716ad4f10eade5af4ed10006678f49bd2e6624f": 3772.700765750,
        "0x99eb33756a2eaa32f5964a747722c4b59e6af351": 1607.430366750,
        "0x2a1eaf114f2c23d30ef571d6e84fcbeb2f6f4e62": 754.951528000,
        "0x46866d274e6d9015c5fdc098ce270803e11e3ef4": 414.994049500,
        "0x2d5d79753bb8e02ca1ce8ece0aa55288f8c8d840": 207.497024750,
        "0xb5e46afa9596cb6f44d2fcb6dbd2096dbe35396c": 37.979115250,
        "0x74f8744020f5900a2c3a3289c6c2182f56a6901f": 10.396768750,
    }
    total = sum(refunds.values())
    print(f"Total amount to be refunded: {total} SDL")
    sdl_contract = multisig.contract(SDL_ADDRESSES[CHAIN_IDS["MAINNET"]])
    for address, amount in refunds.items():
        sdl_contract.transfer(address, amount * 1e18)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 75

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
