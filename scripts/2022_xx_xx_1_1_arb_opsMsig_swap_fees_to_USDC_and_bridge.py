from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    ARB_GATEWAY_ROUTER,
    MULTISIG_ADDRESSES,
    OPS_MULTISIG_ADDRESSES,
    SWAP_ABI,
    META_SWAP_ABI
)
from fee_distro_helpers import (
    token_addresses_arbitrum,
    token_addresses_mainnet,
    arb_token_to_swap_dict,
    arb_swap_to_deposit_dict,
    MAX_POOL_LENGTH,

)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract, chain
from scripts.utils import confirm_posting_transaction, convert_fees_to_USDC


TARGET_NETWORK = "ARBITRUM"


def main():
    """This script swaps fee tokens to USDC and bridges USDC to main multisig on Mainnet"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    ops_multisig = ApeSafe(OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    # Run any pending transactions before simulating any more transactions
    # ops_multisig.preview_pending()

    # Arbitrum L2 gateway router
    gateway_router = ops_multisig.contract(
        ARB_GATEWAY_ROUTER[CHAIN_IDS[TARGET_NETWORK]]
    )

    convert_fees_to_USDC(ops_multisig, CHAIN_IDS[TARGET_NETWORK])

    # # comprehend set of underlying tokens used by pools on that chain
    # token_addresses = set()
    # base_LP_addresses = set()
    # for swap_address in arb_swap_to_deposit_dict:
    #     swap_contract = Contract.from_abi("Swap", swap_address, SWAP_ABI)
    #     if arb_swap_to_deposit_dict[swap_address] == "":  # base pool
    #         for index in range(MAX_POOL_LENGTH):
    #             try:
    #                 token_addresses.add(swap_contract.getToken(index))
    #             except:
    #                 break
    #     else:  # metapool
    #         # first token in metapool is non-base-pool token
    #         token_addresses.add(swap_contract.getToken(0))
    #         base_LP_addresses.add(swap_contract.getToken(1))

    # # capture and log token balances of ops msig before swapping
    # token_balances_before = {}
    # for token_address in token_addresses:
    #     symbol = Contract.from_abi(
    #         "ERC20", token_address, ERC20_ABI
    #     ).symbol()
    #     token_balances_before[token_address] = Contract.from_abi(
    #         "ERC20", token_address, ERC20_ABI
    #     ).balanceOf(ops_multisig.address)
    #     print(
    #         f"Balance of {symbol} before swapping: {token_balances_before[token_address]}"
    #     )

    # # convert all collected fees to USDC, to minimize # of claiming txs on L1
    # for token_address in token_addresses:
    #     # skip USDC, since it's the target
    #     if token_address == token_addresses_arbitrum["USDC"]:
    #         continue

    #     # amount to swap
    #     amount_to_swap = token_balances_before[token_address]

    #     # skip if no fees were claimed
    #     if amount_to_swap > 0:
    #         # get swap and token indices
    #         # if base pool, use base pool for swapping
    #         if arb_swap_to_deposit_dict[arb_token_to_swap_dict[token_address]] == "":
    #             swap_address = arb_token_to_swap_dict[token_address]
    #             # Base swap for swapping
    #             swap = Contract.from_abi(
    #                 "Swap", swap_address, SWAP_ABI
    #             )
    #             # get token indices from base pool contract
    #             token_index_from = swap.getTokenIndex(token_address)
    #             token_index_to = swap.getTokenIndex(
    #                 token_addresses_arbitrum["USDC"])

    #         # if metapool, use metapool deposit for swapping
    #         else:
    #             swap_address = arb_swap_to_deposit_dict[arb_token_to_swap_dict[token_address]]
    #             # Metaswap deposit for swapping
    #             swap = Contract.from_abi(
    #                 "MetaSwapDeposit", swap_address, SWAP_ABI
    #             )
    #             # get (flattened) token indices from underlying swap contract
    #             meta_swap = Contract.from_abi(
    #                 "MetaSwap", arb_token_to_swap_dict[token_address], META_SWAP_ABI
    #             )
    #             base_swap = Contract.from_abi(
    #                 "BaseSwap", meta_swap.metaSwapStorage()[0], SWAP_ABI
    #             )
    #             base_token_index_to = base_swap.getTokenIndex(
    #                 token_addresses_arbitrum["USDC"])
    #             token_index_from = 0  # index 0 is non-base-pool token
    #             # offset by one for flattened 'to' token index
    #             token_index_to = 1 + base_token_index_to

    #         # deadline 1h from now
    #         deadline = chain[chain.height].timestamp + 3600

    #         # min amount to receive
    #         min_amount = swap.calculateSwap(
    #             token_index_from,
    #             token_index_to,
    #             amount_to_swap
    #         )

    #         # approve amount to swap
    #         token_contract = Contract.from_abi(
    #             "ERC20", token_address, ERC20_ABI
    #         )
    #         print(
    #             f"Approving {token_contract.symbol()} for saddle pool"
    #         )
    #         token_contract.approve(
    #             swap_address,
    #             amount_to_swap,
    #             {"from": ops_multisig.address}
    #         )

    #         # perform swap
    #         print(
    #             f"Swapping {amount_to_swap / (10 ** token_contract.decimals())} {token_contract.symbol()} to USDC"
    #         )
    #         swap.swap(
    #             token_index_from,
    #             token_index_to,
    #             amount_to_swap,
    #             min_amount,
    #             deadline,
    #             {"from": ops_multisig.address}
    #         )

    # bridging USDC to mainnet
    USDC = Contract.from_abi(
        "ERC20", token_addresses_arbitrum["USDC"], ERC20_ABI
    )

    # bridge 100% of ops-msig USDC balance to mainnet main multisig
    amount_to_bridge = USDC.balanceOf(
        ops_multisig.address
    )

    print(
        f"Bridging ${USDC.symbol()} {amount_to_bridge / (10 ** USDC.decimals())} to mainnet main msig"
    )

    # find gateway for USDC
    token_gateway_address = gateway_router.getGateway(
        USDC.address
    )

    # approve gateway
    USDC.approve(
        token_gateway_address,
        amount_to_bridge,
        {"from": ops_multisig.address}
    )

    # bridge USDC to mainnet main msig
    gateway_router.outboundTransfer(
        token_addresses_mainnet["USDC"],
        MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]],  # mainnet main multisig
        amount_to_bridge,
        "0x",  # TODO: clarify what format this needs to have
        {"from": ops_multisig.address}
    )

    assert USDC.balanceOf(ops_multisig.address) == 0

    # combine history into multisend txn
    # TODO: set 'safe_nonce'
    safe_tx = ops_multisig.multisend_from_receipts()
    safe_nonce = 0

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    ops_multisig.preview(safe_tx)
    confirm_posting_transaction(ops_multisig, safe_tx)
