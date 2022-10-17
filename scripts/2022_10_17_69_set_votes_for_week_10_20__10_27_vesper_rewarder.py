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

    """
    Set Gauge weights for week 10_20_2022 -> 10_27_2022 from results of snapshot vote
    Vote: https://snapshot.org/#/saddlefinance.eth/proposal/0x84163f92132845811159a020c4a591c009323e4f62ca8d80e02d73149be12caf
    """

    gauge_to_relative_weight_dict = {
        "0xB2Ac3382dA625eb41Fc803b57743f941a484e2a6": 6270,  # FRAXBP Pool
        "0xc64F8A9fe7BabecA66D3997C9d15558BF4817bE3": 2184,  # Sushi SDL/WETH
        "0x953693DCB2E9DDC0c1398C1b540b81b63ceA5e16": 376,  # FraxBP-alUSD Metapool
        "0x104F44551386d603217450822443456229F73aE4": 376,  # FraxBP-sUSD Metapool
        "0x6EC5DD7D8E396973588f0dEFD79dCA04F844d57C": 75,  # FraxBP-USDT Metapool
        "0x13Ba45c2B686c6db7C2E28BD3a9E8EDd24B894eD": 85,  # Frax 3Pool
        "0x9585a54297beAa83F044866678b13d388D0180bf": 376,  # FraxBP-USX Metapool
        "0x702c1b8Ec3A77009D5898e18DA8F8959B6dF2093": 258,  # Saddle D4Pool
        "0x50d745c2a2918A47A363A2d32becd6BBC1A53ece": 0,  # Saddle USX Pool
        "0x2683190e31e8ce47467c98ff1DBc018aCDD43C2f": 0,  # Saddle sUSD Metapool
        "0x17Bde8EBf1E9FDA85b9Bd1a104266b394E9Db33e": 0,  # Saddle s/w/renBTCV2 Pool
        "0x3dC88ee38db8C7b6DCEB447E4348e51bd87ced93": 0,  # WCUSD Metapool
        "0x7B2025Bf8c5ee8Baad9da8C3E3Ee45E96ed8b8EA": 0,  # Saddle USD Pool
        "0x8B701e9B3a1887fE9b0C7936a8233b39408e69f6": 0,  # Saddle alETH Pool
        "0xB79B4fCF7cB4A1c4064Ff5b48F71A331880ab53a": 0,  # Saddle TBTC Metapool
        "0x9980C9b35844946cF3451cC0B43D9b6501F4a96E": 0,  # Saddle FraxBP-VesperFrax Metapool
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

    # Set Reward for the FraxBP-VesperFRAX Metapool Gauge
    fraxbp_vesperfrax_gauge = multisig.contract(
        "0x9980C9b35844946cF3451cC0B43D9b6501F4a96E"
    )
    fraxbp_vesperfrax_reward_forwarder = "0x811b699C69ff0AbfF98091919E637fEDCD5DffaC"
    fraxbp_vesperfrax_reward_token = "0x1b40183EFB4Dd766f11bDa7A7c3AD8982e998421"
    fraxbp_vesperfrax_gauge.add_reward(
        fraxbp_vesperfrax_reward_token, fraxbp_vesperfrax_reward_forwarder
    )

    # Send 4_045_257 SDL to deployer to refill owed rewards on arbitrum
    sdl_contract.transfer(DEPLOYER_ADDRESS, 4_045_257 * 1e18)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 69

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
