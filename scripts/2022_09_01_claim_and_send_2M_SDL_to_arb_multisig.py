import eth_abi
from ape_safe import ApeSafe
from brownie import Contract, accounts, network
from helpers import (ARBITRUM_L2_BRIDGE_ROUTER, CHAIN_IDS, MULTISIG_ADDRESSES,
                     SDL_ADDRESSES, SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS)

from scripts.utils import confirm_posting_transaction


def main():
    """
    Claims SDL from community vesting contract then sends 2M to arbitrum multisig for sperax token swap.
    Vote: https://snapshot.org/#/saddlefinance.eth/proposal/0x3003e0e20359f2bb253705e408ac33de338c2b57fbe38e53ab9f4e15730c1b51
    """
    TARGET_NETWORK = "MAINNET"

    print(f"You are using the '{network.show_active()}' network")
    assert network.chain.id == CHAIN_IDS[TARGET_NETWORK], f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    sdl_contract = multisig.contract(SDL_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])
    sdl_vesting_contract_proxy = multisig.contract(
        SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]
    )
    arbitrum_l2_bridge_router = multisig.contract(
        ARBITRUM_L2_BRIDGE_ROUTER[CHAIN_IDS[TARGET_NETWORK]])

    # release vested tokens to multisig account
    sdl_vesting_contract_proxy.release()

    # bridge some to arbitrum multisig
    amount_to_arb_multisig = 1 * 1e18
    gas_limit_l2 = 1000000
    gas_price_l2 = 990000000
    max_submisstion_cost_l2 = 10000000000000

    # Using msg.value that is less or more will cause the tx to revert
    value = gas_limit_l2 * gas_price_l2 + max_submisstion_cost_l2

    # get multisig address on arbitrum network
    arb_multisig_address = MULTISIG_ADDRESSES[CHAIN_IDS["ARBITRUM"]]
    sdl_gateway_address = arbitrum_l2_bridge_router.getGateway(sdl_contract.address)

    # Approve SDL to be taken by the gateway for SDL
    sdl_contract.approve(sdl_gateway_address, amount_to_arb_multisig)

    # Encode data
    arb_encoded = (
        "0x"
        + eth_abi.encode_abi(["uint256", "bytes32[]"],
                             [max_submisstion_cost_l2, []]).hex()
    )

    # Bridge to arbitrum
    arbitrum_l2_bridge_router.outboundTransfer(
        sdl_contract.address,
        arb_multisig_address,
        amount_to_arb_multisig,
        gas_limit_l2,
        gas_price_l2,
        arb_encoded,
        {"value": value},
    )

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 59

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
