from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    SUSHISWAP_ROUTER_ABI,
    MULTISIG_ADDRESSES,
    OPS_MULTISIG_ADDRESSES,
    SDL_ADDRESSES,
    SUSHISWAP_ROUTER_ADDRESS
)
from fee_distro_helpers import (
    token_addresses_mainnet,
    SUSHI_SDL_SLP_ADDRESS
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract, chain
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "MAINNET"


def main():
    """Supplies SDL+ETH to SushiSwap liquidity pool via Ops-multisig"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    ops_multisig = ApeSafe(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
    )
    main_multisig_address = MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]

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
    WETH_contract = Contract.from_abi(
        "USDC", token_addresses_mainnet["WETH"], ERC20_ABI
    )
    SLP_contract = Contract.from_abi(
        "SLP", SUSHI_SDL_SLP_ADDRESS, ERC20_ABI
    )
    WETH_decimals = WETH_contract.decimals()
    SDL_decimals = SDL_contract.decimals()
    SLP_decimals = SLP_contract.decimals()

    print(
        "Balances before LP'ing:\n"
        f"WETH: {WETH_contract.balanceOf(ops_multisig.address)/ (10 ** WETH_decimals)}\n" +
        f"SDL: {SDL_contract.balanceOf(ops_multisig.address)/ (10 ** SDL_decimals)}\n" +
        f"SUSHI/WETH SLP: {SLP_contract.balanceOf(ops_multisig.address)/ (10 ** SLP_decimals)}\n" +
        f"SUSHI/WETH SLP total supply: {SLP_contract.totalSupply()/ (10 ** SLP_decimals)}\n\n"
    )

    # approve the router to spend the ops_multisig's WETH
    WETH_contract.approve(
        SUSHISWAP_ROUTER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]],
        2 ** 256 - 1,
        {"from": ops_multisig.address}
    )

    # approve the router to spend the ops_multisig's SDL
    SDL_contract.approve(
        SUSHISWAP_ROUTER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]],
        2 ** 256 - 1,
        {"from": ops_multisig.address}
    )

    # paramters for addLiquidity tx
    tolerance_factor = 0.5
    token_a = token_addresses_mainnet["WETH"]
    token_b = SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    amount_a_desired = WETH_contract.balanceOf(ops_multisig.address)

    # NOTE: we can only take total SDL amount, since we're sending this tx from ops-multisig
    amount_b_desired = SDL_contract.balanceOf(
        ops_multisig.address)
    amount_a_min = WETH_contract.balanceOf(
        ops_multisig.address) * tolerance_factor
    amount_b_min = SDL_contract.balanceOf(
        ops_multisig.address) * tolerance_factor
    to = ops_multisig.address
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
        {"from": ops_multisig.address}
    )

    print(
        "Balances after LP'ing:\n"
        f"WETH: {WETH_contract.balanceOf(ops_multisig.address)/ (10 ** WETH_decimals)}\n" +
        f"SDL: {SDL_contract.balanceOf(ops_multisig.address)/ (10 ** SDL_decimals)}\n" +
        f"SUSHI/WETH SLP: {SLP_contract.balanceOf(ops_multisig.address)/ (10 ** SLP_decimals)}\n" +
        f"SUSHI/WETH SLP total supply: {SLP_contract.totalSupply()/ (10 ** SLP_decimals)}\n\n"
    )

    # send SLP back to main multisig
    balance = SLP_contract.balanceOf(ops_multisig.address)
    SLP_contract.transfer(
        main_multisig_address,
        balance,
        {"from": ops_multisig.address}
    )
    assert SLP_contract.balanceOf(ops_multisig.address) == 0
    assert SLP_contract.balanceOf(main_multisig_address) == balance

    # TODO: set 'safe_nonce'
    safe_tx = ops_multisig.multisend_from_receipts()
    safe_nonce = 0

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    ops_multisig.preview(safe_tx)
    confirm_posting_transaction(ops_multisig, safe_tx)
