from helpers import (
    CHAIN_IDS,
    OPS_MULTISIG_ADDRESSES,
    ERC20_ABI,
    read_two_column_csv_to_dict
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract
from scripts.utils import (
    confirm_posting_transaction,
)
from brownie import history, Contract


TARGET_NETWORK = "MAINNET"


def main():
    """
    Send out SLP token based on historical veSDL holdings integral
    """

    print(f"You are using the '{network.show_active()}' network")
    assert (network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"

    ops_multisig = ApeSafe(
        OPS_MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]]
    )

    SLP_ADDRESS = "0x0C6F06b32E6Ae0C110861b8607e67dA594781961"
    SLP = Contract.from_abi("SLP", SLP_ADDRESS, ERC20_ABI)

    airdrop_dict = read_two_column_csv_to_dict(
        "../csv/veSDL_airdrop_amounts.csv")
    total_SLP_sent = 0

    for address in airdrop_dict.keys():
        amount = float(airdrop_dict[address])
        total_SLP_sent += amount
        SLP.transfer(address, amount * SLP.decimals())

    print(f"Total SLP sent: {total_SLP_sent}")

    # TODO: set 'safe_nonce'
    safe_tx = ops_multisig.multisend_from_receipts()
    safe_nonce = 6

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    # ops_multisig.preview(safe_tx)
    for tx in history:
        tx.info()
    confirm_posting_transaction(ops_multisig, safe_tx)
