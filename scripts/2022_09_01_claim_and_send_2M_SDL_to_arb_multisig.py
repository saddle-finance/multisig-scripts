import eth_abi
from ape_safe import ApeSafe
from brownie import Contract, accounts, network
from helpers import (ARBITRUM_L2_BRIDGE_ROUTER, CHAIN_IDS, DEPLOYER_ADDRESS, MULTISIG_ADDRESSES,
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

    # Release vested tokens to multisig account
    sdl_vesting_contract_proxy.release()
 
    # Send 2M SDL to deployer to bridge to arbitrum multisig
    sdl_contract.transfer(DEPLOYER_ADDRESS, 2_000_000 * 1e18)
    assert(sdl_contract.balanceOf(DEPLOYER_ADDRESS) == 2_000_000 * 1e18)

    # Combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 59

    # Sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
