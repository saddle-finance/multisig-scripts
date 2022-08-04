from helpers import CHAIN_IDS, MULTISIG_ADDRESSES, SWAP_ABI, MAINNET_POOL_ADDRESS_TO_POOL_NAME
from ape_safe import ApeSafe
from brownie import accounts, network
from scripts.utils import confirm_posting_transaction


TARGET_NETWORK = "MAINNET"


def main():
    """This script claims admin fees from all Eth mainnet pools"""

    print(f"You are using the '{network.show_active()}' network")
    assert(network.chain.id == CHAIN_IDS[TARGET_NETWORK]), \
        f"Not on {TARGET_NETWORK}"
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    # Run any pending transactions before simulating any more transactions
    multisig.preview_pending()

    pools = {
        "0x13Cc34Aa8037f722405285AD2C82FE570bfa2bdc",  # FRAXBP Pool
        "0x8cAEa59f3Bf1F341f89c51607E4919841131e47a",  # Frax 3Pool
        "0xC69DDcd4DFeF25D8a793241834d4cc4b3668EAD6",  # Saddle D4Pool
        "0x2bFf1B48CC01284416E681B099a0CDDCA0231d72",  # Saddle USX Pool
        "0xdf3309771d2BF82cb2B6C56F9f5365C8bD97c4f2",  # Saddle s/w/renBTCV2 Pool
        "0xFB516cF3710fC6901F2266aAEB8834cF5e4E9558",  # alUSDFRAX Metapool
        "0x69baA0d7c2e864b74173922Ca069Ac79d3be1556",  # sUSDFRAX Metapool
        "0xC765Cd3d015626244AD63B5FB63a97c5634643b9",  # FRAXUSDT Metapool
        "0x4568727f50c7246ded8C39214Ed6FF3c157f080D",  # Saddle sUSD Metapool
        "0x3F1d224557afA4365155ea77cE4BC32D5Dae2174",  # WCUSD Metapool
        "0xaCb83E0633d6605c5001e2Ab59EF3C745547C8C7",  # Saddle USD Pool
        "0xa6018520EAACC06C30fF2e1B3ee2c7c22e64196a",  # Saddle alETH Pool
        "0xfa9ED0309Bf79Eb84C847819F0B3CB84F6d351Af"   # Saddle TBTC Metapool
    }

    # execute txs for claiming admin fees
    # TODO: print out exact fee amounts that are claimable
    for pool_address in pools:
        print(
            f"Claiming admin fees from {MAINNET_POOL_ADDRESS_TO_POOL_NAME[pool_address]}")
        pool = Contract.from_abi("Swap", pool_address, SWAP_ABI)
        pool.withdrawAdminFees()

    # combine history into multisend txn
    # TODO: set 'safe_nonce'
    safe_tx = multisig.multisend_from_receipts()
    safe_nonce = 0

    safe_tx.safe_nonce = safe_nonce

    # sign with private key
    safe_tx.sign(accounts.load("deployer").private_key)  # prompts for password
    multisig.preview(safe_tx)
    confirm_posting_transaction(multisig, safe_tx)
