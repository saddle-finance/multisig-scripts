import this
from helpers import (
    CHAIN_IDS,
    ERC20_ABI,
    MULTISIG_ADDRESSES,
    OPS_MULTISIG_ADDRESSES,
    EVMOS_CELER_LIQUIDITY_BRIDGE,
    EVMOS_CELER_LIQUIDITY_BRIDGE_ABI,
)
from fee_distro_helpers import (
    token_addresses
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract, chain
from scripts.utils import confirm_posting_transaction, convert_fees_to_USDC_saddle


TARGET_NETWORK = "EVMOS"


def main():
    """This script claims admin fees from all Evmos pools, then converts them to ceUSDC and sends them to Mainnet"""

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    ops_multisig = ApeSafe(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        base_url='https://safe.evmos.org/'
    )

    # Run any pending transactions before simulating any more transactions
    # ops_multisig.preview_pending()

    convert_fees_to_USDC_saddle(ops_multisig, CHAIN_IDS[TARGET_NETWORK])

    # Optimism L2 Standard Bridge
    liquidity_bridge = Contract.from_abi(
        "EvmosCelerLiquidityBridge",
        EVMOS_CELER_LIQUIDITY_BRIDGE[CHAIN_IDS[TARGET_NETWORK]],
        EVMOS_CELER_LIQUIDITY_BRIDGE_ABI
    )

    # bridge 100% of USDC balance to mainnet ops ops_multisig
    ceUSDC_contract = Contract.from_abi(
        "ERC20", token_addresses[CHAIN_IDS[TARGET_NETWORK]]["USDC"], ERC20_ABI)
    amount_to_bridge = ceUSDC_contract.balanceOf(
        ops_multisig.address
    )

    print(
        f"Approving bridge for ${ceUSDC_contract.symbol()} {amount_to_bridge / (10 ** ceUSDC_contract.decimals())}"
    )
    # approve gateway
    ceUSDC_contract.approve(
        liquidity_bridge,
        amount_to_bridge,
        {"from": ops_multisig.address}
    )

    # send USDC to mainnet main multisig
    print(
        f"Bridging ${ceUSDC_contract.symbol()} {amount_to_bridge / (10 ** ceUSDC_contract.decimals())} to mainnet"
    )
    # @dev
    # for ref: https://cbridge-docs.celer.network/developer/api-reference/contract-pool-based-transfer
    # Celer suggests using timestamp as nonce
    liquidity_bridge.send(
        MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]],   # _receiver
        token_addresses[
            CHAIN_IDS[TARGET_NETWORK]]["USDC"],     # _token
        amount_to_bridge,                           # _amount
        1,                                          # _dstChainId (eth mainnet)
        chain[chain.height].timestamp,              # _nonce
        5000,                                       # _maxSlippage (in pips)
        {"from": ops_multisig.address}
    )

    assert ceUSDC_contract.balanceOf(ops_multisig.address) == 0

    # combine history into multisend txn
    # TODO: set 'safe_nonce'
    safe_tx = ops_multisig.multisend_from_receipts()
    safe_nonce = 0

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    ops_multisig.preview(safe_tx)
    confirm_posting_transaction(ops_multisig, safe_tx)
