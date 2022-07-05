from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, SDL_ADDRESSES, SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS
from ape_safe import ApeSafe
from brownie import accounts, network
from eth_utils import to_wei

from scripts.utils import confirm_posting_transaction


def main():
    """Send the 186k SDL to affected LPs according to https://dune.com/queries/985291"""

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])
    sdl_vesting_contract_proxy = multisig.contract(
        SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS[CHAIN_IDS["MAINNET"]]
    )

    # release vested tokens to deployer account
    sdl_vesting_contract_proxy.release()

    refunds = {
        "0xb577cc8aa76d3607067934fd6477f0a392194a83": 157480.1266,
        "0x5c1b560c7a30483cf434b3e4cc1338af52df4c8b": 10681.07975,
        "0x87c19db664b77b1055f1ed678fd3ba7141ed3336": 5303.956424,
        "0x91793bce7edb1fc028e5854b93344069355bbb8b": 4334.284605,
        "0xab58779cec2b82a75ffd103fdc88d7e3adb13468": 3420.257569,
        "0xb051eedd14cf9c7297a24b63c28b049fcce838e8": 1938.481046,
        "0xfe4841a4615b8132e6e116a033ca39333c63d121": 1718.894205,
        "0x9664794af710aee954e80b9714daeaeec515fb33": 979.7590044,
        "0xd131f1bcdd547e067af447dd3c36c99d6be9fdeb": 370.6670858,
        "0x856b63349fb6c818ea7cd7305483ae0ef6956f6c": 14.25321833,
    }
    total = sum(refunds.values())
    print(f"Total amount to be refunded: {total} SDL")
    sdl_contract = multisig.contract(SDL_ADDRESSES[CHAIN_IDS["MAINNET"]])
    for address, amount in refunds.items():
        sdl_contract.transfer(address, amount * 1e18)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 44

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
