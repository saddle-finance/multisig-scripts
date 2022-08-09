from helpers import (
    CHAIN_IDS,
    GAUGE_ABI,
    GAUGE_CONTROLLER_ADDRESS,
    MULTISIG_ADDRESSES,
    OWNERS,
    SDL_ADDRESSES,
    SDL_MINTER_ADDRESS,
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract

from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():
    """Update a vesting contract's ownership to company multisig"""

    print(f"You are using the '{network.show_active()}' network")

    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    safe_contract = multisig.contract(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    Kain_Warwick = "0x5b97680e165b4dbf5c45f4ff4241e85f418c66c2"

    # prev owner(pointer), old owner, new owner
    safe_contract.swapOwner(OWNERS[4], Kain_Warwick, OWNERS[5])

    # new owner, threshold
    safe_contract.addOwnerWithThreshold(OWNERS[0], 3)
    assert safe_contract.getOwners() == OWNERS

    # The amount to send to minter
    amount_to_send = 5_000_000 * 1e18

    # Target address
    minter_address = SDL_MINTER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]

    # Send sdl to minter
    sdl = multisig.contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    sdl.transfer(minter_address, amount_to_send)

    # Gauge weight changes for 8/11 - 8/18
    gauge_controller = multisig.contract(
        GAUGE_CONTROLLER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]
    )

    gauge_to_relative_weight_dict = {
        "0xB2Ac3382dA625eb41Fc803b57743f941a484e2a6": 7433,  # FRAXBP Pool
        "0xc64F8A9fe7BabecA66D3997C9d15558BF4817bE3": 611,  # Sushi SDL/WETH
        "0x953693DCB2E9DDC0c1398C1b540b81b63ceA5e16": 604,  # alUSDFRAX Metapool
        "0x104F44551386d603217450822443456229F73aE4": 438,  # sUSDFRAX Metapool
        "0x6EC5DD7D8E396973588f0dEFD79dCA04F844d57C": 270,  # FRAXUSDT Metapool
        "0x13Ba45c2B686c6db7C2E28BD3a9E8EDd24B894eD": 88,  # Frax 3Pool
        "0x9585a54297beAa83F044866678b13d388D0180bf": 135,  # Frax USX Metapool
        "0x702c1b8Ec3A77009D5898e18DA8F8959B6dF2093": 235,  # Saddle D4Pool
        "0x50d745c2a2918A47A363A2d32becd6BBC1A53ece": 138,  # Saddle USX Pool
        "0x2683190e31e8ce47467c98ff1DBc018aCDD43C2f": 48,  # Saddle sUSD Metapool
        "0x17Bde8EBf1E9FDA85b9Bd1a104266b394E9Db33e": 0,  # Saddle s/w/renBTCV2 Pool
        "0x3dC88ee38db8C7b6DCEB447E4348e51bd87ced93": 0,  # WCUSD Metapool
        "0x7B2025Bf8c5ee8Baad9da8C3E3Ee45E96ed8b8EA": 0,  # Saddle USD Pool
        "0x8B701e9B3a1887fE9b0C7936a8233b39408e69f6": 0,  # Saddle alETH Pool
        "0xB79B4fCF7cB4A1c4064Ff5b48F71A331880ab53a": 0,  # Saddle TBTC Metapool
    }

    total_weight = sum(gauge_to_relative_weight_dict.values())
    assert total_weight == 10000, f"Total weight must be 10000 but is {total_weight}"

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
    assert total_weight == 10000, f"Total weight must be 10000 but is {total_weight}"

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 54

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
