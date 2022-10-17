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
    """Supplies SDL+ETH to SushiSwap liquidity pool"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url='https://safe-transaction.optimism.gnosis.io/'
    )

    # Run any pending transactions before simulating any more transactions
    # multisig.preview_pending()

    WETH_MAINNET_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    SUSHI_SDL_SLP_ADDRESS = "0x0C6F06b32E6Ae0C110861b8607e67dA594781961"

    sushiswap_router = Contract.from_abi(
        "SushiSwapRouter",
        SUSHISWAP_ROUTER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]],
        SUSHISWAP_ROUTER_ABI
    )

    SDL_contract = Contract.from_abi(
        "SDL", SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]], ERC20_ABI
    )
    WETH_contract = Contract.from_abi(
        "USDC", WETH_MAINNET_ADDRESS, ERC20_ABI
    )
    SLP_contract = Contract.from_abi(
        "SLP", SUSHI_SDL_SLP_ADDRESS, ERC20_ABI
    )
    WETH_decimals = WETH_contract.decimals()
    SDL_decimals = SDL_contract.decimals()
    SLP_decimals = SLP_contract.decimals()

    print(
        "Balances before LP'ing:\n"
        f"WETH: {WETH_contract.balanceOf(multisig.address)/ (10 ** WETH_decimals)}\n" +
        f"SDL: {SDL_contract.balanceOf(multisig.address)/ (10 ** SDL_decimals)}\n" +
        f"SUSHI/WETH SLP: {SLP_contract.balanceOf(multisig.address)/ (10 ** SLP_decimals)}\n" +
        f"SUSHI/WETH SLP total supply: {SLP_contract.totalSupply()/ (10 ** SLP_decimals)}\n\n"
    )

    # approve the router to spend the multisig's WETH
    WETH_contract.approve(
        SUSHISWAP_ROUTER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]],
        2 ** 256 - 1,
        {"from": multisig.address}
    )

    # approve the router to spend the multisig's SDL
    SDL_contract.approve(
        SUSHISWAP_ROUTER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]],
        2 ** 256 - 1,
        {"from": multisig.address}
    )

    # paramters for addLiquidity tx
    tolerance_factor = 0.9
    token_a = WETH_MAINNET_ADDRESS
    token_b = SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    amount_a_desired = WETH_contract.balanceOf(multisig.address)

    # NOTE: SDL amount needs to be adjusted at point of execution, since amount of SDL that was bought
    # with USDC from fees will have changed (and we can't just use the total SDL balance of the multisig)
    amount_b_desired = 2_494_093 * 1e18
    amount_a_min = WETH_contract.balanceOf(multisig.address) * tolerance_factor
    amount_b_min = SDL_contract.balanceOf(multisig.address) * tolerance_factor
    to = multisig.address
    deadline = chain[-1].timestamp + 3600

    # perform swap
    sushiswap_router.addLiquidity(
        token_a,
        token_b,
        amount_a_desired,
        amount_b_desired,
        amount_a_min,
        amount_b_min,
        to,
        deadline,
        {"from": multisig.address}
    )

    print(
        "Balances after LP'ing:\n"
        f"WETH: {WETH_contract.balanceOf(multisig.address)/ (10 ** WETH_decimals)}\n" +
        f"SDL: {SDL_contract.balanceOf(multisig.address)/ (10 ** SDL_decimals)}\n" +
        f"SUSHI/WETH SLP: {SLP_contract.balanceOf(multisig.address)/ (10 ** SLP_decimals)}\n" +
        f"SUSHI/WETH SLP total supply: {SLP_contract.totalSupply()/ (10 ** SLP_decimals)}\n\n"
    )

    # TODO: set 'safe_nonce'
    safe_tx = multisig.multisend_from_receipts()
    safe_nonce = 0

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    multisig.preview(safe_tx)
    confirm_posting_transaction(multisig, safe_tx)
