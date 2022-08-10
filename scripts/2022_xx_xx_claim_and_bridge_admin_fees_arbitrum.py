import this
from helpers import CHAIN_IDS, ERC20_ABI, ARBITRUM_L2_BRIDGE_ROUTER, MULTISIG_ADDRESSES, SWAP_ABI, ARBITRUM_POOL_ADDRESS_TO_POOL_NAME, L1_TO_L2_ERC20_ADDRESSES
from ape_safe import ApeSafe
from brownie import accounts, network, Contract
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "ARBITRUM"


def main():
    """This script claims admin fees from all Arbitrum pools and sends them to Mainnet"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["ARBITRUM"]])

    # Run any pending transactions before simulating any more transactions
    multisig.preview_pending()

    MAX_POOL_LENGTH = 32

    # Arbitrum L2 gateway router
    gateway_router = multisig.contract(
        ARBITRUM_L2_BRIDGE_ROUTER[CHAIN_IDS["ARBITRUM"]]
    )

    # swap -> metaswapDeposit dict
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

    # log out unique set of tokens of all pools
    token_symbols = set()
    for token_address in token_addresses:
        token_symbols.add(Contract.from_abi(
            "ERC20", token_address, ERC20_ABI).symbol()
        )
    print(f"Found {len(token_symbols)} tokens: {token_symbols}")

    # execute txs for claiming admin fees
    for swap_address in swap_to_deposit_dict:
        print(
            # TODO: change this to LP token name
            f"Claiming admin fees from {ARBITRUM_POOL_ADDRESS_TO_POOL_NAME[swap_address]}"
        )
        pool = Contract.from_abi("Swap", swap_address, SWAP_ABI)
        pool.withdrawAdminFees(
            {"from": MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]})

    # find L1 addresses of tokens for bridging
    L2_to_L1_dict = {}
    for L1_address in L1_TO_L2_ERC20_ADDRESSES:
        for L2_address_key in L1_TO_L2_ERC20_ADDRESSES[L1_address]:
            L2_address = L1_TO_L2_ERC20_ADDRESSES[L1_address][L2_address_key]
            if L2_address in token_addresses:
                L2_to_L1_dict[L2_address] = L1_address
    print(
        L2_to_L1_dict
    )

    # bridge fees to mainnet
    for token_address in token_addresses:
        # the token to be bridged
        token_contract = Contract.from_abi("ERC20", token_address, ERC20_ABI)

        # bridge all available balance
        amount_to_bridge = token_contract.balanceOf(
            MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
        )
        print(
            f"Bridging ${token_contract.symbol()} {amount_to_bridge / token_contract.decimals()} to mainnet"
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
            "0x0".hex()
        )
