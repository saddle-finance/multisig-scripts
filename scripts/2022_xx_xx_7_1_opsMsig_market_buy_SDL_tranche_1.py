from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    SUSHISWAP_ROUTER_ABI,
    OPS_MULTISIG_ADDRESSES,
    SDL_ADDRESSES,
    SUSHISWAP_ROUTER_ADDRESS
)
from fee_distro_helpers import (
    token_addresses_mainnet,
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract, chain
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "MAINNET"


def main():
    """Buys first tranche of SDL tokens from SushiSwap via Ops-multisig"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    ops_multisig = ApeSafe(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
    )

    # Run any pending transactions before simulating any more transactions
    # ops_multisig.preview_pending()

    sushiswap_router = Contract.from_abi(
        "SushiSwapRouter",
        SUSHISWAP_ROUTER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]],
        SUSHISWAP_ROUTER_ABI
    )

    SDL_contract = Contract.from_abi(
        "SDL", SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]], ERC20_ABI
    )
    USDC_contract = Contract.from_abi(
        "USDC", token_addresses_mainnet["USDC"], ERC20_ABI
    )
    USDC_decimals = USDC_contract.decimals()
    SDL_decimals = SDL_contract.decimals()

    print(
        "Balances before swap:\n"
        f"USDC: {USDC_contract.balanceOf(ops_multisig.address)/ (10 ** USDC_decimals)}\n" +
        f"SDL: {SDL_contract.balanceOf(ops_multisig.address)/ (10 ** SDL_decimals)}"
    )

    # approve the router to spend ops_multisig's USDC
    USDC_contract.approve(
        SUSHISWAP_ROUTER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]],
        2 ** 256 - 1,
        {"from": ops_multisig.address}
    )

    # swap 1/4 of ops_multisig's USDC balance to SDL
    amount_in = USDC_contract.balanceOf(ops_multisig.address) / 4

    # path to use for swapping
    path = [token_addresses_mainnet["USDC"],
            token_addresses_mainnet["WETH"],
            SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
            ]

    # min amount of SDL to receive
    amount_out_min = sushiswap_router.getAmountsOut(
        amount_in,
        path
    )[2]

    to = ops_multisig.address
    deadline = chain[-1].timestamp + 3600

    # perform swap
    sushiswap_router.swapExactTokensForTokens(
        amount_in,
        amount_out_min,
        path,
        to,
        deadline,
        {"from": ops_multisig.address}
    )

    print(
        "Balances after swap:\n"
        f"USDC: {USDC_contract.balanceOf(ops_multisig.address)/ (10 ** USDC_decimals)}\n" +
        f"SDL: {SDL_contract.balanceOf(ops_multisig.address)/ (10 ** SDL_decimals)}"
    )

    # TODO: set 'safe_nonce'
    safe_tx = ops_multisig.multisend_from_receipts()
    safe_nonce = 0

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    ops_multisig.preview(safe_tx)
    confirm_posting_transaction(ops_multisig, safe_tx)
