import json
import urllib.request
from urllib.error import URLError

import click
from ape_safe import ApeSafe
from brownie import network
from gnosis.safe.safe_tx import SafeTx
from helpers import (
    ARB_BRIDGE_INBOX,
    ARB_GATEWAY_ROUTER,
    CHAIN_IDS,
    MULTISIG_ADDRESSES,
    MULTISIG_TRANSACTION_URLS,
)
from pytest import console_main


def confirm_posting_transaction(safe: ApeSafe, safe_tx: SafeTx):
    safe_nonce = safe_tx.safe_nonce

    current_nonce = 0
    try:
        url = f"{MULTISIG_TRANSACTION_URLS[network.chain.id]}/api/v1/safes/{safe.address}/multisig-transactions/"

        # fetch list of txs from gnosis api
        response = urllib.request.urlopen(url)
        data = json.load(response)

        # find last executed tx and set 'curent_nonce' as last executed tx + 1
        for result in data["results"]:
            if result["isExecuted"] == True:
                current_nonce = result["nonce"] + 1
                break
    except (URLError) as err:
        print(f"Fetching txs from gnosis api failed with error: {err}")
        current_nonce = click.prompt("Please input current nonce manually:", type=int)

    pending_nonce = safe.pending_nonce()

    # check if nonce is invalid or already in use
    if safe_nonce == 0:
        if (
            input(
                "Safe nonce is set to 0. This tx will be executed using pending "
                + f"nonce at the time of submission. Continue? [y/N]"
            )
        ) == "N":
            return
        else:
            safe_tx.safe_nonce = None
    elif safe_nonce < current_nonce:
        print(
            f"Error: Your nonce ({safe_nonce}) is already used. "
            + f"Please use a nonce greater equal {current_nonce}."
        )
        return
    elif safe_nonce < pending_nonce:
        if (
            input(
                f"There is already a pending transaction at nonce {safe_nonce}. "
                + "Are you sure you want to use duplicate nonce for this submission? [y/N]"
            )
        ) == "N":
            return
    elif safe_nonce > pending_nonce:
        if (
            input(
                f"Your nonce ({safe_nonce}) is greater than current pending nonce "
                + f"({pending_nonce}). Tx won't execute until intermediate nonces have "
                + "been used. Are you sure you want to post submission? [y/N]"
            )
        ) == "N":
            return

    should_post = click.confirm(
        f"Post this gnosis safe transaction to {safe.address} on {safe.base_url}?"
    )
    while True:
        if should_post:
            safe.post_transaction(safe_tx)
            print("Transaction posted to network")
            break
        else:
            should_post = click.confirm(
                f"Post this gnosis safe transaction to {safe.address} on {safe.base_url}?"
            )


def bridge_to_arbitrum(safe: ApeSafe, token_address: str, amount: int):
    # bridge to arbitrum
    token = safe.contract(token_address)

    # Find the the gate way for the token
    gateway_router = safe.contract(ARB_GATEWAY_ROUTER[CHAIN_IDS["MAINNET"]])
    gateway_address = gateway_router.getGateway(token.address)

    # Find the approval amount
    approval_amount = token.allowance(safe.address, gateway_address)

    # Approve more tokens to the gateway if needed
    if approval_amount < amount:
        token.approve(gateway_address, amount)

    # Calcualte the outbound call data
    outbound_calldata = gateway_router.getOutboundCalldata(
        token_address, MULTISIG_ADDRESSES["ARBITRUM"], amount, b""
    )

    # Calculate retryable submission fee
    inbox = safe.contract(ARB_BRIDGE_INBOX[CHAIN_IDS["MAINNET"]])
    inbox.calculateRetryableSubmissionFee(
        outbound_calldata + 256,
    )

    # TODO: Use the retryable submission fee as msg.value
    # Solidity code:
    # https://github.com/saddle-finance/saddle-contract/blob/29c785ce8d7788fcbe781129ce925679f36771c4/contracts/xchainGauges/bridgers/ArbitrumBridger.sol#L102-L124
