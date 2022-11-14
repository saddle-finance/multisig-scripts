from scripts.utils import confirm_posting_transaction
from brownie import accounts, network, Contract, chain
from ape_safe import ApeSafe
from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    META_SWAP_DEPOSIT_ABI,
    MULTISIG_ADDRESSES,
    SWAP_ABI,
    META_SWAP_ABI,
)


TARGET_NETWORK = "KAVA"


def main():
    """This script claims admin fees from all Kava pools, then converts them to xxxx and sends them to Mainnet"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    ops_multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
    )

    # Run any pending transactions before simulating any more transactions
    # ops_multisig.preview_pending()

    MAX_POOL_LENGTH = 32
    USDC_KAVA = "0xfa9343c3897324496a05fc75abed6bac29f8a40f"

    # TODO: get Kava bridge

    # bridge = Contract.from_abi(
    #
    # )

    # token -> swap/metaswap dict
    # @dev which pool to use for swapping which token
    token_to_swap_dict = {
        # USDT : Kava USDT Pool
        "0xb44a9b6905af7c801311e8f4e76932ee959c663c": "0x5847f8177221268d279Cf377D0E01aB3FD993628",
        # USDC : Kava USDT Pool
        "0xfa9343c3897324496a05fc75abed6bac29f8a40f": "0x5847f8177221268d279Cf377D0E01aB3FD993628",
    }

    # swap -> metaswapDeposit dict
    swap_to_deposit_dict = {
        # Kava USDT Pool
        "0x5847f8177221268d279Cf377D0E01aB3FD993628": "",
        # Kava 3Pool (paused)
        # "0xA500b0e1360462eF777804BCAe6CE2BfB524dD2e": "",
    }

    # comprehend set of underlying tokens used by pools on that chain
    token_addresses = set()
    base_LP_addresses = set()
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
            base_LP_addresses.add(swap_contract.getToken(1))

    # capture and log token balances of msig before claiming
    token_balances_before = {}
    for token_address in token_addresses:
        symbol = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        ).symbol()
        token_balances_before[token_address] = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        ).balanceOf(ops_multisig.address)
        print(
            f"Balance of {symbol} before claiming: {token_balances_before[token_address]}"
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
        pool.withdrawAdminFees(
            {"from": ops_multisig.address})

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
            LP_balance = base_pool_LP_contract.balanceOf(ops_multisig.address)
            if LP_balance > 0:
                base_swap_address = metaswap_deposit_contract.baseSwap()
                base_swap = Contract.from_abi(
                    "BaseSwap", base_swap_address, SWAP_ABI
                )
                token_index_USDC = base_swap.getTokenIndex(USDC_KAVA)
                min_amount = base_swap.calculateRemoveLiquidityOneToken(
                    LP_balance,
                    token_index_USDC
                )
                # approve amount to swap
                print(
                    f"Approving base pool for {base_pool_LP_contract.symbol()} {LP_balance}"
                )
                base_pool_LP_contract.approve(
                    base_swap,
                    LP_balance,
                    {"from": ops_multisig.address}
                )
                print(
                    f"Burning {LP_balance} {base_pool_LP_contract.symbol()} for USDC"
                )
                deadline = chain[chain.height].timestamp + 3600
                base_swap.removeLiquidityOneToken(
                    LP_balance,
                    token_index_USDC,
                    min_amount,
                    deadline,
                    {"from": ops_multisig.address}
                )

    # capture and log token balances of msig after claiming
    token_balances_after = {}
    for token_address in token_addresses:
        symbol = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        ).symbol()
        token_balances_after[token_address] = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        ).balanceOf(ops_multisig.address)
        print(
            f"Balance of {symbol} after claiming: {token_balances_after[token_address]}"
        )

    # log claimed amounts
    for token_address in token_addresses:
        symbol = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        ).symbol()
        print(
            f"Claimed {symbol}: {(token_balances_after[token_address] - token_balances_before[token_address])}"
        )

    # convert all collected fees to USDC, to minimize # of bridge transactions
    for token_address in token_addresses:
        # skip USDC, since it's the target
        if token_address == USDC_KAVA:
            continue

        # amount to swap
        amount_to_swap = token_balances_after[token_address] - \
            token_balances_before[token_address]

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
                token_index_to = swap.getTokenIndex(USDC_KAVA)

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
                base_token_index_to = base_swap.getTokenIndex(USDC_KAVA)
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
                f"Approving swap for ${token_contract.symbol()} {amount_to_swap}"
            )
            token_contract.approve(
                swap_address,
                amount_to_swap,
                {"from": ops_multisig.address}
            )

            # perform swap
            print(
                f"Swapping {amount_to_swap / (10 ** token_contract.decimals())} {token_contract.symbol()} to USDC"
            )
            swap.swap(
                token_index_from,
                token_index_to,
                amount_to_swap,
                min_amount,
                deadline,
                {"from": ops_multisig.address}
            )

    # bridging USDC to mainnet
    USDC_contract = Contract.from_abi("ERC20", USDC_KAVA, ERC20_ABI)
    amount_to_bridge = USDC_contract.balanceOf(
        ops_multisig.address
    )

    print(
        f"Approving bridge for ${USDC_contract.symbol()} {amount_to_bridge / (10 ** USDC_contract.decimals())}"
    )
    # approve gateway
    # USDC_contract.approve(
    #    liquidity_bridge,
    #    amount_to_bridge,
    #    {"from": ops_multisig.address}
    # )

    # send tx to bridge
    # print(
    #    f"Bridging ${USDC_contract.symbol()} {amount_to_bridge / (10 ** USDC_contract.decimals())} to mainnet"
    # )

    # TODO: bridge USDC to mainnet main msig (bridge for Kava tbd)

    # combine history into multisend txn
    # TODO: set 'safe_nonce'
    safe_tx = ops_multisig.multisend_from_receipts()
    safe_nonce = 0

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    ops_multisig.preview(safe_tx)
    confirm_posting_transaction(ops_multisig, safe_tx)
