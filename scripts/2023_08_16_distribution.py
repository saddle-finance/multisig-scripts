import time
from pathlib import Path

from brownie import Contract, accounts, chain, history, network
from brownie_safe import BrownieSafe

from helpers import (CHAIN_IDS, ENG_EOA_ADDRESS, ERC20_ABI,
                     INCITE_MULTISIG_ADDRESS, META_SWAP_ABI,
                     META_SWAP_DEPOSIT_ABI, MULTISIG_ADDRESSES,
                     OPS_MULTISIG_ADDRESSES, SDL_ADDRESSES,
                     SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS,
                     SDL_MINTER_ADDRESS, SWAP_ABI, VESTING_ABI, WENTOKENS_ABI,
                     get_contract_from_deployment)
from scripts.utils import (claim_admin_fees, confirm_posting_transaction,
                           pause_all_pools)

TARGET_NETWORKS = ["MAINNET", "ARBITRUM", "OPTIMISM"]

mod_path = Path(__file__).parent


def main():
    """
    Uses distribution.csv in the root folder to distribute tokens to users
    csv is in format of [address, eth_amount, arb_amount, chain_id]
    Since this is a mainnet script, we will use the multisig to send eth for each user with chain_id 1
    First print out the total amount of eth required to send to users
    call multisig.account.transfer(addr, amount) to send eth to each user
    """

    print(f"You are using the '{network.show_active()}' network")

    assert (network.chain.id in [CHAIN_IDS[x] for x in TARGET_NETWORKS]), \
        f"Not on {TARGET_NETWORKS}"
    multisig = BrownieSafe(
        MULTISIG_ADDRESSES[network.chain.id],
    )
    wentokens = Contract.from_abi(
        f"WenTokens", "0x2c952eE289BbDB3aEbA329a4c41AE4C836bcc231", WENTOKENS_ABI, multisig.account)

    distribution_csv = open((mod_path / "../distribution.csv").resolve(), "r")
    distribution_csv.readline()  # skip header
    total_token_required = 0
    recipients = []
    amounts = []

    token_ticker = "ARB" if network.chain.id == CHAIN_IDS["ARBITRUM"] else "ETH"

    for line in distribution_csv:
        addr, eth_amount, arb_amount, chain_id = line.split(",")
        if int(chain_id) == network.chain.id:
            distribution_amount = int(
                eth_amount) if token_ticker == "ETH" else int(arb_amount)
            total_token_required += distribution_amount
            recipients.append(addr)
            amounts.append(distribution_amount)

    if (token_ticker == "ETH"):
        total_token_in_multisig = multisig.account.balance()
    else:
        arbitrum_token = Contract.from_abi(f"ARB",
                                           "0x912CE59144191C1204E64559FE8253a0e49E6548", ERC20_ABI, multisig.account)
        total_token_in_multisig = arbitrum_token.balanceOf(
            multisig.address)

    print(
        f"Total {token_ticker} in multisig: {total_token_in_multisig / 1e18}")
    print(f"Total {token_ticker} required   : {total_token_required / 1e18}")

    assert total_token_in_multisig >= total_token_required, f"Not enough {token_ticker} in multisig"

    if token_ticker == "ETH":
        # for i in range(len(recipients)):
        #     print(f"Sending {amounts[i]} {token_ticker} to {recipients[i]}")
        #     multisig.account.transfer(recipients[i], amounts[i])
        tx = wentokens.airdropETH(recipients, amounts, {
            "value": total_token_required})

        # combine history into multisend txn
        safe_tx = multisig.tx_from_receipt(tx)
        safe_tx.sign(accounts.load("deployer").private_key)
        multisig.preview(safe_tx)
        confirm_posting_transaction(multisig, safe_tx)
    else:
        MAX_LENGTH = 800
        start_safe_nonce = 29
        nonce_offset = 0
        arbitrum_token.approve(wentokens.address, total_token_required)

        # Batch every 500 recipients and amounts to avoid gas limit
        # use wentokens.airdropERC20(tokenAddress, recipients, amounts, total_token_required_for_this_batch)
        # total_token_required_for_this_batch is calculated by summing the amount of tokens to be sent in this batch
        for i in range(0, len(recipients), MAX_LENGTH):
            # Print out summary for this batch. Ensure we are not reading out of index
            # Use min function to ensure we don't read out of index
            batch_start_index = i
            batch_end_index = min(i + MAX_LENGTH, len(recipients))
            batch_amount = sum(amounts[i:batch_end_index])
            print(
                f"Sending {batch_amount} {token_ticker} for users from {batch_start_index}:{recipients[batch_start_index]} to {batch_end_index - 1}:{recipients[batch_end_index - 1]}")

            tx = wentokens.airdropERC20(arbitrum_token.address, recipients[batch_start_index:batch_end_index], amounts[batch_start_index:batch_end_index],
                                        batch_amount)

            if len(history.from_sender(multisig.address)) > 1:
                safe_tx = multisig.multisend_from_receipts()
            else:
                safe_tx = multisig.tx_from_receipt(tx)
            # sign with private key
            safe_tx.safe_nonce = start_safe_nonce + nonce_offset
            safe_tx.sign(accounts.load("deployer").private_key)
            # multisig.preview(safe_tx, events=False)
            confirm_posting_transaction(multisig, safe_tx)
            nonce_offset = nonce_offset + 1
