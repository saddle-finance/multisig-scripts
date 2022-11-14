import math

from ape_safe import ApeSafe
from brownie import Contract, accounts, network
from helpers import CHAIN_IDS, DEPLOYER_ADDRESS, GAUGE_ABI, GAUGE_CONTROLLER_ADDRESS, MINICHEF_ADDRESSES, MULTISIG_ADDRESSES, OPTIMISM_STANDARD_BRIDGE, SDL_ADDRESSES, SDL_MINTER_ADDRESS

from scripts.utils import confirm_posting_transaction


def main():
    """
    Set Gauge weights for week 09_01_2022 -> 09_08_2022 from results of snapshot vote
    Vote: https://snapshot.org/#/saddlefinance.eth/proposal/0x9c10d4850750b2aa1e377502fa9e6cfbc276ca7dfa5da18190d4bc7f9f7328d9
    Sends SDL to minter for gauge emissions and deployer for Optimism's minichef emissions
    """
    TARGET_NETWORK = "MAINNET"

    print(f"You are using the '{network.show_active()}' network")
    assert network.chain.id == CHAIN_IDS[TARGET_NETWORK], f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    gauge_controller = multisig.contract(
        GAUGE_CONTROLLER_ADDRESS[CHAIN_IDS["MAINNET"]])

    gauge_to_relative_weight_dict = {
        "0xB2Ac3382dA625eb41Fc803b57743f941a484e2a6": 6515,  # FRAXBP Pool
        "0xc64F8A9fe7BabecA66D3997C9d15558BF4817bE3": 1197,  # Sushi SDL/WETH
        "0x953693DCB2E9DDC0c1398C1b540b81b63ceA5e16": 781,  # FraxBP-alUSD Metapool
        "0x104F44551386d603217450822443456229F73aE4": 400,  # FraxBP-sUSD Metapool
        "0x6EC5DD7D8E396973588f0dEFD79dCA04F844d57C": 99,  # FraxBP-USDT Metapool
        "0x13Ba45c2B686c6db7C2E28BD3a9E8EDd24B894eD": 80,  # Frax 3Pool
        "0x9585a54297beAa83F044866678b13d388D0180bf": 427,  # FraxBP-USX Metapool
        "0x702c1b8Ec3A77009D5898e18DA8F8959B6dF2093": 448,  # Saddle D4Pool
        "0x50d745c2a2918A47A363A2d32becd6BBC1A53ece": 0,  # Saddle USX Pool
        "0x2683190e31e8ce47467c98ff1DBc018aCDD43C2f": 52,  # Saddle sUSD Metapool
        "0x17Bde8EBf1E9FDA85b9Bd1a104266b394E9Db33e": 0,  # Saddle s/w/renBTCV2 Pool
        "0x3dC88ee38db8C7b6DCEB447E4348e51bd87ced93": 0,  # WCUSD Metapool
        "0x7B2025Bf8c5ee8Baad9da8C3E3Ee45E96ed8b8EA": 0,  # Saddle USD Pool
        "0x8B701e9B3a1887fE9b0C7936a8233b39408e69f6": 0,  # Saddle alETH Pool
        "0xB79B4fCF7cB4A1c4064Ff5b48F71A331880ab53a": 0,  # Saddle TBTC Metapool
    }

    total_weight = sum(gauge_to_relative_weight_dict.values())
    assert (
        9999 <= total_weight <= 10000
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

    ##### Send 500k SDL to Optimism Minichef #####

    sdl = multisig.contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    # 500k SDL ~= 16 days worth of emissions at 59.3k per day for side chains
    # and 53% of that for Optimism
    amount_to_send_to_deployer = 500_000 * 1e18
    starting_balance = sdl.balanceOf(multisig.address)
    assert (starting_balance >= amount_to_send_to_deployer)

    sdl.transfer(DEPLOYER_ADDRESS, amount_to_send_to_deployer)
    assert (sdl.balanceOf(multisig.address) ==
            starting_balance - amount_to_send_to_deployer), "SDL was not sent"

    ##### Send 5kk SDL to Minter #####

    # Target address
    minter_address = SDL_MINTER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]

    # The amount to send to minter
    amount_to_send_to_minter = 5_000_000 * 1e18
    starting_balance = sdl.balanceOf(multisig.address)
    assert (starting_balance >= amount_to_send_to_minter)

    # Send sdl to minter
    sdl.transfer(minter_address, amount_to_send_to_minter)

    assert (sdl.balanceOf(multisig.address) ==
            starting_balance - amount_to_send_to_minter), "SDL was not sent"

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 58

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
