from helpers import CHAIN_IDS
from fee_distro_helpers import (
    swap_to_deposit_dicts,
    token_addresses,
    token_to_swap_dicts_saddle,
    univ3_fee_tier_dicts,
    token_to_token_univ3_dicts,
    univ3_route_type_tuples,
    univ3_route_string_tuples,
    MAX_POOL_LENGTH,
    UNIV3_ROUTER_ADDRESSES,
    UNIV3_QUOTER_ADDRESSES,
    SUSHI_SDL_SLP_ADDRESSES
)
from helpers import (
    ERC20_ABI,
    META_SWAP_DEPOSIT_ABI,
    SWAP_ABI,
    META_SWAP_ABI,
    OPS_MULTISIG_ADDRESSES,
    UNIV3_ROUTER_ABI,
    UNIV3_QUOTER_ABI,
    SUSHISWAP_ROUTER_ADDRESSES,
    SUSHISWAP_ROUTER_ABI,
    SDL_ADDRESSES,
)
from eth_abi.packed import encode_abi_packed
from gnosis.safe.safe_tx import SafeTx
from brownie import accounts, network, Contract, chain
import json
import urllib.request
from urllib.error import URLError
import click
from ape_safe import ApeSafe


def confirm_posting_transaction(safe: ApeSafe, safe_tx: SafeTx):
    safe_nonce = safe_tx.safe_nonce

    current_nonce = 0
    try:
        url = safe.base_url + \
            f"/api/v1/safes/{safe.address}/multisig-transactions/"

        # fetch list of txs from gnosis api
        response = urllib.request.urlopen(url)
        data = json.load(response)

        # find last executed tx and set 'curent_nonce' as last executed tx + 1
        for result in data["results"]:
            if result["isExecuted"] == True:
                current_nonce = result["nonce"] + 1
                break
    except (URLError) as err:
        print(f"Fetching txs from gnosis api failed with error: {err}")
        current_nonce = click.prompt(
            "Please input current nonce manually:", type=int)

    pending_nonce = safe.pending_nonce()

    # check if nonce is invalid or already in use
    if safe_nonce == 0:
        if (
            input(
                "Safe nonce is set to 0. This tx will be executed using pending "
                + f"nonce at the time of submission. Continue? [y/N]"
            )
        ) == "N":
            return
        # else:
        # safe_tx.safe_nonce = None
    elif safe_nonce < current_nonce:
        print(
            f"Error: Your nonce ({safe_nonce}) is already used. "
            + f"Please use a nonce greater equal {current_nonce}."
        )
        return
    elif safe_nonce < pending_nonce:
        if (
            input(
                f"There is already a pending transaction at nonce {safe_nonce}. "
                + "Are you sure you want to use duplicate nonce for this submission? [y/N]"
            )
        ) == "N":
            return
    elif safe_nonce > pending_nonce:
        if (
            input(
                f"Your nonce ({safe_nonce}) is greater than current pending nonce "
                + f"({pending_nonce}). Tx won't execute until intermediate nonces have "
                + "been used. Are you sure you want to post submission? [y/N]"
            )
        ) == "N":
            return

    should_post = click.confirm(
        f"Post this gnosis safe transaction to {safe.address} on {safe.base_url}?"
    )
    while True:
        if should_post:
            safe.post_transaction(safe_tx)
            print("Transaction posted to network")
            break
        else:
            should_post = click.confirm(
                f"Post this gnosis safe transaction to {safe.address} on {safe.base_url}?"
            )

# claims admin fees and sends them to ops-multisig on the same chain


def claim_admin_fees(multisig: ApeSafe, chain_id: int):
    ops_multisig_address = OPS_MULTISIG_ADDRESSES[chain_id]
    swap_to_deposit_dict = swap_to_deposit_dicts[chain_id]

    # comprehend set of underlying tokens used by pools on that chain
    collected_token_addresses = set()
    base_LP_addresses = set()
    for swap_address in swap_to_deposit_dict:
        swap_contract = Contract.from_abi("Swap", swap_address, SWAP_ABI)
        if swap_to_deposit_dict[swap_address] == "":  # base pool
            for index in range(MAX_POOL_LENGTH):
                try:
                    collected_token_addresses.add(
                        swap_contract.getToken(index))
                except:
                    break
        else:  # metapool
            # first token in metapool is non-base-pool token
            collected_token_addresses.add(swap_contract.getToken(0))
            base_LP_addresses.add(swap_contract.getToken(1))

    # capture and log token balances of msig before claiming
    token_balances_before = {}
    for token_address in collected_token_addresses:
        token_contract = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        )
        token_balances_before[token_address] = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        ).balanceOf(multisig.address)
        symbol = token_contract.symbol()
        decimals = token_contract.decimals()
        print(
            f"Balance of {symbol} before claiming: {token_balances_before[token_address] / (10 ** decimals)}"
        )

    # execute txs for claiming admin fees
    for swap_address in swap_to_deposit_dict:
        lp_token_address = Contract.from_abi(
            "Swap", swap_address, SWAP_ABI).swapStorage()[6]
        lp_token_name = Contract.from_abi(
            "LPToken", lp_token_address, ERC20_ABI).name()
        print(
            f"Claiming admin fees from {lp_token_name}"
        )
        pool = Contract.from_abi("Swap", swap_address, SWAP_ABI)
        pool.withdrawAdminFees({"from": multisig.address})

    # burn LP tokens of base pools gained from claiming for USDC
    for swap_address in swap_to_deposit_dict:
        metaswap_deposit_address = swap_to_deposit_dict[swap_address]
        if metaswap_deposit_address != "":
            metaswap_contract = Contract.from_abi(
                "MetaSwap", swap_address, META_SWAP_ABI
            )
            metaswap_deposit_contract = Contract.from_abi(
                "MetaSwapDeposit", metaswap_deposit_address, META_SWAP_DEPOSIT_ABI
            )
            base_pool_LP_address = metaswap_contract.getToken(1)
            base_pool_LP_contract = Contract.from_abi(
                "LPToken", base_pool_LP_address, ERC20_ABI
            )
            LP_balance = base_pool_LP_contract.balanceOf(multisig.address)
            if LP_balance > 0:
                base_swap_address = metaswap_deposit_contract.baseSwap()
                base_swap = Contract.from_abi(
                    "BaseSwap", base_swap_address, SWAP_ABI
                )
                # approve amount to burn
                print(
                    f"Approving base pool for {base_pool_LP_contract.symbol()} {LP_balance}"
                )
                base_pool_LP_contract.approve(
                    base_swap,
                    LP_balance,
                    {"from": multisig.address}
                )
                print(
                    f"Burning {LP_balance} {base_pool_LP_contract.symbol()} for USDC or underlyings"
                )
                deadline = chain[chain.height].timestamp + 3600
                # if on mainnet, burn for individual underlyings
                if chain_id == 1:
                    # calculate min amounts to receive
                    min_amounts = base_swap.calculateRemoveLiquidity(
                        LP_balance
                    )
                    base_swap.removeLiquidity(
                        LP_balance,
                        min_amounts,
                        deadline,
                        {"from": multisig.address}
                    )
                # if on side chains, burn for USDC only
                else:
                    token_index_USDC = base_swap.getTokenIndex(
                        token_addresses[chain_id]["USDC"])
                    min_amount = base_swap.calculateRemoveLiquidityOneToken(
                        LP_balance,
                        token_index_USDC
                    )

                    base_swap.removeLiquidityOneToken(
                        LP_balance,
                        token_index_USDC,
                        min_amount,
                        deadline,
                        {"from": multisig.address}
                    )

    # capture and log token balances of msig after swapping
    token_balances_after = {}
    for token_address in collected_token_addresses:
        token_contract = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        )
        symbol = token_contract.symbol()
        balance = token_contract.balanceOf(multisig.address)
        token_balances_after[token_address] = token_contract.balanceOf(
            multisig.address)
        decimals = token_contract.decimals()
        print(
            f"Balance of {symbol} after swapping: {token_balances_after[token_address] / (10 ** decimals)}"
        )

    # send tokens to ops multisig
    for token_address in collected_token_addresses:
        token_contract = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        )
        symbol = token_contract.symbol()
        balance = token_contract.balanceOf(multisig.address)
        decimals = token_contract.decimals()
        if balance > 0:
            print(
                f"Sending {balance / (10 ** decimals)} {symbol} to ops multisig"
            )
            token_contract.transfer(
                ops_multisig_address,
                balance,
                {"from": multisig.address}
            )
        assert token_contract.balanceOf(multisig.address) == 0
        assert token_contract.balanceOf(ops_multisig_address) >= balance


def convert_fees_to_USDC_saddle(ops_multisig: ApeSafe, chain_id: int):
    swap_to_deposit_dict = swap_to_deposit_dicts[chain_id]
    specific_token_addresses = token_addresses[chain_id]
    token_to_swap_dict = token_to_swap_dicts_saddle[chain_id]

    # comprehend set of underlying tokens used by pools on that chain
    collected_token_addresses = set()
    base_LP_addresses = set()
    for swap_address in swap_to_deposit_dict:
        swap_contract = Contract.from_abi("Swap", swap_address, SWAP_ABI)
        if swap_to_deposit_dict[swap_address] == "":  # base pool
            for index in range(MAX_POOL_LENGTH):
                try:
                    collected_token_addresses.add(
                        swap_contract.getToken(index))
                except:
                    break
        else:  # metapool
            # first token in metapool is non-base-pool token
            collected_token_addresses.add(swap_contract.getToken(0))
            base_LP_addresses.add(swap_contract.getToken(1))

    # capture and log token balances of ops msig before swapping
    token_balances_before = {}
    for token_address in collected_token_addresses:
        token_contract = Contract.from_abi("ERC20", token_address, ERC20_ABI)
        token_balances_before[token_address] = token_contract.balanceOf(
            ops_multisig.address)
        symbol = token_contract.symbol()
        decimals = token_contract.decimals()
        print(
            f"Balance of {symbol} before swapping: {token_balances_before[token_address] / (10 ** decimals)}"
        )

    # convert all collected fees to USDC, to minimize # of claiming txs on L1
    for token_address in collected_token_addresses:
        # skip USDC, since it's the target
        if token_address == specific_token_addresses["USDC"]:
            continue

        # amount to swap
        amount_to_swap = token_balances_before[token_address]

        # skip if no fees were claimed
        if amount_to_swap > 0:
            # get swap and token indices
            # if base pool, use base pool for swapping
            if swap_to_deposit_dict[token_to_swap_dict[token_address]] == "":
                swap_address = token_to_swap_dict[token_address]
                # Base swap for swapping
                swap = Contract.from_abi(
                    "Swap", swap_address, SWAP_ABI
                )
                # get token indices from base pool contract
                token_index_from = swap.getTokenIndex(token_address)
                token_index_to = swap.getTokenIndex(
                    specific_token_addresses["USDC"])

            # if metapool, use metapool deposit for swapping
            else:
                swap_address = swap_to_deposit_dict[token_to_swap_dict[token_address]]
                # Metaswap deposit for swapping
                swap = Contract.from_abi(
                    "MetaSwapDeposit", swap_address, SWAP_ABI
                )
                # get (flattened) token indices from underlying swap contract
                meta_swap = Contract.from_abi(
                    "MetaSwap", token_to_swap_dict[token_address], META_SWAP_ABI
                )
                base_swap = Contract.from_abi(
                    "BaseSwap", meta_swap.metaSwapStorage()[0], SWAP_ABI
                )
                base_token_index_to = base_swap.getTokenIndex(
                    specific_token_addresses["USDC"])
                token_index_from = 0  # index 0 is non-base-pool token
                # offset by one for flattened 'to' token index
                token_index_to = 1 + base_token_index_to

            # deadline 1h from now
            deadline = chain[chain.height].timestamp + 3600

            # min amount to receive
            min_amount = swap.calculateSwap(
                token_index_from,
                token_index_to,
                amount_to_swap
            )

            # approve amount to swap
            token_contract = Contract.from_abi(
                "ERC20", token_address, ERC20_ABI
            )
            print(
                f"Approving {token_contract.symbol()} for saddle pool"
            )
            token_contract.approve(
                swap_address,
                amount_to_swap,
                {"from": ops_multisig.address}
            )

            # perform swap
            print(
                f"Swapping {amount_to_swap / (10 ** token_contract.decimals())} {token_contract.symbol()} to USDC (or wBTC/WETH on mainnet)"
            )
            swap.swap(
                token_index_from,
                token_index_to,
                amount_to_swap,
                min_amount,
                deadline,
                {"from": ops_multisig.address}
            )
    return collected_token_addresses


def convert_fees_to_USDC_uniswap(ops_multisig: ApeSafe, chain_id: int, collected_token_addresses: set):
    # capture and log token balances of msig
    # after claiming, burning and swapping via saddle
    print(
        f"Balances of tokens before swapping with Uniswap:"
    )
    univ3_router = Contract.from_abi(
        "UniV3Router", UNIV3_ROUTER_ADDRESSES, UNIV3_ROUTER_ABI
    )
    univ3_quoter = Contract.from_abi(
        "UniV3Quoter", UNIV3_QUOTER_ADDRESSES, UNIV3_QUOTER_ABI
    )
    univ3_fee_tier_dict = univ3_fee_tier_dicts[chain_id]
    token_to_token_univ3_dict = token_to_token_univ3_dicts[chain_id]
    token_balances_after_saddle_swap = {}
    for token_address in collected_token_addresses:
        token_contract = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        )
        symbol = token_contract.symbol()
        token_balances_after_saddle_swap[token_address] = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        ).balanceOf(ops_multisig.address)
        print(
            f"Balance of {symbol}: {token_balances_after_saddle_swap[token_address] / (10 ** token_contract.decimals())}"
        )

    # swap all remaining tokens that are not USDC into USDC via UniswapV3
    for token_address in token_to_token_univ3_dict.keys():
        balance = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        ).balanceOf(ops_multisig.address)
        # skip if balance is 0
        if balance == 0:
            continue

        token_from = token_address
        token_to = token_to_token_univ3_dict[token_address]
        fee = univ3_fee_tier_dict[token_from]
        recipient = ops_multisig.address
        deadline = chain[chain.height].timestamp + 3600
        amount_in = token_balances_after_saddle_swap[token_from]
        sqrt_price_limit_X96 = 0

        # approve Univ3 router
        print(
            f"Approve UniV3 router for ${token_contract.symbol()} {amount_in / (10 ** token_contract.decimals())}"
        )
        token_contract = Contract.from_abi("ERC20", token_address, ERC20_ABI)
        token_contract.approve(
            UNIV3_ROUTER_ADDRESSES[chain_id],
            amount_in,
            {"from": ops_multisig.address}
        )
        print(
            f"Getting quote for ${token_contract.symbol()}"
        )

        # getting min amounts
        amount_out_min = 0
        params = ()

        # in case we want to use a multi-hop route
        if token_address in univ3_route_type_tuples[chain_id]:
            route_type_tuple = univ3_route_type_tuples[chain_id][token_addresses[chain_id][token_address]]
            route_string_tuple = univ3_route_string_tuples[
                chain_id][token_addresses[chain_id][token_address]]
            route_encoded = encode_abi_packed(
                route_type_tuple, route_string_tuple)
            amount_out_min = univ3_quoter.quoteExactInput(
                route_encoded,
                amount_in,
                {"from": ops_multisig.address}
            ).return_value
            print(
                f"Quote for ${token_contract.symbol()}: {amount_out_min / (10 ** token_contract.decimals())}"
            )
            # input struct for exactInput swap
            params = (
                route_encoded,
                recipient,
                deadline,
                amount_in,
                amount_out_min,
            )
            # swap using univ3
            print(
                f"Swap {amount_in / (10 ** token_contract.decimals())} ${token_contract.symbol()} for $USDC on UniV3"
            )
            univ3_router.exactInput(
                params,
                {"from": ops_multisig.address}
            )
        # in case we have a direct pairing between the token and USDC
        else:
            amount_out_min = univ3_quoter.quoteExactInputSingle(
                token_from,
                token_to,
                fee,
                amount_in,
                sqrt_price_limit_X96,
                {"from": ops_multisig.address}
            ).return_value
            print(
                f"Quote for ${token_contract.symbol()}: {amount_out_min / (10 ** token_contract.decimals())}"
            )
            # input struct for exactInputSingle swap
            params = (
                token_from,
                token_to,
                fee,
                recipient,
                deadline,
                amount_in,
                amount_out_min,
                sqrt_price_limit_X96
            )
            # swap using univ3
            print(
                f"Swap {amount_in / (10 ** token_contract.decimals())} ${token_contract.symbol()} for $USDC on UniV3"
            )
            univ3_router.exactInputSingle(
                params,
                {"from": ops_multisig.address}
            )

    # capture and log token balances of msig after claiming and burning
    print(
        f"Final balances in Ops-Multisig after claiming, burning, swapping via saddle and UniswapV3:"
    )
    token_balances_final = {}
    for token_address in collected_token_addresses:
        token_contract = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        )
        symbol = token_contract.symbol()
        token_balances_final[token_address] = token_contract.balanceOf(
            ops_multisig.address
        )
        decimals = token_contract.decimals()
        print(
            f"Balance of ${symbol} : {token_balances_final[token_address] / (10 ** decimals)}"
        )


def buy_sdl_with_usdc_sushi(ops_multisig: ApeSafe, chain_id: int, divisor: int = 1):
    sushiswap_router = Contract.from_abi(
        "SushiSwapRouter",
        SUSHISWAP_ROUTER_ADDRESSES[chain_id],
        SUSHISWAP_ROUTER_ABI
    )

    SDL_contract = Contract.from_abi(
        "SDL", SDL_ADDRESSES[CHAIN_IDS[chain_id]], ERC20_ABI
    )
    USDC_contract = Contract.from_abi(
        "USDC", token_addresses[chain_id]["USDC"], ERC20_ABI
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
        SUSHISWAP_ROUTER_ADDRESSES[chain_id],
        2 ** 256 - 1,
        {"from": ops_multisig.address}
    )

    # swap 1/4 of ops_multisig's USDC balance to SDL
    amount_in = USDC_contract.balanceOf(ops_multisig.address) / divisor

    # path to use for swapping
    path = [token_addresses[chain_id]["USDC"],
            token_addresses[chain_id]["WETH"],
            SDL_ADDRESSES[chain_id]
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


def provide_sdl_eth_lp_sushi(ops_multisig: ApeSafe, multisig: ApeSafe, chain_id: int):
    sushiswap_router = Contract.from_abi(
        "SushiSwapRouter",
        SUSHISWAP_ROUTER_ADDRESSES[chain_id],
        SUSHISWAP_ROUTER_ABI
    )

    SDL_contract = Contract.from_abi(
        "SDL", SDL_ADDRESSES[chain_id], ERC20_ABI
    )
    WETH_contract = Contract.from_abi(
        "USDC", token_addresses[chain_id]["WETH"], ERC20_ABI
    )
    SLP_contract = Contract.from_abi(
        "SLP", SUSHI_SDL_SLP_ADDRESSES[chain_id], ERC20_ABI
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
        SUSHISWAP_ROUTER_ADDRESSES[chain_id],
        2 ** 256 - 1,
        {"from": ops_multisig.address}
    )

    # approve the router to spend the ops_multisig's SDL
    SDL_contract.approve(
        SUSHISWAP_ROUTER_ADDRESSES[chain_id],
        2 ** 256 - 1,
        {"from": ops_multisig.address}
    )

    # paramters for addLiquidity tx
    tolerance_factor = 0.5
    token_a = token_addresses[chain_id]["WETH"]
    token_b = SDL_ADDRESSES[chain_id]
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
        multisig.address,
        balance,
        {"from": ops_multisig.address}
    )
    assert SLP_contract.balanceOf(ops_multisig.address) == 0
    assert SLP_contract.balanceOf(multisig.address) == balance


def convert_string_to_bytes32(string: str) -> bytes:
    """
    Encodes a string to bytes32 format. 

    If the string is shorter than 32 bytes, it will be right-padded with 0s. 
    Otherwise, it will be truncated.
    """
    return string.encode("utf-8").ljust(32, b"\x00")
