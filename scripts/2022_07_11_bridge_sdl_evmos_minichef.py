from helpers import (
    CHAIN_IDS,
    MINICHEF_ADDRESSES,
    MULTISIG_ADDRESSES,
    NOMAD_GATEWAY_ABI,
    SDL_ADDRESSES,
    EVMOS_NOMAD_ERC20_BRIDGE_ROUTER,
)
from ape_safe import ApeSafe
from brownie import Contract, accounts, network

from scripts.utils import confirm_posting_transaction, fetch_current_nonce


def main():
    """Bridges 187,418 SDL to EVMOS minichef using the Nomad Gateway contract"""

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer")  # prompts for password
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    sdl_contract = multisig.contract(SDL_ADDRESSES[CHAIN_IDS["MAINNET"]])
    
    # Fetch abi from the target contract directly
    evmos_l1_gateway = Contract.from_abi(
        "EvmosL1Gateway",
        EVMOS_NOMAD_ERC20_BRIDGE_ROUTER[CHAIN_IDS["MAINNET"]],
        NOMAD_GATEWAY_ABI,
        multisig.account
    )

    # Send needed SDL to EVMOS minichef
    amountToSendEvmosMinichef = 187418984788359784835428
    NomadEVMOSMainnetDestinationCode = "1702260083"
    evmosMiniChefAddress = MINICHEF_ADDRESSES[CHAIN_IDS["EVMOS"]]
    evmos_encoded = "0x" + evmosMiniChefAddress[2:].zfill(64)
    sdl_contract.approve(evmos_l1_gateway.address, amountToSendEvmosMinichef)
    evmos_l1_gateway.send(
        sdl_contract.address,
        amountToSendEvmosMinichef,
        NomadEVMOSMainnetDestinationCode,
        # .to_bytes convert by default to bytes32 then decode to str
        evmos_encoded,
        False,
    )

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()
    safe_tx.current_nonce = fetch_current_nonce(multisig)

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
