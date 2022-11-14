import this
from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    META_SWAP_DEPOSIT_ABI,
    MULTISIG_ADDRESSES,
    OPS_MULTISIG_ADDRESSES,
    SWAP_ABI,
    META_SWAP_ABI,
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract, chain
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "MAINNET"


def main():
    """This script claims admin fees from all Mainnet pools and sends them to Operations Multisig"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
    )
    ops_multisig_address = OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]

    # Run any pending transactions before simulating any more transactions
    # multisig.preview_pending()

    MAX_POOL_LENGTH = 32

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

    # send fee tokens to operations multisig
    for token_address in token_addresses:
        token_contract = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        )
        symbol = token_contract.symbol()
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

    # combine history into multisend txn
    # TODO: set 'safe_nonce'
    safe_tx = multisig.multisend_from_receipts()
    safe_nonce = 0

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    multisig.preview(safe_tx)
    confirm_posting_transaction(multisig, safe_tx)
