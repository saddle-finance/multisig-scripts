from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, VESTING_ABI, INCITE_MULTISIG_ADDRESS
from ape_safe import ApeSafe
from brownie import accounts, network, Contract
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "MAINNET"
def main():
    """Release tokens and shift beneficiary for vesting contracts of outgoing employees"""

    print(f"You are using the '{network.show_active()}' network")
    assert(network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]], "https://safe-transaction-mainnet.safe.global")

    # Run any pending transactions before simulating any more transactions
    multisig.preview_pending()

    target_addresses = [
      "0xC7B2F1a2D0838370f88a2FD5c2E3F64D8aF89a18", # Art
      "0xd17c31796d3Cb41d9d211904780320C4be286172" # Sandra
    ]
    for vesting_address in target_addresses:
      vesting_contract = Contract.from_abi(
          "Vesting",
          vesting_address,
          VESTING_ABI,
          multisig.account,
      )
      vesting_contract.release()
      vesting_contract.changeBeneficiary(INCITE_MULTISIG_ADDRESS)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_nonce = 75

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key) # prompts for password
    multisig.preview(safe_tx)
    confirm_posting_transaction(multisig, safe_tx)
