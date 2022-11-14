from ape_safe import ApeSafe
from brownie import Contract, accounts, network
from helpers import (
    CHAIN_IDS,
    DEPLOYER_ADDRESS,
    GAUGE_ABI,
    GAUGE_CONTROLLER_ADDRESS,
    MINTER,
    MULTISIG_ADDRESSES,
    SDL_ADDRESSES,
    SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS,
)

from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():
    """
    Set Gauge weights for week 11_02_2022 -> 11_09_2022 from results of snapshot vote
    Vote: https://snapshot.org/#/saddlefinance.eth/proposal/0xdb044df9ddbd3d09f96a7252496db75408529d89382c60c3a1249c0ae9ed93bc
    """

    print(f"You are using the '{network.show_active()}' network")
    assert network.chain.id == CHAIN_IDS[TARGET_NETWORK], f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url="https://safe-transaction-mainnet.safe.global",
    )
    sdl = multisig.contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    gauge_controller = multisig.contract(
        GAUGE_CONTROLLER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]
    )
    sdl_vesting_contract_proxy = multisig.contract(
        SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]
    )

    # Claim SDL from vesting contract
    sdl_vesting_contract_proxy.release()

    # Set gauge weights
    gauge_to_relative_weight_dict = {
        "0xB2Ac3382dA625eb41Fc803b57743f941a484e2a6": 7162,  # FRAXBP Pool
        "0xc64F8A9fe7BabecA66D3997C9d15558BF4817bE3": 523,  # Sushi SDL/WETH
        "0x953693DCB2E9DDC0c1398C1b540b81b63ceA5e16": 451,  # FraxBP-alUSD Metapool
        "0x104F44551386d603217450822443456229F73aE4": 451,  # FraxBP-sUSD Metapool
        "0x6EC5DD7D8E396973588f0dEFD79dCA04F844d57C": 88,  # FraxBP-USDT Metapool
        "0x13Ba45c2B686c6db7C2E28BD3a9E8EDd24B894eD": 88,  # Frax 3Pool
        "0x9585a54297beAa83F044866678b13d388D0180bf": 265,  # FraxBP-USX Metapool
        "0x702c1b8Ec3A77009D5898e18DA8F8959B6dF2093": 794,  # Saddle D4Pool
        "0x50d745c2a2918A47A363A2d32becd6BBC1A53ece": 0,  # Saddle USX Pool
        "0x2683190e31e8ce47467c98ff1DBc018aCDD43C2f": 0,  # Saddle sUSD Metapool
        "0x17Bde8EBf1E9FDA85b9Bd1a104266b394E9Db33e": 0,  # Saddle s/w/renBTCV2 Pool
        "0x3dC88ee38db8C7b6DCEB447E4348e51bd87ced93": 0,  # WCUSD Metapool
        "0x7B2025Bf8c5ee8Baad9da8C3E3Ee45E96ed8b8EA": 0,  # Saddle USD Pool
        "0x8B701e9B3a1887fE9b0C7936a8233b39408e69f6": 0,  # Saddle alETH Pool
        "0xB79B4fCF7cB4A1c4064Ff5b48F71A331880ab53a": 0,  # Saddle TBTC Metapool
        # Saddle FraxBP-VesperFrax Metapool
        "0x9980C9b35844946cF3451cC0B43D9b6501F4a96E": 177,
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

    # Send 5M SDL to Minter
    sdl.transfer(MINTER[CHAIN_IDS["MAINNET"]], 5_000_000e18)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 71

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
