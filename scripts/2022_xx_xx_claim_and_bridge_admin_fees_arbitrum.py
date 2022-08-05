import this
from helpers import CHAIN_IDS, ERC20_ABI, ARBITRUM_L2_BRIDGE_ROUTER, MULTISIG_ADDRESSES, SWAP_ABI, ARBITRUM_POOL_ADDRESS_TO_POOL_NAME, USDC_ADDRESSES, USDT_ADDRESSES
from ape_safe import ApeSafe
from brownie import accounts, network
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "MAINNET"


def main():
    """This script claims admin fees from all Arbitrum pools and sends them to Mainnet"""

    print(f"You are using the '{network.show_active()}' network")
    assert(network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["ARBITRUM"]])

    # Run any pending transactions before simulating any more transactions
    multisig.preview_pending()

    MAX_POOL_LENGTH = 32

    gateway_router = multisig.contract(
        ARBITRUM_L2_BRIDGE_ROUTER[CHAIN_IDS["ARBITRUM"]]
    )

    # swap, metaswap_deposit dict
    swap_to_deposit = {
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

    # comprehend set of underlying tokens of that chain
    tokens = {}
    for swap in swap_to_deposit:
        swap_contract = Contract.from_abi("Swap", swap, SWAP_ABI)
        if swap_to_deposit[swap] == "":  # base pool
            for index in range(MAX_POOL_LENGTH):
                try:
                    tokens.add(swap_contract.getToken(index))
                except:
                    break
        else:  # metapool
            tokens.add(swap_contract.getToken(0))

    # execute txs for claiming admin fees
    for swap in swap_to_deposit.values():
        print(
            f"Claiming admin fees from {ARBITRUM_POOL_ADDRESS_TO_POOL_NAME[pool_address]}")
        pool = Contract.from_abi("Swap", pool_address, SWAP_ABI)
        pool.withdrawAdminFees()

    # bridge admin fees to mainnet
    # TODO: approve gateway, correct _data argument
    for token_address in tokens:
        token = Contract.from_abi("Token", token_address, ERC20_ABI)
        amount_to_bridge = token.balanceOf(
            MULTISIG_ADDRESSES[CHAIN_IDS["ARBITRUM"]])
        print(
            f"Bridging ${token.symbol()} {amount_to_bridge / token.decimals()} to mainnet")
        # TODO: approve gateway here
        gateway_router.outboundTransfer(
            token_address,
            MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]],
            amount_to_bridge,
            "0x0".hex()  # TODO: correct _data argument
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
