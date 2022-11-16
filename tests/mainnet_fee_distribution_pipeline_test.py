import this
from helpers import (
    SDL_ADDRESSES,
    CHAIN_IDS,
    ERC20_ABI,
    META_SWAP_DEPOSIT_ABI,
    MULTISIG_ADDRESSES,
    SWAP_ABI,
    META_SWAP_ABI,
    UNIV3_ROUTER_ABI,
    UNIV3_QUOTER_ABI,
    SUSHISWAP_ROUTER_ABI,
    SUSHISWAP_ROUTER_ADDRESS,
    OPS_MULTISIG_ADDRESSES
)
from fee_distro_helpers import (
    token_to_swap_dict_saddle,
    token_addresses_mainnet,
    token_to_token_univ3_dict,
    swap_to_deposit_dict,
    SUSHI_SDL_SLP_ADDRESS,
    MAX_POOL_LENGTH,
    UNIV3_ROUTER,
    UNIV3_QUOTER
)
from eth_abi.packed import encode_abi_packed
from ape_safe import ApeSafe
from brownie import accounts, network, Contract, chain
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "MAINNET"


# This script concatenates all mainnet scripts (5 to 8) and impersonates
# ops-multisig with deployer EOA, since we don't yet have an ops-multisig
# @dev  All instances in the original scripts of ops ApeSafe.address
# ('ops_multisig_address') are replaced by simple 'ops_multisig_address'

def main():
    """This script claims admin fees from all Mainnet pools,
    then converts them to SDL/ETH SLP and sends it to main multisig for distribution
    Steps are:
    1. Claim admin fees on all pools
    2. Burn claimed LPs to get underlyings and send them to ops multisig
    3. Swap assets into USDC, WBTC, WETH using Saddle, if possible
    4. Swap remaining assets into USDC, using UniswapV3
    5. Buy SDL+ETH 50/50 and LP in Sushi pool
    6. Send SDL/ETH SLP to main multisig for distribution
    """

    #####################################################################
    ############# 2022_xx_xx_5_mainnet_claim_admin_fees.py ##############
    #####################################################################

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
    )
    ops_multisig_address = OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]

    # Run any pending transactions before simulating any more transactions
    # multisig.preview_pending()

    # comprehend set of underlying tokens used by pools on that chain
    token_addresses = set()
    for swap_address in swap_to_deposit_dict:
        swap_contract = Contract.from_abi("Swap", swap_address, SWAP_ABI)
        if swap_to_deposit_dict[swap_address] == "":  # base pool
            for index in range(MAX_POOL_LENGTH):
                try:
                    token_addresses.add(swap_contract.getToken(index))
                except:
                    break
        else:  # metapool
            # first token in metapool is non-base-pool token
            token_addresses.add(swap_contract.getToken(0))

    # capture and log token balances of msig before claiming
    token_balances_before = {}
    for token_address in token_addresses:
        token_contract = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        )
        symbol = token_contract.symbol()
        token_balances_before[token_address] = token_contract.balanceOf(
            multisig.address
        )
        decimals = token_contract.decimals()
        print(
            f"Balance of {symbol} before claiming: {token_balances_before[token_address] / 10**decimals}"
        )

    # execute txs for claiming admin fees
    for swap_address in swap_to_deposit_dict:
        lp_token_address = Contract.from_abi(
            "Swap", swap_address, SWAP_ABI
        ).swapStorage()[6]
        lp_token_name = Contract.from_abi(
            "LPToken", lp_token_address, ERC20_ABI
        ).name()
        print(
            f"Claiming admin fees from {lp_token_name}"
        )
        pool = Contract.from_abi("Swap", swap_address, SWAP_ABI)
        pool.withdrawAdminFees({"from": multisig.address})

    # burn LP tokens of base pools for underlyings
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
                # calculate min amounts to receive
                min_amounts = base_swap.calculateRemoveLiquidity(
                    LP_balance
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
                # burn LP token
                print(
                    f"Burning {LP_balance} {base_pool_LP_contract.symbol()} for balanced underlyings"
                )
                deadline = chain[chain.height].timestamp + 3600
                base_swap.removeLiquidity(
                    LP_balance,
                    min_amounts,
                    deadline,
                    {"from": multisig.address}
                )

    # capture and log token balances of msig after claiming and burning
    print(
        f"Balances of tokens after claiming and burning:"
    )
    token_balances_after_claim_burn = {}
    for token_address in token_addresses:
        token_contract = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        )
        symbol = token_contract.symbol()
        token_balances_after_claim_burn[token_address] = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        ).balanceOf(multisig.address)
        print(
            f"Balance of {symbol}: {token_balances_after_claim_burn[token_address] / (10 ** token_contract.decimals())}"
        )

    # log claimed amounts
    for token_address in token_addresses:
        symbol = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        ).symbol()
        print(
            f"Claimed {symbol}: {(token_balances_after_claim_burn[token_address] - token_balances_before[token_address])}"
        )

    # send fee tokens to operations multisig
    for token_address in token_addresses:
        token_contract = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        )
        symbol = token_contract.symbol()

        # send 100% of claimed tokens to operations multisig
        balance = token_contract.balanceOf(multisig.address)
        if balance > 0:
            print(
                f"Sending {symbol} to operations multisig"
            )
            # send tokens to operations multisig
            token_contract.transfer(
                ops_multisig_address,
                balance,
                {"from": multisig.address}
            )
        assert token_contract.balanceOf(multisig.address) == 0
        # @dev changed from '==' to '>=' due to deployer EOA having some tokens
        assert token_contract.balanceOf(ops_multisig_address) >= balance

    #####################################################################
    ############# 2022_xx_xx_6_opsMsig_swap_fees_to_USDC.py #############
    #####################################################################

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"

    # ops_multisig = ApeSafe(
    #    OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    # )

    # @dev using EOA address instead of ApeSafe object for testing
    ops_multisig_address = OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]

    # Run any pending transactions before simulating any more transactions
    # ops_multisig.preview_pending()

    univ3_router = Contract.from_abi(
        "UniV3Router", UNIV3_ROUTER, UNIV3_ROUTER_ABI
    )
    univ3_quoter = Contract.from_abi(
        "UniV3Quoter", UNIV3_QUOTER, UNIV3_QUOTER_ABI
    )
    univ3_fee_tier_dict = {
        token_addresses_mainnet["WETH"]: int(3000),
        token_addresses_mainnet["WBTC"]: int(3000),
        token_addresses_mainnet["FEI"]: int(500),
        token_addresses_mainnet["DAI"]: int(500),
        token_addresses_mainnet["LUSD"]: int(500)
    }

    # comprehend set of underlying tokens used by pools on that chain
    token_addresses = set()
    # base_LP_addresses = set()
    for swap_address in swap_to_deposit_dict:
        swap_contract = Contract.from_abi("Swap", swap_address, SWAP_ABI)
        if swap_to_deposit_dict[swap_address] == "":  # base pool
            for index in range(MAX_POOL_LENGTH):
                try:
                    token_addresses.add(swap_contract.getToken(index))
                except:
                    break
        else:  # metapool
            # first token in metapool is non-base-pool token
            token_addresses.add(swap_contract.getToken(0))
            # base_LP_addresses.add(swap_contract.getToken(1))

    # capture and log token balances of msig before claiming
    token_balances_before = {}
    for token_address in token_addresses:
        token_contract = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        )
        symbol = token_contract.symbol()
        token_balances_before[token_address] = token_contract.balanceOf(
            ops_multisig_address
        )
        decimals = token_contract.decimals()
        print(
            f"Balance of {symbol} before claiming: {token_balances_before[token_address] / 10**decimals}"
        )

    # @dev done from operations ops_multisig
    # swap all tokens that a are swappable via Saddle to USDC/WBTC/WETH
    for token_address in token_to_swap_dict_saddle.keys():
        token_contract = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        )

        # swap 100% of holdings
        amount_to_swap = token_contract.balanceOf(
            ops_multisig_address)  # debug: changed for testing

        # skip if no fees were claimed
        if amount_to_swap > 0:
            # get swap and token indices
            # if base pool, use base pool for swapping
            if swap_to_deposit_dict[token_to_swap_dict_saddle[token_address][1]] == "":
                swap_address = token_to_swap_dict_saddle[token_address][1]
                # Base swap for swapping
                swap = Contract.from_abi(
                    "Swap", swap_address, SWAP_ABI
                )
                # get token indices from base pool contract
                token_index_from = swap.getTokenIndex(token_address)
                token_index_to = swap.getTokenIndex(
                    token_to_swap_dict_saddle[token_address][0]
                )

            # if metapool, use metapool deposit for swapping
            else:
                swap_address = swap_to_deposit_dict[token_to_swap_dict_saddle[token_address][1]]
                # Metaswap deposit for swapping
                swap = Contract.from_abi(
                    "MetaSwapDeposit", swap_address, SWAP_ABI
                )
                # get (flattened) token indices from underlying swap contract
                meta_swap = Contract.from_abi(
                    "MetaSwap", token_to_swap_dict_saddle[token_address][1], META_SWAP_ABI
                )
                base_swap = Contract.from_abi(
                    "BaseSwap", meta_swap.metaSwapStorage()[0], SWAP_ABI
                )
                base_token_index_to = base_swap.getTokenIndex(
                    token_to_swap_dict_saddle[token_address][0]
                )
                token_index_from = 0  # index 0 is non-base-pool token
                # offset by one for flattened 'to' token index
                token_index_to = 1 + base_token_index_to

            # deadline 1 hour from now
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
                f"Approving swap for ${token_contract.symbol()} {amount_to_swap / (10 ** token_contract.decimals())}"
            )
            token_contract.approve(
                swap_address,
                amount_to_swap,
                {"from": ops_multisig_address}  # debug: changed for testing
            )

            # perform swap
            print(
                f"Swapping {amount_to_swap / (10 ** token_contract.decimals())} ${token_contract.symbol()} to $USDC (or wBTC or wETH)"
            )
            swap.swap(
                token_index_from,
                token_index_to,
                amount_to_swap,
                min_amount,
                deadline,
                {"from": ops_multisig_address}  # debug: changed for testing
            )

    # capture and log token balances of msig
    # after claiming, burning and swapping via saddle
    print(
        f"Balances of tokens after claiming, burning, swapping via saddle"
    )
    token_balances_after_saddle_swap = {}
    for token_address in token_addresses:
        token_contract = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        )
        symbol = token_contract.symbol()
        token_balances_after_saddle_swap[token_address] = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        ).balanceOf(ops_multisig_address)  # debug: changed for testing
        print(
            f"Balance of {symbol}: {token_balances_after_saddle_swap[token_address] / (10 ** token_contract.decimals())}"
        )

    # swap all remaining tokens that are not USDC into USDC via UniswapV3
    for token_address in token_to_token_univ3_dict.keys():
        token_from = token_address
        token_to = token_to_token_univ3_dict[token_address]
        fee = univ3_fee_tier_dict[token_from]
        recipient = ops_multisig_address  # debug: changed for testing
        deadline = chain[chain.height].timestamp + 3600
        amount_in = token_balances_after_saddle_swap[token_from]
        sqrt_price_limit_X96 = 0

        # approve Univ3 router
        print(
            f"Approve UniV3 router for ${token_contract.symbol()} {amount_in / (10 ** token_contract.decimals())}"
        )
        token_contract = Contract.from_abi("ERC20", token_address, ERC20_ABI)
        token_contract.approve(
            UNIV3_ROUTER,
            amount_in,
            {"from": ops_multisig_address}  # debug: changed for testing
        )
        print(
            f"Getting quote for ${token_contract.symbol()}"
        )

        # getting min amounts
        amount_out_min = 0
        params = ()
        # in case of FEI we need to hop to DAI first due to low liq on FEI/USDC
        if token_address == token_addresses_mainnet["FEI"]:
            route_types = ['address', 'uint24', 'address', 'uint24', 'address']
            # route FEI -> DAI -> USDC
            route_tuple = (str(token_addresses_mainnet["FEI"]),
                           univ3_fee_tier_dict[token_addresses_mainnet["FEI"]],
                           str(token_addresses_mainnet["DAI"]),
                           univ3_fee_tier_dict[token_addresses_mainnet["DAI"]],
                           str(token_addresses_mainnet["USDC"]))
            route_encoded = encode_abi_packed(route_types, route_tuple)
            amount_out_min = univ3_quoter.quoteExactInput(
                route_encoded,
                amount_in,
                {"from": multisig.address}
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
                {"from": ops_multisig_address}  # debug: changed for testing
            )
        else:
            amount_out_min = univ3_quoter.quoteExactInputSingle(
                token_from,
                token_to,
                fee,
                amount_in,
                sqrt_price_limit_X96,
                {"from": ops_multisig_address}  # debug: changed for testing
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
                {"from": ops_multisig_address}  # debug: changed for testing
            )

    # capture and log token balances of msig after claiming and burning
    print(
        f"Final balances in Ops-Multisig after claiming, burning, swapping via saddle and UniswapV3:"
    )
    token_balances_final = {}
    for token_address in token_addresses:
        token_contract = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        )
        symbol = token_contract.symbol()
        token_balances_final[token_address] = token_contract.balanceOf(
            ops_multisig_address  # debug: changed for testing
        )
        decimals = token_contract.decimals()
        print(
            f"Balance of ${symbol} : {token_balances_final[token_address] / (10 ** decimals)}"
        )

    #####################################################################
    ######## 2022_xx_xx_7_0_opsMsig_market_buy_WETH_with_USDC.py ########
    #####################################################################

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    # ops_multisig = ApeSafe(
    #    OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    # )

    # @dev using EOA address instead of ApeSafe object for testing
    ops_multisig_address = OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]

    # Run any pending transactions before simulating any more transactions
    # ops_multisig.preview_pending()

    univ3_router = Contract.from_abi(
        "UniV3Router", UNIV3_ROUTER, UNIV3_ROUTER_ABI
    )
    univ3_quoter = Contract.from_abi(
        "UniV3Quoter", UNIV3_QUOTER, UNIV3_QUOTER_ABI
    )

    USDC_contract = Contract.from_abi(
        "ERC20", token_addresses_mainnet["USDC"], ERC20_ABI
    )
    WETH_contract = Contract.from_abi(
        "ERC20", token_addresses_mainnet["WETH"], ERC20_ABI
    )
    USDC_decimals = USDC_contract.decimals()
    WETH_decimals = WETH_contract.decimals()

    USDC_balance_before = USDC_contract.balanceOf(ops_multisig_address)

    token_from_address = token_addresses_mainnet["USDC"]
    token_to_address = token_addresses_mainnet["WETH"]
    fee = 500
    recipient = ops_multisig_address
    deadline = chain[chain.height].timestamp + 3600  # 1 hour
    sqrt_price_limit_X96 = 0

    # Swap ~50% of ops_multisig's USDC for WETH.
    # factor to correct for price increases of SDL through tranch buys,
    # requiring less and less SDL to provide liq in optimal ratio.

    # TODO: adjust factor before executing, s.t. minimal SDL or WETH is left
    # after LPing
    SDL_price_impact_factor = 1.3
    amount_in = USDC_contract.balanceOf(
        ops_multisig_address
    ) / 2 * SDL_price_impact_factor

    # getting min amounts
    print(
        f"Getting quote for WETH"
    )
    amount_out_min = univ3_quoter.quoteExactInputSingle(
        token_from_address,
        token_to_address,
        fee,
        amount_in,
        sqrt_price_limit_X96,
        {"from": ops_multisig_address}
    ).return_value

    # input struct for univ3 swap
    params = (
        token_from_address,
        token_to_address,
        fee,
        recipient,
        deadline,
        amount_in,
        amount_out_min,
        sqrt_price_limit_X96
    )

    # approve Univ3 router
    print(
        f"Approve UniV3 router for USDC {amount_in / (10 ** USDC_decimals)}"
    )
    USDC_contract.approve(
        UNIV3_ROUTER,
        amount_in,
        {"from": ops_multisig_address}
    )

    # swap using univ3
    print(
        f"Swap {amount_in / (10 ** USDC_decimals)} USDC for WETH on UniV3"
    )
    univ3_router.exactInputSingle(
        params,
        {"from": ops_multisig_address}
    )

    USDC_balance_after = USDC_contract.balanceOf(ops_multisig_address)

    assert (USDC_balance_after < 0.51 * USDC_balance_before * SDL_price_impact_factor and
            USDC_balance_after > 0.49 * USDC_balance_before * (1 - SDL_price_impact_factor))

    print(
        "Balances after swap:\n"
        f"USDC: {USDC_contract.balanceOf(ops_multisig_address)/ (10 ** USDC_decimals)}\n" +
        f"WETH: {WETH_contract.balanceOf(ops_multisig_address)/ (10 ** WETH_decimals)}"
    )

    #####################################################################
    ######## 2022_xx_xx_7_1_opsMsig_market_buy_SDL_tranche_1.py #########
    #####################################################################

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    # ops_multisig = ApeSafe(
    #    OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    # )

    # @dev using EOA address instead of ApeSafe object for testing
    ops_multisig_address = OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]

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
        f"USDC: {USDC_contract.balanceOf(ops_multisig_address)/ (10 ** USDC_decimals)}\n" +
        f"SDL: {SDL_contract.balanceOf(ops_multisig_address)/ (10 ** SDL_decimals)}"
    )

    # approve the router to spend ops_multisig's USDC
    USDC_contract.approve(
        SUSHISWAP_ROUTER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]],
        2 ** 256 - 1,
        {"from": ops_multisig_address}
    )

    # swap 1/4 of ops_multisig's USDC balance to SDL
    amount_in = USDC_contract.balanceOf(ops_multisig_address) / 4

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

    to = ops_multisig_address
    deadline = chain[-1].timestamp + 3600

    # perform swap
    sushiswap_router.swapExactTokensForTokens(
        amount_in,
        amount_out_min,
        path,
        to,
        deadline,
        {"from": ops_multisig_address}
    )

    print(
        "Balances after swap:\n"
        f"USDC: {USDC_contract.balanceOf(ops_multisig_address)/ (10 ** USDC_decimals)}\n" +
        f"SDL: {SDL_contract.balanceOf(ops_multisig_address)/ (10 ** SDL_decimals)}"
    )

    #####################################################################
    ######## 2022_xx_xx_7_1_opsMsig_market_buy_SDL_tranche_2.py #########
    #####################################################################

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    # ops_multisig = ApeSafe(
    #    OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    # )

    # @dev using EOA address instead of ApeSafe object for testing
    ops_multisig_address = OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]

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
        f"USDC: {USDC_contract.balanceOf(ops_multisig_address)/ (10 ** USDC_decimals)}\n" +
        f"SDL: {SDL_contract.balanceOf(ops_multisig_address)/ (10 ** SDL_decimals)}"
    )

    # approve the router to spend the ops_multisig's USDC
    USDC_contract.approve(
        SUSHISWAP_ROUTER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]],
        2 ** 256 - 1,
        {"from": ops_multisig_address}
    )

    # swap 1/4 of *initial* ops_multisig's USDC balance to SDL (which is 1/3 now)
    amount_in = USDC_contract.balanceOf(ops_multisig_address) / 3

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

    to = ops_multisig_address
    deadline = chain[-1].timestamp + 3600

    # perform swap
    sushiswap_router.swapExactTokensForTokens(
        amount_in,
        amount_out_min,
        path,
        to,
        deadline,
        {"from": ops_multisig_address}
    )

    print(
        "Balances after swap:\n"
        f"USDC: {USDC_contract.balanceOf(ops_multisig_address)/ (10 ** USDC_decimals)}\n" +
        f"SDL: {SDL_contract.balanceOf(ops_multisig_address)/ (10 ** SDL_decimals)}"
    )

    #####################################################################
    ######## 2022_xx_xx_7_1_opsMsig_market_buy_SDL_tranche_3.py #########
    #####################################################################

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    # ops_multisig = ApeSafe(
    #    OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    # )

    # @dev using EOA address instead of ApeSafe object for testing
    ops_multisig_address = OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]

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
        f"USDC: {USDC_contract.balanceOf(ops_multisig_address)/ (10 ** USDC_decimals)}\n" +
        f"SDL: {SDL_contract.balanceOf(ops_multisig_address)/ (10 ** SDL_decimals)}"
    )

    # approve the router to spend the ops_multisig's USDC
    USDC_contract.approve(
        SUSHISWAP_ROUTER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]],
        2 ** 256 - 1,
        {"from": ops_multisig_address}
    )

    # swap 1/4 of *initial* ops_multisig's USDC balance to SDL (which is 1/2 now)
    amount_in = USDC_contract.balanceOf(ops_multisig_address) / 2

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

    to = ops_multisig_address
    deadline = chain[-1].timestamp + 3600

    # perform swap
    sushiswap_router.swapExactTokensForTokens(
        amount_in,
        amount_out_min,
        path,
        to,
        deadline,
        {"from": ops_multisig_address}
    )

    print(
        "Balances after swap:\n"
        f"USDC: {USDC_contract.balanceOf(ops_multisig_address)/ (10 ** USDC_decimals)}\n" +
        f"SDL: {SDL_contract.balanceOf(ops_multisig_address)/ (10 ** SDL_decimals)}"
    )

    #####################################################################
    ######## 2022_xx_xx_7_1_opsMsig_market_buy_SDL_tranche_4.py #########
    #####################################################################

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    # ops_multisig = ApeSafe(
    #    OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    # )

    # @dev using EOA address instead of ApeSafe object for testing
    ops_multisig_address = OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]

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
        f"USDC: {USDC_contract.balanceOf(ops_multisig_address)/ (10 ** USDC_decimals)}\n" +
        f"SDL: {SDL_contract.balanceOf(ops_multisig_address)/ (10 ** SDL_decimals)}"
    )

    # approve the router to spend the ops_multisig's USDC
    USDC_contract.approve(
        SUSHISWAP_ROUTER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]],
        2 ** 256 - 1,
        {"from": ops_multisig_address}
    )

    # swap 1/4 of *initial* ops_multisig's USDC balance to SDL (which is total balance now)
    amount_in = USDC_contract.balanceOf(ops_multisig_address)

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

    to = ops_multisig_address
    deadline = chain[-1].timestamp + 3600

    # perform swap
    sushiswap_router.swapExactTokensForTokens(
        amount_in,
        amount_out_min,
        path,
        to,
        deadline,
        {"from": ops_multisig_address}
    )

    print(
        "Balances after swap:\n"
        f"USDC: {USDC_contract.balanceOf(ops_multisig_address)/ (10 ** USDC_decimals)}\n" +
        f"SDL: {SDL_contract.balanceOf(ops_multisig_address)/ (10 ** SDL_decimals)}"
    )

    #####################################################################
    ######### 2022_xx_xx_8_opsMsig_LP_SDL_WETH_in_sushi_pool.py #########
    #####################################################################

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    # ops_multisig = ApeSafe(
    #    OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    # )

    # @dev using EOA address instead of ApeSafe object for testing
    ops_multisig_address = OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]

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
        f"WETH: {WETH_contract.balanceOf(ops_multisig_address)/ (10 ** WETH_decimals)}\n" +
        f"SDL: {SDL_contract.balanceOf(ops_multisig_address)/ (10 ** SDL_decimals)}\n" +
        f"SUSHI/WETH SLP: {SLP_contract.balanceOf(ops_multisig_address)/ (10 ** SLP_decimals)}\n" +
        f"SUSHI/WETH SLP total supply: {SLP_contract.totalSupply()/ (10 ** SLP_decimals)}\n\n"
    )

    # approve the router to spend the ops_multisig's WETH
    WETH_contract.approve(
        SUSHISWAP_ROUTER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]],
        2 ** 256 - 1,
        {"from": ops_multisig_address}
    )

    # approve the router to spend the ops_multisig's SDL
    SDL_contract.approve(
        SUSHISWAP_ROUTER_ADDRESS[CHAIN_IDS[TARGET_NETWORK]],
        2 ** 256 - 1,
        {"from": ops_multisig_address}
    )

    # paramters for addLiquidity tx

    token_a = token_addresses_mainnet["WETH"]
    token_b = SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    amount_a_desired = WETH_contract.balanceOf(ops_multisig_address)
    # factor for how much deviation from optimal token ratio is acceptable
    tolerance_factor = 0.2
    amount_b_desired = SDL_contract.balanceOf(
        ops_multisig_address)
    amount_a_min = WETH_contract.balanceOf(
        ops_multisig_address) * tolerance_factor
    amount_b_min = SDL_contract.balanceOf(
        ops_multisig_address) * tolerance_factor
    to = ops_multisig_address
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
        {"from": ops_multisig_address}
    )

    print(
        "Balances after LP'ing:\n"
        f"WETH: {WETH_contract.balanceOf(ops_multisig_address)/ (10 ** WETH_decimals)}\n" +
        f"SDL: {SDL_contract.balanceOf(ops_multisig_address)/ (10 ** SDL_decimals)}\n" +
        f"SUSHI/WETH SLP: {SLP_contract.balanceOf(ops_multisig_address)/ (10 ** SLP_decimals)}\n" +
        f"SUSHI/WETH SLP total supply: {SLP_contract.totalSupply()/ (10 ** SLP_decimals)}\n\n"
    )

    # send SLP back to main multisig
    balance = SLP_contract.balanceOf(ops_multisig_address)
    SLP_contract.transfer(
        main_multisig_address,
        balance,
        {"from": ops_multisig_address}
    )
    assert SLP_contract.balanceOf(ops_multisig_address) == 0
    assert SLP_contract.balanceOf(main_multisig_address) >= balance
