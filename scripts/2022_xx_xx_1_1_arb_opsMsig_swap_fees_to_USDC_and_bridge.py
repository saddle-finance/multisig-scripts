from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    ARB_GATEWAY_ROUTER,
    MULTISIG_ADDRESSES,
    SWAP_ABI,
    META_SWAP_ABI
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract, chain
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "ARBITRUM"


def main():
    """This script swaps fee tokens to USDC and bridges USDC to main multisig on Mainnet"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    ops_multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    # Run any pending transactions before simulating any more transactions
    # ops_multisig.preview_pending()

    MAX_POOL_LENGTH = 32
    USDC_ARBITRUM = "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8"
    USDC_MAINNET = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

    # Arbitrum L2 gateway router
    gateway_router = ops_multisig.contract(
        ARB_GATEWAY_ROUTER[CHAIN_IDS[TARGET_NETWORK]]
    )

    # token -> swap/metaswap dict , which pool to use for swapping which token
    token_to_swap_dict = {
        # USDC : Arb USD Pool
        "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8": "0xBea9F78090bDB9e662d8CB301A00ad09A5b756e9",
        # USDT : Arb USDV2 Pool
        "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9": "0xfeEa4D1BacB0519E8f952460A70719944fe56Ee0",
        # FRAX : Arb FRAXBP Pool
        "0x17FC002b466eEc40DaE837Fc4bE5c67993ddBd6F": "0x401AFbc31ad2A3Bc0eD8960d63eFcDEA749b4849",
        # MIM : Arb USD Pool
        "0xFEa7a6a0B346362BF88A9e4A88416B77a57D6c2A": "0xBea9F78090bDB9e662d8CB301A00ad09A5b756e9",
        # nUSD : Arb USD Pool
        "0x2913E812Cf0dcCA30FB28E6Cac3d2DCFF4497688": "0xBea9F78090bDB9e662d8CB301A00ad09A5b756e9",
        # USDs : Arb FRAXBP/USDS Metapool
        "0xD74f5255D557944cf7Dd0E45FF521520002D5748": "0xa5bD85ed9fA27ba23BfB702989e7218E44fd4706"
    }

    # swap/metaswap -> metaswapDeposit dict
    swap_to_deposit_dict = {
        # Arb USD Pool
        "0xBea9F78090bDB9e662d8CB301A00ad09A5b756e9": "",
        # Arb USDV2 Pool
        "0xfeEa4D1BacB0519E8f952460A70719944fe56Ee0": "",
        # Arb USDS Metapool
        "0x5dD186f8809147F96D3ffC4508F3C82694E58c9c": "0xDCA5b16A96f984ffb2A3022cfF339eb049126101",
        # Arb FRAXBP Pool
        "0x401AFbc31ad2A3Bc0eD8960d63eFcDEA749b4849": "",
        # Arb FRAXBP/USDS Metapool
        "0xa5bD85ed9fA27ba23BfB702989e7218E44fd4706": "0x1D434f50acf16BA013BE3536e9A3CDb5D7d4e694",
        # Arb FRAXBP/USDT Metapool
        "0xf8504e92428d65E56e495684A38f679C1B1DC30b": "0xc8DFCFC329E19fDAF43a338aD6038dBA02a5079B",
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

    # capture and log token balances of ops msig before swapping
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
        if token_address == USDC_ARBITRUM:
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
                token_index_to = swap.getTokenIndex(USDC_ARBITRUM)

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
                base_token_index_to = base_swap.getTokenIndex(USDC_ARBITRUM)
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
    USDC = Contract.from_abi("ERC20", USDC_ARBITRUM, ERC20_ABI)

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
        USDC_MAINNET,
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
