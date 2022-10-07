import this
from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    META_SWAP_DEPOSIT_ABI,
    MULTISIG_ADDRESSES,
    SWAP_ABI,
    META_SWAP_ABI,
    UNIV3_ROUTER_ABI,
    UNIV3_QUOTER_ABI
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract, chain
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "MAINNET"


def main():
    """This script claims admin fees from all Mainnet pools, 
    then converts them to SDL/ETH SLP and sends it to the fee distrbutor
    Steps are:
    1. Claim admin fees on all pools
    2. Burn claimed LPs to get underlyings
    3. Swap assets into USDC, WBTC, WETH using Saddle, if possible
    4. Swap remaining assets into USDC, using UniswapV3
    5. Buy SDL+ETH 50/50 and LP in Sushi pool
    6. Send SDL/ETH SLP to fee distributor
    """

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url='https://safe-transaction.optimism.gnosis.io/'
    )

    # Run any pending transactions before simulating any more transactions
    # multisig.preview_pending()

    MAX_POOL_LENGTH = 32
    USDC_MAINNET = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    WETH_MAINNET = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    WBTC_MAINNET = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"

    UNIV3_ROUTER = "0xE592427A0AEce92De3Edee1F18E0157C05861564"
    UNIV3_QUOTER = "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6"

    univ3_router = Contract.from_abi(
        "UniV3Router", UNIV3_ROUTER, UNIV3_ROUTER_ABI
    )
    univ3_quoter = Contract.from_abi(
        "UniV3Quoter", UNIV3_QUOTER, UNIV3_QUOTER_ABI
    )

    # token_from -> (token_to, swap/metaswap) dict
    # which target token and pool
    token_to_swap_dict_saddle = {
        # USDT : USDv2 Pool
        "0xdAC17F958D2ee523a2206206994597C13D831ec7": (USDC_MAINNET, "0xaCb83E0633d6605c5001e2Ab59EF3C745547C8C7"),
        # FRAX : FraxBP Pool
        "0x853d955aCEf822Db058eb8505911ED77F175b99e": (USDC_MAINNET, "0x13Cc34Aa8037f722405285AD2C82FE570bfa2bdc"),
        # sUSD : FraxBP/sUSD Metapool
        "0x57Ab1ec28D129707052df4dF418D58a2D46d5f51": (USDC_MAINNET, "0x69baA0d7c2e864b74173922Ca069Ac79d3be1556"),
        # DAI : USDv2 Pool
        "0x6B175474E89094C44Da98b954EedeAC495271d0F": (USDC_MAINNET, "0xaCb83E0633d6605c5001e2Ab59EF3C745547C8C7"),
        # alUSD : FraxBP/alUSD Metapool
        "0xBC6DA0FE9aD5f3b0d58160288917AA56653660E9": (USDC_MAINNET, "0xFB516cF3710fC6901F2266aAEB8834cF5e4E9558"),
        # WCUSD : WCUSD/USDv2 Metapool
        "0xad3E3Fc59dff318BecEaAb7D00EB4F68b1EcF195": (USDC_MAINNET, "0x3F1d224557afA4365155ea77cE4BC32D5Dae2174"),
        # USX : USDC-USX Pool
        "0x0a5E677a6A24b2F1A2Bf4F3bFfC443231d2fDEc8": (USDC_MAINNET, "0x2bFf1B48CC01284416E681B099a0CDDCA0231d72"),
        # renBTC : wBTC
        "0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D": (WBTC_MAINNET, "0xdf3309771d2BF82cb2B6C56F9f5365C8bD97c4f2"),
        # sBTC : wBTC
        "0xfE18be6b3Bd88A2D2A7f928d00292E7a9963CfC6": (WBTC_MAINNET, "0xdf3309771d2BF82cb2B6C56F9f5365C8bD97c4f2"),
        # tBTC : wBTC
        "0x18084fbA666a33d37592fA2633fD49a74DD93a88": (WBTC_MAINNET, "0xfa9ED0309Bf79Eb84C847819F0B3CB84F6d351Af"),
        # alETH : WETH
        "0x0100546F2cD4C9D97f798fFC9755E47865FF7Ee6": (WETH_MAINNET, "0xa6018520EAACC06C30fF2e1B3ee2c7c22e64196a"),
        # sETH : WETH
        "0x5e74C9036fb86BD7eCdcb084a0673EFc32eA31cb": (WETH_MAINNET, "0xa6018520EAACC06C30fF2e1B3ee2c7c22e64196a"),
    }

    # token_from -> token_to dict, for using UniswapV3
    token_to_token_univ3_dict = {
        # LUSD : USDC
        "0x5f98805A4E8be255a32880FDeC7F6728C6568bA0": USDC_MAINNET,
        # WBTC : USDC
        WBTC_MAINNET: USDC_MAINNET,
        # WETH : USDC
        WETH_MAINNET: USDC_MAINNET,
        # FEI : USDC (skipped temporarily due to not getting a quote from UniV3)
        # "0x956F47F50A910163D8BF957Cf5846D573E7f87CA": USDC_MAINNET,
    }

    # swap -> metaswapDeposit dict
    swap_to_deposit_dict = {
        # FraxBP Pool
        "0x13Cc34Aa8037f722405285AD2C82FE570bfa2bdc": "",
        # Frax 3Pool Pool
        "0x8cAEa59f3Bf1F341f89c51607E4919841131e47a": "",
        # Saddle D4Pool Pool
        "0xC69DDcd4DFeF25D8a793241834d4cc4b3668EAD6": "",
        # Saddle USX Pool
        "0x2bFf1B48CC01284416E681B099a0CDDCA0231d72": "",
        # Saddle s/w/renBTCV2 Pool
        "0xdf3309771d2BF82cb2B6C56F9f5365C8bD97c4f2": "",
        # FraxBP/alUSD Metapool
        "0xFB516cF3710fC6901F2266aAEB8834cF5e4E9558": "0xe9154791883Df07e1328B636BCedfcCb80fefa38",
        # FraxBP/sUSD Metapool
        "0x69baA0d7c2e864b74173922Ca069Ac79d3be1556": "0x7D6c760cBde5a9Ad47510A86b9DCc58F9473CdD8",
        # FraxBP/USDT Metapool
        "0xC765Cd3d015626244AD63B5FB63a97c5634643b9": "0xAbf69CDE7B3725c12B8703005342EB5DD8a95D61",
        # FraxBP/USX Metapool
        "0x1dcB69a2b9148C641a43F731fCee123e2be30bAb": "0x4F0E41a37cE2ff1fA654cC93Eb03F9d16E65fD11",
        # Saddle sUSD Metapool
        "0x4568727f50c7246ded8C39214Ed6FF3c157f080D": "0xB98fd1f66884cD5786b37cDE040B9f0cf763866f",
        # WCUSD Metapool
        "0x3F1d224557afA4365155ea77cE4BC32D5Dae2174": "0x9898D87368DE0Bf1f10bbea8dE46c00cC3a2F9F1",
        # Saddle USD Pool
        "0xaCb83E0633d6605c5001e2Ab59EF3C745547C8C7": "",
        # Saddle alETH Pool
        "0xa6018520EAACC06C30fF2e1B3ee2c7c22e64196a": "",
        # Saddle TBTC Metapool
        "0xfa9ED0309Bf79Eb84C847819F0B3CB84F6d351Af": "0x4946DE721ce70D4B7aa226aA0Fe869C935769388"
    }

    # comprehend set of underlying tokens used by pools on that chain
    token_addresses = set()
    #base_LP_addresses = set()
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
                deadline = chain[chain.height].timestamp + 10 * 60
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

    # swap all tokens that a are swappable via Saddle to USDC/WBTC/WETH
    for token_address in token_to_swap_dict_saddle.keys():
        # amount to swap
        amount_to_swap = token_balances_after_claim_burn[token_address] - \
            token_balances_before[token_address]

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
                f"Approving swap for ${token_contract.symbol()} {amount_to_swap / (10 ** token_contract.decimals())}"
            )
            token_contract.approve(
                swap_address,
                amount_to_swap,
                {"from": multisig.address}
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
                {"from": multisig.address}
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
        ).balanceOf(multisig.address)
        print(
            f"Balance of {symbol}: {token_balances_after_saddle_swap[token_address] / (10 ** token_contract.decimals())}"
        )

    # swap all remaining tokens that are not USDC into USDC via UniswapV3
    for token_address in token_to_token_univ3_dict.keys():
        token_from = token_address
        token_to = token_to_token_univ3_dict[token_address]
        fee = 500
        recipient = multisig.address
        deadline = chain[chain.height].timestamp + 10 * 60
        amount_in = token_balances_after_saddle_swap[token_from] - \
            token_balances_before[token_from]
        sqrt_price_limit_X96 = 0

        token_contract = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        )

        # getting min amounts
        print(
            f"Getting quote for ${token_contract.symbol()}"
        )
        amount_out_min = univ3_quoter.quoteExactInputSingle(
            token_from,
            token_to,
            fee,
            amount_in,
            sqrt_price_limit_X96,
            {"from": multisig.address}
        ).return_value
        print(
            f"Quote for ${token_contract.symbol()}: {amount_out_min / (10 ** token_contract.decimals())}"
        )

        # input struct for univ3 swap
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

        # approve Univ3 router
        print(
            f"Approve UniV3 router for ${token_contract.symbol()} {amount_in / (10 ** token_contract.decimals())}"
        )
        token_contract = Contract.from_abi("ERC20", token_address, ERC20_ABI)
        token_contract.approve(
            UNIV3_ROUTER,
            amount_in,
            {"from": multisig.address}
        )

        # swap using univ3
        print(
            f"Swap {amount_in / (10 ** token_contract.decimals())} ${token_contract.symbol()} for $USDC on UniV3"
        )
        univ3_router.exactInputSingle(
            params,
            {"from": multisig.address}
        )

    # capture and log token balances of msig after claiming and burning
    print(
        f"Final balances of tokens after claiming, burning, swapping via saddle and UniswapV3:"
    )
    token_balances_final = {}
    for token_address in token_addresses:
        token_contract = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        )
        symbol = token_contract.symbol()
        token_balances_final[token_address] = token_contract.balanceOf(
            multisig.address
        )
        decimals = token_contract.decimals()
        print(
            f"Balance of ${symbol} : {token_balances_final[token_address] / (10 ** decimals)}"
        )

    # TODO: Buy ETH + SDL with USDC
    # TODO: LP in Sushi pool
    # TODO: Send SLP to fee distributor

    # combine history into multisend txn
    # TODO: set 'safe_nonce'
    safe_tx = multisig.multisend_from_receipts()
    safe_nonce = 0

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    multisig.preview(safe_tx)
    confirm_posting_transaction(multisig, safe_tx)
