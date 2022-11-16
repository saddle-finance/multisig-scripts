from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    OPS_MULTISIG_ADDRESSES,
    SWAP_ABI,
    META_SWAP_ABI,
    UNIV3_ROUTER_ABI,
    UNIV3_QUOTER_ABI
)
from fee_distro_helpers import (
    token_to_swap_dict_saddle,
    token_addresses_mainnet,
    token_to_token_univ3_dict,
    swap_to_deposit_dict,
    MAX_POOL_LENGTH,
    UNIV3_ROUTER,
    UNIV3_QUOTER
)
from eth_abi.packed import encode_abi_packed
from ape_safe import ApeSafe
from brownie import accounts, network, Contract, chain
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "MAINNET"


def main():
    """This script swaps all fee tokens to USDC, from Ops-Multisig"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    ops_multisig = ApeSafe(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    )

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
            ops_multisig.address
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
            ops_multisig.address)

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
                {"from": ops_multisig.address}
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
                {"from": ops_multisig.address}
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
        ).balanceOf(ops_multisig.address)
        print(
            f"Balance of {symbol}: {token_balances_after_saddle_swap[token_address] / (10 ** token_contract.decimals())}"
        )

    # swap all remaining tokens that are not USDC into USDC via UniswapV3
    for token_address in token_to_token_univ3_dict.keys():
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
            UNIV3_ROUTER,
            amount_in,
            {"from": ops_multisig.address}
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
    for token_address in token_addresses:
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

    # combine history into multisend txn
    # TODO: set 'safe_nonce'
    safe_tx = ops_multisig.multisend_from_receipts()
    safe_nonce = 0

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    ops_multisig.preview(safe_tx)
    confirm_posting_transaction(ops_multisig, safe_tx)
