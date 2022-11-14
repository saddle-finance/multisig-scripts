from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    OPTIMISM_STANDARD_BRIDGE,
    MULTISIG_ADDRESSES,
    SWAP_ABI,
    META_SWAP_ABI,
    OPTIMISM_L2_STANDARD_BRIDGE_ABI
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract, chain
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "OPTIMISM"


def main():
    """This script swaps admin fees to USDC and sends them to Mainnet main multisig"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    ops_multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url='https://safe-transaction.optimism.gnosis.io/'
    )

    # Run any pending transactions before simulating any more transactions
    # ops_multisig.preview_pending()

    MAX_POOL_LENGTH = 32
    USDC_OPTIMISM = "0x7F5c764cBc14f9669B88837ca1490cCa17c31607"

    # Optimism L2 Standard Bridge
    standard_bridge = Contract.from_abi(
        "L2StandardBridge",
        OPTIMISM_STANDARD_BRIDGE[CHAIN_IDS[TARGET_NETWORK]],
        OPTIMISM_L2_STANDARD_BRIDGE_ABI
    )

    # token -> swap/metaswap dict , which pool to use for swapping which token
    token_to_swap_dict = {
        # USDC : Opt FRAXBP Pool
        "0x7f5c764cbc14f9669b88837ca1490cca17c31607": "0xF6C2e0aDc659007Ba7c48446F5A4e4E94dfe08b5",
        # USDT : Opt FRAXBP/USDT Metapool
        "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58": "0xa9a84238098Dc3d1529228E6c74dBE7EbdF117a5",
        # FRAX : Opt FRAXBP Pool
        "0x2E3D870790dC77A83DD1d18184Acc7439A53f475": "0xF6C2e0aDc659007Ba7c48446F5A4e4E94dfe08b5",
        # sUSD : Opt FRAXBP/sUSD Metapool
        "0x8c6f28f2F1A3C87F0f938b96d27520d9751ec8d9": "0x250184dDDEC6d38E28ac12B481c9016867226E9D",
    }

    # swap -> metaswapDeposit dict
    swap_to_deposit_dict = {
        # Opt USD Pool
        "0x5847f8177221268d279Cf377D0E01aB3FD993628": "",
        # Opt FRAXBP Pool
        "0xF6C2e0aDc659007Ba7c48446F5A4e4E94dfe08b5": "",
        # Opt FRAXBP/sUSD Metapool
        "0x250184dDDEC6d38E28ac12B481c9016867226E9D": "0xdf815Ea6b066Ac9f3107d8863a6c19aA2a5d24d3",
        # Opt FRAXBP/USDT Metapool
        "0xa9a84238098Dc3d1529228E6c74dBE7EbdF117a5": "0x3F1d224557afA4365155ea77cE4BC32D5Dae2174",
        # Opt USD/FRAX Metapool
        "0xc55E8C79e5A6c3216D4023769559D06fa9A7732e": "0x88Cc4aA0dd6Cf126b00C012dDa9f6F4fd9388b17",
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

    # capture and log token balances of msig before swapping
    token_balances_before = {}
    for token_address in token_addresses:
        symbol = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        ).symbol()
        token_balances_before[token_address] = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        ).balanceOf(ops_multisig.address)
        print(
            f"Balance of {symbol} before swapping: {token_balances_before[token_address]}"
        )

    # convert all collected fees to USDC, to minimize # of claiming txs on L1
    for token_address in token_addresses:
        # skip USDC, since it's the target
        if token_address == USDC_OPTIMISM:
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
                token_index_to = swap.getTokenIndex(USDC_OPTIMISM)

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
                base_token_index_to = base_swap.getTokenIndex(USDC_OPTIMISM)
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

    # bridge 100% of USDC balance to mainnet main multisig
    USDC = Contract.from_abi("ERC20", USDC_OPTIMISM, ERC20_ABI)
    amount_to_bridge = USDC.balanceOf(
        ops_multisig.address
    )

    print(
        f"Approving bridge for ${USDC.symbol()} {amount_to_bridge / (10 ** USDC.decimals())}"
    )
    # approve gateway
    USDC.approve(
        standard_bridge,
        amount_to_bridge,
        {"from": ops_multisig.address}
    )

    # send tx to bridge
    print(
        f"Bridging ${USDC.symbol()} {amount_to_bridge / (10 ** USDC.decimals())} to mainnet"
    )
    standard_bridge.withdrawTo(
        USDC_OPTIMISM,                              # _l2token
        MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]],   # _to
        amount_to_bridge,                           # _amount
        0,                                          # _l1Gas   TODO: check if 0 is viable
        "",                                         # _data
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
