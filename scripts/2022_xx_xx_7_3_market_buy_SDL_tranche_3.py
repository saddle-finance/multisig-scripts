import this
from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    SUSHISWAP_ROUTER_ABI,
    MULTISIG_ADDRESSES,
    SDL_ADDRESSES,
    SUSHISWAP_ROUTER_ADDRESS
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract, chain
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "MAINNET"


def main():
    """Buys third tranche of SDL tokens from SushiSwap"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url='https://safe-transaction.optimism.gnosis.io/'
    )

    # Run any pending transactions before simulating any more transactions
    # multisig.preview_pending()

    USDC_MAINNET_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    WETH_MAINNET_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

    sushiswap_router = Contract.from_abi(
        "SushiSwapRouter",
        SUSHISWAP_ROUTER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]],
        SUSHISWAP_ROUTER_ABI
    )

    SDL_contract = Contract.from_abi(
        "SDL", SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]], ERC20_ABI
    )
    USDC_contract = Contract.from_abi(
        "USDC", USDC_MAINNET_ADDRESS, ERC20_ABI
    )
    USDC_decimals = USDC_contract.decimals()
    SDL_decimals = SDL_contract.decimals()

    print(
        "Balances before swap:\n"
        f"USDC: {USDC_contract.balanceOf(multisig.address)/ (10 ** USDC_decimals)}\n" +
        f"SDL: {SDL_contract.balanceOf(multisig.address)/ (10 ** SDL_decimals)}"
    )

    # approve the router to spend the multisig's USDC
    USDC_contract.approve(
        SUSHISWAP_ROUTER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]],
        2 ** 256 - 1,
        {"from": multisig.address}
    )

    # swap 1/4 of *initial* multisig's USDC balance to SDL (which is 1/2 now)
    amount_in = USDC_contract.balanceOf(multisig.address) / 2

    # path to use for swapping
    path = [USDC_MAINNET_ADDRESS,
            WETH_MAINNET_ADDRESS,
            SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
            ]

    # min amount of SDL to receive
    amount_out_min = sushiswap_router.getAmountsOut(
        amount_in,
        path
    )[2]

    to = multisig.address
    deadline = chain[-1].timestamp + 3600

    # perform swap
    sushiswap_router.swapExactTokensForTokens(
        amount_in,
        amount_out_min,
        path,
        to,
        deadline,
        {"from": multisig.address}
    )

    print(
        "Balances after swap:\n"
        f"USDC: {USDC_contract.balanceOf(multisig.address)/ (10 ** USDC_decimals)}\n" +
        f"SDL: {SDL_contract.balanceOf(multisig.address)/ (10 ** SDL_decimals)}"
    )

    # TODO: set 'safe_nonce'
    safe_tx = multisig.multisend_from_receipts()
    safe_nonce = 0

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    multisig.preview(safe_tx)
    confirm_posting_transaction(multisig, safe_tx)
