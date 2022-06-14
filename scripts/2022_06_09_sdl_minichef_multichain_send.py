from helpers import (
    CHAIN_IDS,
    MINICHEF_ADDRESSES,
    MULTISIG_ADDRESSES,
    SDL_ADDRESSES,
    ARBITRUM_L2_BRIDGE_ROUTER,
    EVMOS_NOMAD_ERC20_BRIDGE_ROUTER,
)
from ape_safe import ApeSafe
from brownie import accounts, network

from scripts.utils import confirm_posting_transaction


def main():
    """Add SimpleRewarder for T to minichef"""

    print(f"You are using the '{network.show_active()}' network")
    deployer = accounts.load("deployer")  # prompts for password
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
    poolLength = minichef.poolLength()
    for i in poolLength - 1:
        minichef.massUpdatePools(i)

    # Send needed SDL to minichef
    amountToSendMainnetMiniChef = 1e18
    sdl_contract.transfer(minichef.address, amountToSendMainnetMiniChef)

    # Send needed SDL to Arbitrum minichef
    amountToSendArbitrumMiniChef = 1e18
    gasLimitL2 = 1000000
    gasPriceL2 = 990000000
    maxSubmisstionCostL2 = 10000000000000
    arbitrumMinichefAddress = "0x2069043d7556B1207a505eb459D18d908DF29b55"
    sdlGatewayAddress = arbitrum_L1_Gateway.getGateway(sdl_contract.address)
    sdl_contract.approve(sdlGatewayAddress, amountToSendArbitrumMiniChef)
    arb_calldata = "0x000000000000000000000000000000000000000000000000000009184e72a00000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000000"
    arbitrum_L1_Gateway.outboundTransfer(
        sdl_contract.address,
        arbitrumMinichefAddress,
        amountToSendArbitrumMiniChef,
        gasLimitL2,
        gasPriceL2,
        # todo: find how to convert tuple to bytes, brownie.convert.to_bytes() only takes a singe arg
        arb_calldata,
        {"value": 1e15},
    )
    # should look like Arbitrum calldata: 0x000000000000000000000000000000000000000000000000000009184e72a00000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000000

    # Send needed SDL to EVMOS minichef
    amountToSendEvmosMinichef = 1e18
    NomadEVMOSMainnetDestinationCode = "1702260083"
    evmosMiniChefAddress = "0x0000000000000000000000000232e0b6df048c8CC4037c52Bc90cf943c9C8cC6"
    sdl_contract.approve(evmos_L1_Gateway.address, amountToSendEvmosMinichef)
    evmos_L1_Gateway.send(
        sdl_contract.address,
        amountToSendEvmosMinichef,
        NomadEVMOSMainnetDestinationCode,
        # .to_bytes convert by default to bytes32 then decode to str
        (brownie.convert.to_bytes(evmosMiniChefAddress)).decode(),
        False,
    )
    # should look like EVMOS calldata 0x0000000000000000000000000232e0b6df048c8CC4037c52Bc90cf943c9C8cC6

    # combine history into multisend txn
    safe_tx = multisig.multisend_from_receipts()

    # sign with private key
    safe_tx.sign(deployer.private_key)
    multisig.preview(safe_tx)

    confirm_posting_transaction(multisig, safe_tx)
