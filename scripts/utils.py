import json
import urllib.request
from urllib.error import URLError

import click
import eth_abi
from ape_safe import ApeSafe
from brownie import Contract, chain
from gnosis.safe.safe_tx import SafeTx
from helpers import (
    ARBITRUM_BRIDGE_INBOX,
    ARBITRUM_BRIDGE_INBOX_ABI,
    ARBITRUM_L2_BRIDGE_ROUTER,
    CHAIN_IDS,
    DEPLOYER_ADDRESS,
    MINICHEF_ADDRESSES,
    MULTISIG_ADDRESSES,
    OPTIMISM_STANDARD_BRIDGE,
    SDL_ADDRESSES,
)
from pytest import console_main


def confirm_posting_transaction(safe: ApeSafe, safe_tx: SafeTx):
    safe_nonce = safe_tx.safe_nonce

    current_nonce = 0
    try:
        url = safe.base_url + f"/api/v1/safes/{safe.address}/multisig-transactions/"

        # fetch list of txs from gnosis api
        response = urllib.request.urlopen(url)
        data = json.load(response)

        # find last executed tx and set 'curent_nonce' as last executed tx + 1
        for result in data["results"]:
            if result["isExecuted"] == True:
                current_nonce = result["nonce"] + 1
                break
    except (URLError) as err:
        console_main.log(f"Fetching txs from gnosis api failed with error: {err}")
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


def bridge_to_arbitrum_minichef(safe: ApeSafe, token_address: str, amount: int):
    print(f"Attempting to bridge tokens at {token_address} to Arbitrum")

    # Solidity code:
    # https://github.com/saddle-finance/saddle-contract/blob/29c785ce8d7788fcbe781129ce925679f36771c4/contracts/xchainGauges/bridgers/ArbitrumBridger.sol#L102-L124

    # bridge to arbitrum
    token = safe.contract(token_address)
    abi = json.load(open("abis/ArbitrumL2BridgeRouter.json"))
    gateway_router = Contract.from_abi(
        "GateWayRouter",
        ARBITRUM_L2_BRIDGE_ROUTER[CHAIN_IDS["MAINNET"]],
        abi,
        owner=DEPLOYER_ADDRESS,
    )

    # Find the the gate way for the token
    gateway_router = safe.contract(ARBITRUM_L2_BRIDGE_ROUTER[CHAIN_IDS["MAINNET"]])
    print("Fetching L2 token address")
    gateway_address = gateway_router.getGateway(token.address)
    print(f"L2 token address found at {gateway_address}")
    # Find the approval amount
    approval_amount = token.allowance(safe.address, gateway_address)

    # Approve more tokens to the gateway if needed
    if approval_amount < amount:
        token.approve(gateway_address, amount)

    # Calcualte the outbound call data
    print("Calculating outbound call data")
    outbound_calldata = gateway_router.getOutboundCalldata(
        token_address,
        DEPLOYER_ADDRESS,
        MULTISIG_ADDRESSES[CHAIN_IDS["ARBITRUM"]],
        amount,
        b"",
    )
    print(f"Outbound call data: {outbound_calldata}")

    # Get current block and base fee
    block = chain.height
    # TODO: is this correct?
    # base_fee = chain.base_fee
    print(chain[block])
    # base_fee = chain[block].baseFeePerGas #TODO: does not work
    base_fee = 47211945345
    # print("basefee", base_fee)

    # Calculate retryable submission fee
    print("Attempting to get retryable submission fee")
    inbox = Contract.from_abi(
        "inbox",
        (ARBITRUM_BRIDGE_INBOX[CHAIN_IDS["MAINNET"]]),
        ARBITRUM_BRIDGE_INBOX_ABI,
    )

    retryableFee = inbox.calculateRetryableSubmissionFee(
        outbound_calldata + 256,
        base_fee,  # block base fee
    )
    print("Retryable submission fee", retryableFee)

    # Gas price constants
    gasLimitL2 = 1000000
    gasPriceL2 = 990000000

    print("Submitting retryable transfer to Arbitrum L1 Router")
    # Submit the retryable transaction
    print(
        token_address,  # L1 token
        DEPLOYER_ADDRESS,  # L1 owner (receier of gas refund)
        MULTISIG_ADDRESSES[CHAIN_IDS["ARBITRUM"]],  # to
        amount,
        gasLimitL2,
        gasPriceL2,
        "0x" + eth_abi.encode_abi(["uint256", "bytes32[]"], [retryableFee, []]).hex(),
    )
    # gateway_router.outboundTransferCustomRefund(
    #     token_address,  # L1 token
    #     DEPLOYER_ADDRESS,  # L1 owner (receier of gas refund)
    #     MULTISIG_ADDRESSES["ARBITRUM"],  # to
    #     amount,
    #     gasLimitL2,
    #     gasPriceL2,
    #     "0x" + eth_abi.encode_abi(["uint256", "bytes32[]"], [retryableFee, []]).hex(),
    #     {"value": gasLimitL2 * gasPriceL2 + retryableFee},
    # )


def bridge_to_optimism(safe: ApeSafe, token_address: str, amount: int):
    token = safe.contract(token_address)
    optimism_L1_standard_bridge = safe.contract(
        OPTIMISM_STANDARD_BRIDGE[CHAIN_IDS["MAINNET"]]
    )

    # Find the approval amount
    approval_amount = token.allowance(safe.address, optimism_L1_standard_bridge.address)

    # Approve more tokens to the gateway if needed
    if approval_amount < amount:
        token.approve(optimism_L1_standard_bridge, amount)

    # approve bridge
    token.approve(optimism_L1_standard_bridge.address, amount)

    # gas limit required to complete the deposit on L2
    l2gas = "0x1e8480"  # 2,000,000

    # Optimism bride code https://etherscan.io/address/0x40e0c049f4671846e9cff93aaed88f2b48e527bb#code
    # send to Optimism minichef
    print("Sending tokens to Optimism minichef")
    optimism_L1_standard_bridge.depositERC20To(
        token_address,  # _l1token
        SDL_ADDRESSES[CHAIN_IDS["OPTIMISM"]],  # _l2token
        MINICHEF_ADDRESSES[CHAIN_IDS["OPTIMISM"]],  # _to
        amount,  # _amount
        l2gas,  # _l2gas
        "0x",  # _data
    )
