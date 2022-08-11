from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    MULTISIG_ADDRESSES,
    SWAP_ABI,
    OPTIMISM_STANDARD_BRIDGE,
    L1_TO_L2_ERC20_ADDRESSES
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "OPTIMISM"


def main():
    """This script claims admin fees from all Optimism pools and sends them to Mainnet"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    # Run any pending transactions before simulating any more transactions
    # multisig.preview_pending()

    MAX_POOL_LENGTH = 32

    # Optimism L2 Standard Bridge
    standard_bridge = multisig.contract(
        OPTIMISM_STANDARD_BRIDGE[CHAIN_IDS[TARGET_NETWORK]]
    )

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
        symbol = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        ).symbol()
        token_balances_before[token_address] = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        ).balanceOf(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
        print(
            f"Balance of {symbol} before claiming: {token_balances_before[token_address]}"
        )

    # execute txs for claiming admin fees
    for swap_address in swap_to_deposit_dict:
        lp_token_address = Contract.from_abi(
            "Swap", swap_address, SWAP_ABI).swapStorage()[6]
        lp_token_name = Contract.from_abi(
            "LPtoken", lp_token_address, ERC20_ABI).name()
        print(
            # TODO: change this to LP token name
            f"Claiming admin fees from {lp_token_name}"
        )
        pool = Contract.from_abi("Swap", swap_address, SWAP_ABI)
        pool.withdrawAdminFees(
            {"from": MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]})

    # capture and log token balances of msig after claiming
    token_balances_after = {}
    for token_address in token_addresses:
        symbol = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        ).symbol()
        token_balances_after[token_address] = Contract.from_abi(
            "ERC20", token_address, ERC20_ABI
        ).balanceOf(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
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

    # find L1 addresses of tokens for bridging
    L2_to_L1_dict = {}
    for L1_address in L1_TO_L2_ERC20_ADDRESSES:
        for L2_address_key in L1_TO_L2_ERC20_ADDRESSES[L1_address]:
            L2_address = L1_TO_L2_ERC20_ADDRESSES[L1_address][L2_address_key]
            if L2_address in token_addresses:
                L2_to_L1_dict[L2_address] = L1_address
    # debug. TODO: remove this
    print(
        L2_to_L1_dict
    )

    # bridge fees to mainnet
    for token_address in token_addresses:
        # the token to be bridged
        token_contract = Contract.from_abi("ERC20", token_address, ERC20_ABI)

        # bridge difference between before and after claiming
        amount_to_bridge = token_balances_after[token_address] - \
            token_balances_before[token_address]
        print(
            f"Bridging ${token_contract.symbol()} {amount_to_bridge / (10 ** token_contract.decimals())} to mainnet"
        )

        # find gateway for token
        token_gateway_address = gateway_router.getGateway(
            token_contract.address
        )

        # approve gateway
        token_contract.approve(
            token_gateway_address,
            amount_to_bridge,
            {"from": MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]}
        )

        # send tx to bridge
        gateway_router.outboundTransfer(
            L2_to_L1_dict[token_address],
            MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]],
            amount_to_bridge,
            "0x0"  # TODO: clarify what format this needs to have
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
