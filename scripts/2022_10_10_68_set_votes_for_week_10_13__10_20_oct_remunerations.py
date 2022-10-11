import math

from ape_safe import ApeSafe
from brownie import Contract, accounts, network
from helpers import (
    CHAIN_IDS,
    DEPLOYER_ADDRESS,
    GAUGE_ABI,
    GAUGE_CONTROLLER_ADDRESS,
    MULTISIG_ADDRESSES,
    SDL_ADDRESSES,
    SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS,
    SDL_MINTER_ADDRESS,
)

from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():

    print(f"You are using the '{network.show_active()}' network")
    assert network.chain.id == CHAIN_IDS[TARGET_NETWORK], f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    sdl_vesting_contract_proxy = multisig.contract(
        SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]
    )
    sdl_contract = multisig.contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    gauge_controller = multisig.contract(GAUGE_CONTROLLER_ADDRESS[CHAIN_IDS["MAINNET"]])

    sdl_vesting_contract_proxy.release()

    """Send the 6.7m SDL for October 2022 to affected LPs according to https://snapshot.org/#/saddlefinance.eth/proposal/0xf27b07ef7025aa23edb2a84d56825511ea7adff8d6164cd09a23c63c42cdc01a"""

    refunds = {
        "0xa0f75491720835b36edc92d06ddc468d201e9b73": 1552781.39214474,
        "0x38ee5f5a39c01cb43473992c12936ba1219711ab": 1508913.00981469,
        "0x38f9abd4bd8947da035abf51fc21244108a81ca6": 1132442.54883665,
        "0x0ea4a285e1353f490ec7f473ab3174cac71cf79a": 1132219.93569692,
        "0x6ef3f0ff397c3de367c6ca2cc3e6b6955e7993a5": 183256.672290299,
        "0x6a73204db71f8e054bf9a0680b02ae96f700b595": 181265.62698562,
        "0x5eea118e75f247014c6d0e990f02a0c254edc852": 151319.065792276,
        "0x2b9d8f558e02753ed7d4d97dedfad662c02af3cb": 150998.563444325,
        "0x0bb31c6278d58cff41b7e8ed3b20f76424fd69ad": 150936.201534769,
        "0xc7d2a419f8f2eaa06b3811cf7faaa7440dcf96b7": 150888.579725597,
        "0xae1e5c84b73136a49efb70a15149c350015391ed": 113255.253248794,
        "0xe2d079278c0f4959199136f8db11c645d69a292b": 113234.843908429,
        "0xffd4dae0d7d8ddb6f408dca0a47763ae3a57f4ce": 62280.638160798,
        "0x9c7d894a29f97636b66dea646a1ae2f9c83a2830": 54450.629479509,
        "0x77956a9d1b9901bbe4cfc2ed37db17500fbe7b0c": 37688.12936225,
        "0x02ef8147e2d0997cca48d99f01bad846d16558fa": 30168.0509875,
        "0xc7193c01f43257f3fe4c8f86784fcaa578a9e2b1": 24138.9591695,
        "0xd716ad4f10eade5af4ed10006678f49bd2e6624f": 7545.4015315,
        "0x99eb33756a2eaa32f5964a747722c4b59e6af351": 3214.8607335,
        "0x2a1eaf114f2c23d30ef571d6e84fcbeb2f6f4e62": 1509.903056,
        "0x46866d274e6d9015c5fdc098ce270803e11e3ef4": 829.988099,
        "0x2d5d79753bb8e02ca1ce8ece0aa55288f8c8d840": 414.9940495,
        "0xb5e46afa9596cb6f44d2fcb6dbd2096dbe35396c": 75.9582305,
        "0x74f8744020f5900a2c3a3289c6c2182f56a6901f": 20.7935375,
    }
    total = sum(refunds.values())
    print(f"Total amount to be refunded: {total} SDL")
    for address, amount in refunds.items():
        sdl_contract.transfer(address, amount * 1e18)

    """
    Set Gauge weights for week 10_13_2022 -> 10_20_2022 from results of snapshot vote
    Vote: https://snapshot.org/#/saddlefinance.eth/proposal/0xda1c8607e38db12bd5affe7891cb9d9e4eedb13fe7301afcb0e67d7abd10831a
    """

    gauge_to_relative_weight_dict = {
        "0xB2Ac3382dA625eb41Fc803b57743f941a484e2a6": 5765,  # FRAXBP Pool
        "0xc64F8A9fe7BabecA66D3997C9d15558BF4817bE3": 2170,  # Sushi SDL/WETH
        "0x953693DCB2E9DDC0c1398C1b540b81b63ceA5e16": 362,  # FraxBP-alUSD Metapool
        "0x104F44551386d603217450822443456229F73aE4": 360,  # FraxBP-sUSD Metapool
        "0x6EC5DD7D8E396973588f0dEFD79dCA04F844d57C": 72,  # FraxBP-USDT Metapool
        "0x13Ba45c2B686c6db7C2E28BD3a9E8EDd24B894eD": 72,  # Frax 3Pool
        "0x9585a54297beAa83F044866678b13d388D0180bf": 362,  # FraxBP-USX Metapool
        "0x702c1b8Ec3A77009D5898e18DA8F8959B6dF2093": 827,  # Saddle D4Pool
        "0x50d745c2a2918A47A363A2d32becd6BBC1A53ece": 2,  # Saddle USX Pool
        "0x2683190e31e8ce47467c98ff1DBc018aCDD43C2f": 0,  # Saddle sUSD Metapool
        "0x17Bde8EBf1E9FDA85b9Bd1a104266b394E9Db33e": 0,  # Saddle s/w/renBTCV2 Pool
        "0x3dC88ee38db8C7b6DCEB447E4348e51bd87ced93": 0,  # WCUSD Metapool
        "0x7B2025Bf8c5ee8Baad9da8C3E3Ee45E96ed8b8EA": 0,  # Saddle USD Pool
        "0x8B701e9B3a1887fE9b0C7936a8233b39408e69f6": 2,  # Saddle alETH Pool
        "0xB79B4fCF7cB4A1c4064Ff5b48F71A331880ab53a": 0,  # Saddle TBTC Metapool
        "0x9980C9b35844946cF3451cC0B43D9b6501F4a96E": 5,  # Saddle FraxBP-VesperFrax Metapool
    }

    total_weight = sum(gauge_to_relative_weight_dict.values())
    assert (
        9999 <= total_weight <= 10001
    ), f"Total weight must be 10000 but is {total_weight}"

    # print out details first to confirm the we are setting gauge weights correctly
    # separate printing and executing into 2 loops to avoid printing inbetween transaction logs
    for gauge in gauge_to_relative_weight_dict:
        gauge_contract = Contract.from_abi("LiqGaugeV5", gauge, GAUGE_ABI)
        gauge_name = gauge_contract.name()
        print(
            f"Setting {gauge_name}'s weight to {gauge_to_relative_weight_dict[gauge]}"
        )

    # execute txs for setting gauge weights if they are changed
    for gauge, future_weight in gauge_to_relative_weight_dict.items():
        current_weight = gauge_controller.get_gauge_weight(gauge)
        if current_weight != future_weight:
            gauge_controller.change_gauge_weight(gauge, future_weight)

    total_weight = gauge_controller.get_total_weight() // 1e18
    assert (
        9999 <= total_weight <= 10000
    ), f"Total weight must be 10000 but is {total_weight}"

    # Send 500k SDL to deployer for manual bridging to Arbitrum Minichef to refill rewards
    sdl_contract.transfer(DEPLOYER_ADDRESS, 4_360_921 * 1e18)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 68

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
