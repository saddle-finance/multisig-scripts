import this
from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    MULTISIG_ADDRESSES,
    SDL_ADDRESSES
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract, chain
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "MAINNET"


def main():
    """Buys one tranche of SDL tokens from FraxSwap"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url='https://safe-transaction.optimism.gnosis.io/'
    )

    # Run any pending transactions before simulating any more transactions
    # multisig.preview_pending()

    USDC_MAINNET = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    FRAXSWAP_ROUTER = "0x1C6cA5DEe97C8C368Ca559892CCce2454c8C35C7"

    # fraxswap_router = Contract.from_abi(
    #    "UniV3Router", UNIV3_ROUTER, FRAXSWAP_ROUTER_ABI
    # )

    SDL_contract = Contract.from_abi(
        "ERC20", SDL_ADDRESSES[TARGET_NETWORK], ERC20_ABI
    )
    USDC_contract = Contract.from_abi(
        "ERC20", USDC_MAINNET, ERC20_ABI
    )
    USDC_decimals = USDC_contract.decimals()
    SDL_decimals = SDL_contract.decimals()

    # TODO: Swap 1/3 or multisigs USDC for SDL using FraxSwap

    print(
        "Balances after swap:\n"
        f"USDC: {USDC_contract.balanceOf(multisig.address)/ (10 ** USDC_decimals)}\n" +
        f"WETH: {SDL_contract.balanceOf(multisig.address)/ (10 ** WETH_decimals)}"
    )

    # TODO: set 'safe_nonce'
    safe_tx = multisig.multisend_from_receipts()
    safe_nonce = 0

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    multisig.preview(safe_tx)
    confirm_posting_transaction(multisig, safe_tx)
