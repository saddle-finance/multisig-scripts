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


TARGET_NETWORK = "EVMOS"


def main():
    """This script claims admin fees from all Evmos pools, then sends it operations multisig on evmos"""

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
    CEUSDC_EVMOS = "0xe46910336479F254723710D57e7b683F3315b22B"

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
                deadline = chain[chain.height].timestamp + 3600
                base_swap.removeLiquidityOneToken(
                    LP_balance,
                    token_index_USDC,
                    min_amount,
                    deadline,
                    {"from": multisig.address}
                )

    # capture and log token balances of msig after swapping
    token_balances_after = {}
    for token_address in token_addresses:
        symbol = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        ).symbol()
        token_balances_after[token_address] = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        ).balanceOf(multisig.address)
        print(
            f"Balance of {symbol} after swapping: {token_balances_after[token_address]}"
        )

    # send tokens to operations multisig
    for token_address in token_addresses:
        token_contract = Contract.from_abi("ERC20", token_address, ERC20_ABI)
        symbol = token_contract.symbol()
        token_balance = token_contract.balanceOf(multisig.address)
        if token_balance > 0:
            print(
                f"Sending {token_balance} {symbol} to operations multisig"
            )
            token_contract.transfer(
                ops_multisig_address,
                token_balance,
                {"from": multisig.address}
            )
        assert token_contract.balanceOf(multisig.address) == 0
        assert token_contract.balanceOf(ops_multisig_address) == token_balance

    # combine history into multisend txn
    # TODO: set 'safe_nonce'
    safe_tx = multisig.multisend_from_receipts()
    safe_nonce = 0

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    multisig.preview(safe_tx)
    confirm_posting_transaction(multisig, safe_tx)
