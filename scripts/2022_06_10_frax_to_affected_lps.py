from helpers import CHAIN_IDS, MULTISIG_ADDRESSES
from ape_safe import ApeSafe
from brownie import accounts, network
from eth_utils import to_wei

from scripts.utils import confirm_posting_transaction


def main():
    """Send the 3m FRAX recovered by BlockSec to affected LPs according to https://dune.com/queries/689792"""
    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    refunds = {
        "0xa0f75491720835b36edc92d06ddc468d201e9b73": to_wei(690754.4172, "ether"),
        "0x38ee5f5a39c01cb43473992c12936ba1219711ab": to_wei(671239.5782, "ether"),
        "0x38f9abd4bd8947da035abf51fc21244108a81ca6": to_wei(503766.787, "ether"),
        "0x0ea4a285e1353f490ec7f473ab3174cac71cf79a": to_wei(503667.7576, "ether"),
        "0x6ef3f0ff397c3de367c6ca2cc3e6b6955e7993a5": to_wei(81521.68522, "ether"),
        "0x6a73204db71f8e054bf9a0680b02ae96f700b595": to_wei(80635.96921, "ether"),
        "0x5eea118e75f247014c6d0e990f02a0c254edc852": to_wei(67314.24889, "ether"),
        "0x2b9d8f558e02753ed7d4d97dedfad662c02af3cb": to_wei(67171.6735, "ether"),
        "0x0bb31c6278d58cff41b7e8ed3b20f76424fd69ad": to_wei(67143.93182, "ether"),
        "0xc7d2a419f8f2eaa06b3811cf7faaa7440dcf96b7": to_wei(67122.74727, "ether"),
        "0xae1e5c84b73136a49efb70a15149c350015391ed": to_wei(50381.57132, "ether"),
        "0xe2d079278c0f4959199136f8db11c645d69a292b": to_wei(50372.49223, "ether"),
        "0xffd4dae0d7d8ddb6f408dca0a47763ae3a57f4ce": to_wei(27705.52644, "ether"),
        "0x9c7d894a29f97636b66dea646a1ae2f9c83a2830": to_wei(24222.34902, "ether"),
        "0x77956a9d1b9901bbe4cfc2ed37db17500fbe7b0c": to_wei(16765.555, "ether"),
        "0x02ef8147e2d0997cca48d99f01bad846d16558fa": to_wei(13420.25, "ether"),
        "0xc7193c01f43257f3fe4c8f86784fcaa578a9e2b1": to_wei(10738.21, "ether"),
        "0xd716ad4f10eade5af4ed10006678f49bd2e6624f": to_wei(3356.57, "ether"),
        "0x99eb33756a2eaa32f5964a747722c4b59e6af351": to_wei(1430.13, "ether"),
        "0x2a1eaf114f2c23d30ef571d6e84fcbeb2f6f4e62": to_wei(671.68, "ether"),
        "0x46866d274e6d9015c5fdc098ce270803e11e3ef4": to_wei(369.22, "ether"),
        "0x2d5d79753bb8e02ca1ce8ece0aa55288f8c8d840": to_wei(184.61, "ether"),
        "0xb5e46afa9596cb6f44d2fcb6dbd2096dbe35396c": to_wei(33.79, "ether"),
        "0x74f8744020f5900a2c3a3289c6c2182f56a6901f": to_wei(9.25, "ether"),
    }
    total = sum(refunds.values())
    print(f"Total amount to be refunded: {total} FRAX")
    frax = multisig.contract("0x853d955aCEf822Db058eb8505911ED77F175b99e")
    for address, amount in refunds.items():
        frax.transfer(address, amount)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 37

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
