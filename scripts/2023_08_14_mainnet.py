from ape_safe import ApeSafe
from brownie import Contract, accounts, chain, history, network

from helpers import (CHAIN_IDS, ENG_EOA_ADDRESS, ERC20_ABI,
                     INCITE_MULTISIG_ADDRESS, META_SWAP_ABI,
                     META_SWAP_DEPOSIT_ABI, MULTISIG_ADDRESSES,
                     OPS_MULTISIG_ADDRESSES, SDL_ADDRESSES,
                     SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS,
                     SDL_MINTER_ADDRESS, SWAP_ABI, VESTING_ABI)
from scripts.utils import (claim_admin_fees, confirm_posting_transaction,
                           pause_all_pools)

TARGET_NETWORK = "MAINNET"


def main():
    """
    This script 
    - claims admin fees from all Mainnet pools and sends them to Operations Multisig
    """

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
    )

    # Pause all pools
    pause_all_pools(multisig, CHAIN_IDS[TARGET_NETWORK])

    # Claim admin fees from all pools and send them to ops multisig
    claim_admin_fees(multisig, CHAIN_IDS[TARGET_NETWORK])

    # Send other tokens to ops multisig
    tokens_to_transfer = [
        "0xdBdb4d16EdA451D0503b854CF79D55697F90c8DF",  # ALCX
        "0xCe391315b414D4c7555956120461D21808A69F3A",  # Bao
        "0x5fAa989Af96Af85384b8a938c2EdE4A7378D9875",  # GAL
        "0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F",  # SNX
    ]

    # For each token, get the balance of the multisig, then transfer it to the ops multisig
    for token in tokens_to_transfer:
        token_contract = Contract.from_abi(
            "ERC20", token, ERC20_ABI, owner=multisig.address)
        token_balance = token_contract.balanceOf(multisig.address)
        print(f"Transferring {token_balance} of {token} to ops multisig")
        token_contract.transfer(
            OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]], token_balance
        )

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    # multisig.preview(safe_tx)
    for tx in history:
        tx.info()
    confirm_posting_transaction(multisig, safe_tx)
