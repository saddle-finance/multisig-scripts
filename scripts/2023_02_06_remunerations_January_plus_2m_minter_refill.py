

from helpers import (
    CHAIN_IDS,
    MULTISIG_ADDRESSES,
    SDL_ADDRESSES,
    GNOSIS_SAFE_BASE_URLS,
    SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS,
    SDL_MINTER_ADDRESS,
    VESTING_ABI
)
from ape_safe import ApeSafe
from brownie import accounts, network, Contract
from eth_utils import to_wei
from scripts.utils import confirm_posting_transaction

TARGET_NETWORK = "MAINNET"


def main():
    """
    - Send last batch of ~1.69m SDL (5% of total) for January 2023 
    to affected LPs according to https://snapshot.org/#/saddlefinance.eth/proposal/0xf27b07ef7025aa23edb2a84d56825511ea7adff8d6164cd09a23c63c42cdc01a
    - Claim SDL from vesting contract 
    - Transfer 2_000_000 SDL to minter
    """

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer")  # prompts for password

    multisig = ApeSafe(
        MULTISIG_ADDRESSES[CHAIN_IDS[TARGET_NETWORK]],
        GNOSIS_SAFE_BASE_URLS[CHAIN_IDS[TARGET_NETWORK]]
    )

    # December remunerations
    refunds = {
        '0xa0f75491720835b36edc92d06ddc468d201e9b73': 388195.348036185,
        '0x38ee5f5a39c01cb43473992c12936ba1219711ab': 377228.2524536725,
        '0x38f9abd4bd8947da035abf51fc21244108a81ca6': 283110.6372091625,
        '0x0ea4a285e1353f490ec7f473ab3174cac71cf79a': 283054.98392423,
        '0x6ef3f0ff397c3de367c6ca2cc3e6b6955e7993a5': 45814.168072575,
        '0x6a73204db71f8e054bf9a0680b02ae96f700b595': 45316.406746405,
        '0x5eea118e75f247014c6d0e990f02a0c254edc852': 37829.766448069,
        '0x2b9d8f558e02753ed7d4d97dedfad662c02af3cb': 37749.6408610815,
        '0x0bb31c6278d58cff41b7e8ed3b20f76424fd69ad': 37734.0503836925,
        '0xc7d2a419f8f2eaa06b3811cf7faaa7440dcf96b7': 37722.1449313995,
        '0xae1e5c84b73136a49efb70a15149c350015391ed': 28313.8133121985,
        '0xe2d079278c0f4959199136f8db11c645d69a292b': 28308.7109771075,
        '0xffd4dae0d7d8ddb6f408dca0a47763ae3a57f4ce': 15570.1595401995,
        '0x9c7d894a29f97636b66dea646a1ae2f9c83a2830': 13612.6573698775,
        '0x77956a9d1b9901bbe4cfc2ed37db17500fbe7b0c': 9422.0323405625,
        '0x02ef8147e2d0997cca48d99f01bad846d16558fa': 7542.012746875,
        '0xc7193c01f43257f3fe4c8f86784fcaa578a9e2b1': 6034.739792375,
        '0xd716ad4f10eade5af4ed10006678f49bd2e6624f': 1886.350382875,
        '0x99eb33756a2eaa32f5964a747722c4b59e6af351': 803.715183375,
        '0x2a1eaf114f2c23d30ef571d6e84fcbeb2f6f4e62': 377.475764,
        '0x46866d274e6d9015c5fdc098ce270803e11e3ef4': 207.49702475,
        '0x2d5d79753bb8e02ca1ce8ece0aa55288f8c8d840': 103.748512375,
        '0xb5e46afa9596cb6f44d2fcb6dbd2096dbe35396c': 18.989557625,
        '0x74f8744020f5900a2c3a3289c6c2182f56a6901f': 5.198384375
    }

    total = sum(refunds.values())
    print(f"Total amount to be refunded: {total} SDL")
    sdl_contract = Contract.from_explorer(SDL_ADDRESSES[CHAIN_IDS["MAINNET"]])
    for address, amount in refunds.items():
        sdl_contract.transfer(
            address,
            amount * 1e18,
            {"from": multisig.address}
        )

    sdl_vesting_contract_proxy = multisig.get_contract(
        SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS[CHAIN_IDS[TARGET_NETWORK]]
    )

    # Claim SDL from vesting contract
    sdl_vesting_contract_proxy.release()

    # Transfer 2m SDL to minter
    sdl_contract.transfer(SDL_MINTER_ADDRESS[CHAIN_IDS["MAINNET"]], 2_000_000)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.safe_nonce = 83

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)
    confirm_posting_transaction(multisig, safe_tx)
