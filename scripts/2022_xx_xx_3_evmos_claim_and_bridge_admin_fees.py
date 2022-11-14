import this
from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    META_SWAP_DEPOSIT_ABI,
    MULTISIG_ADDRESSES,
    SWAP_ABI,
    META_SWAP_ABI,
    EVMOS_CELER_LIQUIDITY_BRIDGE,
    EVMOS_CELER_LIQUIDITY_BRIDGE_ABI,
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract, chain
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "EVMOS"


def main():
    """This script claims admin fees from all Evmos pools, then converts them to ceUSDC and sends them to Mainnet"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
    )

    # Run any pending transactions before simulating any more transactions
    # multisig.preview_pending()

    MAX_POOL_LENGTH = 32
    CEUSDC_EVMOS = "0xe46910336479F254723710D57e7b683F3315b22B"

    # Optimism L2 Standard Bridge
    liquidity_bridge = Contract.from_abi(
        "EvmosCelerLiquidityBridge",
        EVMOS_CELER_LIQUIDITY_BRIDGE[CHAIN_IDS[TARGET_NETWORK]],
        EVMOS_CELER_LIQUIDITY_BRIDGE_ABI
    )

    # token -> swap/metaswap dict
    # @dev which pool to use for swapping which token (Evmos representations ignored for now)
    token_to_swap_dict = {
        # ceUSDC : Evmos USDT Pool
        "0x7f5c764cbc14f9669b88837ca1490cca17c31607": "0x79cb59c7B6bd0e5ef99189efD9065500eAbc1a4b",
        # ceUSDT : Evmos USDT Pool
        "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58": "0x79cb59c7B6bd0e5ef99189efD9065500eAbc1a4b",
    }

    # swap -> metaswapDeposit dict
    swap_to_deposit_dict = {
        # Evmos USDT Pool
        "0x79cb59c7B6bd0e5ef99189efD9065500eAbc1a4b": "",
        # Evmos 4Pool (paused)
        # "0x81272C5c573919eF0C719D6d63317a4629F161da": "",
        # Evmos Frax3Pool (paused)
        # "0x21d4365834B7c61447e142ef6bCf01136cBD01c6": "",
        # Evmos 3Pool (paused)
        # "0x1275203FB58Fc25bC6963B13C2a1ED1541563aF0": "",
        # Evmos BTC Pool (paused)
        # "0x7003102c75587E8D29c56124060463Ef319407D0": "",
        # Evmos tBTC Metapool (paused)
        # "0xdb5c5A6162115Ce9a188E7D773C4D011F421BbE5": "0xFdA5D2ad8b6d3884AbB799DA66f57175E8706941",
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
        ).balanceOf(multisig.address)
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
            {"from": multisig.address})

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
                token_index_USDC = base_swap.getTokenIndex(CEUSDC_EVMOS)
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
                    {"from": multisig.address}
                )
                print(
                    f"Burning {LP_balance} {base_pool_LP_contract.symbol()} for USDC"
                )
                deadline = chain[chain.height].timestamp + 10 * 60
                base_swap.removeLiquidityOneToken(
                    LP_balance,
                    token_index_USDC,
                    min_amount,
                    deadline,
                    {"from": multisig.address}
                )

    # capture and log token balances of msig after claiming
    token_balances_after = {}
    for token_address in token_addresses:
        symbol = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        ).symbol()
        token_balances_after[token_address] = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        ).balanceOf(multisig.address)
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
        if token_address == CEUSDC_EVMOS:
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
                token_index_to = swap.getTokenIndex(CEUSDC_EVMOS)

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
                base_token_index_to = base_swap.getTokenIndex(CEUSDC_EVMOS)
                token_index_from = 0  # index 0 is non-base-pool token
                # offset by one for flattened 'to' token index
                token_index_to = 1 + base_token_index_to

            # deadline 10 mins from now
            deadline = chain[chain.height].timestamp + 10 * 60

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
                {"from": multisig.address}
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
                {"from": multisig.address}
            )

    # bridging USDC to mainnet
    ceUSDC_contract = Contract.from_abi("ERC20", CEUSDC_EVMOS, ERC20_ABI)

    # bridge difference between balance before and after claiming + converting
    amount_to_bridge = ceUSDC_contract.balanceOf(
        multisig.address
    ) - token_balances_before[CEUSDC_EVMOS]

    print(
        f"Approving bridge for ${ceUSDC_contract.symbol()} {amount_to_bridge / (10 ** ceUSDC_contract.decimals())}"
    )
    # approve gateway
    ceUSDC_contract.approve(
        liquidity_bridge,
        amount_to_bridge,
        {"from": multisig.address}
    )

    # send tx to bridge
    print(
        f"Bridging ${ceUSDC_contract.symbol()} {amount_to_bridge / (10 ** ceUSDC_contract.decimals())} to mainnet"
    )
    # @dev
    # for ref: https://cbridge-docs.celer.network/developer/api-reference/contract-pool-based-transfer
    # Celer suggests using timestamp as nonce
    liquidity_bridge.send(
        MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]],   # _receiver
        CEUSDC_EVMOS,                               # _token
        amount_to_bridge,                           # _amount
        1,                                          # _dstChainId (eth mainnet)
        chain[chain.height].timestamp,              # _nonce
        5000,                                       # _maxSlippage (in pips)
        {"from": multisig.address}
    )

    # combine history into multisend txn
    # TODO: set 'safe_nonce'
    safe_tx = multisig.multisend_from_receipts()
    safe_nonce = 0

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    multisig.preview(safe_tx)
    confirm_posting_transaction(multisig, safe_tx)
