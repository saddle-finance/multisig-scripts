from ape_safe import ApeSafe
from brownie import Contract, accounts, chain, history, network

from helpers import (CHAIN_IDS, ERC20_ABI, MULTISIG_ADDRESSES,
                     OPS_MULTISIG_ADDRESSES)
from scripts.utils import (claim_admin_fees, confirm_posting_transaction,
                           pause_all_pools)

TARGET_NETWORK = "ARBITRUM"


def main():
    """This script claims admin fees from all Arbitrum pools, sends them to Ops multisig"""

    print(f"You are using the '{network.show_active()}' network")
    print(f"Network id: {network.chain.id}")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]])

    # Run any pending transactions before simulating any more transactions
    # multisig.preview_pending()

    # Pause all pools
    pause_all_pools(multisig, CHAIN_IDS[TARGET_NETWORK])

    # claim admin fees
    claim_admin_fees(multisig, CHAIN_IDS[TARGET_NETWORK])

    # Send other tokens to ops multisig
    tokens_to_transfer = [
        "0x912CE59144191C1204E64559FE8253a0e49E6548",  # Arb
        "0x5575552988A3A80504bBaeB1311674fCFd40aD4B",  # SPA
        "0x2CaB3abfC1670D1a452dF502e216a66883cDf079",  # L2DAO
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
