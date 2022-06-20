from math import ceil
from multiprocessing import pool
from helpers import (
    CHAIN_IDS,
    MINICHEF_ADDRESSES,
    MULTISIG_ADDRESSES,
    SDL_ADDRESSES,
    ARBITRUM_L2_BRIDGE_ROUTER,
    EVMOS_NOMAD_ERC20_BRIDGE_ROUTER,
    SDL_MINTER_ADDRESS,
)
from ape_safe import ApeSafe
from brownie import accounts, network
import web3 as Web3

from scripts.utils import confirm_posting_transaction
import eth_abi


def main():
    """Add SimpleRewarder for T to minichef"""

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer")  # prompts for password
    print("deployer.balance(): ", deployer.balance())

    if network.show_active() == "mainnet-fork":
        accounts[0].transfer(deployer, "1 ether")
    print("deployer.balance(): ", deployer.balance())
    multisig = ApeSafe(MULTISIG_ADDRESSES[CHAIN_IDS["MAINNET"]])

    minichef = multisig.contract(MINICHEF_ADDRESSES[CHAIN_IDS["MAINNET"]])
    sdl_contract = multisig.contract(SDL_ADDRESSES[CHAIN_IDS["MAINNET"]])
    arbitrum_L1_Gateway = multisig.contract(
        ARBITRUM_L2_BRIDGE_ROUTER[CHAIN_IDS["MAINNET"]]
    )
    evmos_L1_Gateway = multisig.contract(
        EVMOS_NOMAD_ERC20_BRIDGE_ROUTER[CHAIN_IDS["MAINNET"]]
    )

    # Enable transferability of SDL
    sdl_contract.enableTransfer()

    # Pause MiniChef rewards on mainnet and update pools
    minichef.setSaddlePerSecond(0)

    poolLength = list(map(str, list(range(1, minichef.poolLength()))))
    minichef.massUpdatePools(poolLength)

    # Send needed SDL to minichef
    amountToSendMainnetMiniChef = ceil(7543898) * 1e18
    sdl_contract.transfer(minichef.address, amountToSendMainnetMiniChef)

    # Send needed SDL to Arbitrum minichef
    amountToSendArbitrumMiniChef = ceil(8974940) * 1e18
    gasLimitL2 = 1000000
    gasPriceL2 = 990000000
    maxSubmisstionCostL2 = 10000000000000
    arbitrumMinichefAddress = MINICHEF_ADDRESSES[CHAIN_IDS["ARBITRUM"]]
    sdlGatewayAddress = arbitrum_L1_Gateway.getGateway(sdl_contract.address)
    sdl_contract.approve(sdlGatewayAddress, amountToSendArbitrumMiniChef)
    arb_encoded = (
        "0x"
        + eth_abi.encode_abi(["uint256", "bytes32[]"], [maxSubmisstionCostL2, []]).hex()
    )

    arbitrum_L1_Gateway.outboundTransfer(
        sdl_contract.address,
        arbitrumMinichefAddress,
        amountToSendArbitrumMiniChef,
        gasLimitL2,
        gasPriceL2,
        arb_encoded,
        {"value": 1e15},
    )

    # Send needed SDL to EVMOS minichef
    amountToSendEvmosMinichef = ceil(197135) * 1e18
    NomadEVMOSMainnetDestinationCode = "1702260083"
    evmosMiniChefAddress = MINICHEF_ADDRESSES[CHAIN_IDS["EVMOS"]]
    evmos_encoded = "0x" + evmosMiniChefAddress[2:].zfill(64)
    sdl_contract.approve(evmos_L1_Gateway.address, amountToSendEvmosMinichef)
    evmos_L1_Gateway.send(
        sdl_contract.address,
        amountToSendEvmosMinichef,
        NomadEVMOSMainnetDestinationCode,
        # .to_bytes convert by default to bytes32 then decode to str
        evmos_encoded,
        False,
    )

    # Send needed SDL to SDL minter
    # minter = multisig.contract(SDL_MINTER_ADDRESS[CHAIN_IDS["MAINNET"]])
    # sdl_contract.transfer(minter.address, 5000000)

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
