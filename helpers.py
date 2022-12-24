import json
from enum import IntEnum

from brownie.network.state import Chain

CHAIN_IDS = {
    "MAINNET": 1,
    "ROPSTEN": 3,
    "OPTIMISM": 10,
    "HARDHAT": 31337,
    "ARBITRUM": 42161,
    "EVMOS": 9001,
    "KAVA": 2222,
    "AURORA": 1313161554,
}

DEPLOYMENT_FOLDER_NAMES = {
    CHAIN_IDS["MAINNET"]: "mainnet",
    CHAIN_IDS["OPTIMISM"]: "optimism_mainnet",
    CHAIN_IDS["ARBITRUM"]: "arbitrum_mainnet",
    CHAIN_IDS["EVMOS"]: "evmos_mainnet",
    CHAIN_IDS["KAVA"]: "kava_mainnet",
    CHAIN_IDS["AURORA"]: "aurora_mainnet",
}

DEPLOYER_ADDRESS = "0x5bdb37d0ddea3a90f233c7b7f6b9394b6b2eef34"

ENG_EOA_ADDRESS = "0xA1DBb0A0388f105212C2a8d51fF37010f6A0C36A"

INCITE_MULTISIG_ADDRESS = "0x4ba5B41c4378966f08E3E4F7dd80840191D54C69"

# Addresses of 3/8 multisigs for administrational purposes
MULTISIG_ADDRESSES = {
    # https://app.safe.global/eth:0x3F8E527aF4e0c6e763e8f368AC679c44C45626aE/home
    CHAIN_IDS["MAINNET"]: "0x3F8E527aF4e0c6e763e8f368AC679c44C45626aE",
    CHAIN_IDS["HARDHAT"]: "0x3F8E527aF4e0c6e763e8f368AC679c44C45626aE",
    # https://app.safe.global/arb1:0x8e6e84DDab9d13A17806d34B097102605454D147/home
    CHAIN_IDS["ARBITRUM"]: "0x8e6e84DDab9d13A17806d34B097102605454D147",
    # https://safe.evmos.org/evmos:0x25e73a609751E3289EAE21A6Dae431ff1E6fE261/home
    CHAIN_IDS["EVMOS"]: "0x25e73a609751E3289EAE21A6Dae431ff1E6fE261",
    # https://app.safe.global/oeth:0x91804c72076aDd9fAB49b2c1e1A61A7503199599/home
    CHAIN_IDS["OPTIMISM"]: "0x91804c72076aDd9fAB49b2c1e1A61A7503199599",
    # https://app.safe.global/aurora:0x4e76a78Fd1Fb0811a0A9092275A32c04e346d000/home
    CHAIN_IDS["AURORA"]: "0x4e76a78Fd1Fb0811a0A9092275A32c04e346d000",
}

# Addresses of 2/3 multisigs for operational purposes
OPS_MULTISIG_ADDRESSES = {
    CHAIN_IDS["MAINNET"]: "0x4802CedbDF865382dbaED8D5e41a65C8AB840676",
    CHAIN_IDS["ARBITRUM"]: "0x6d9b26C25993358dCa0ABE9BF6A26Ddb18583200",
    CHAIN_IDS["OPTIMISM"]: "0x55F51A0DF2714F3CcA7acBcd9d3552A66FF5953B",
    CHAIN_IDS["EVMOS"]: "0x8A0BB6E3456008195219Bf71E1Bb6E37b909c153",
    CHAIN_IDS["AURORA"]: "0xeae45E6958C2808a4C8b8bC2f3E8E99d2c65b734",
}

MASTER_REGISTRY_ADDRESSES = {
    CHAIN_IDS["MAINNET"]: "0xc5ad17b98D7fe73B6dD3b0df5b3040457E68C045",
    CHAIN_IDS["ARBITRUM"]: "0xaB94A2c0D8F044AA439A5654f06b5797928396cF",
    CHAIN_IDS["OPTIMISM"]: "0x0E510c9b20a5D136E75f7FD2a5F344BD98f9d875",
    CHAIN_IDS["EVMOS"]: "0xBa684B8E05415726Ee1fFE197eaf1b82E4d44418",
}

POOL_REGISTRY_ADDRESSES = {
    CHAIN_IDS["MAINNET"]: "0xFb4DE84c4375d7c8577327153dE88f58F69EeC81",
}

OPS_MULTISIG_ADDRESSES = {
    CHAIN_IDS["MAINNET"]: "0x4802CedbDF865382dbaED8D5e41a65C8AB840676",
    CHAIN_IDS["ARBITRUM"]: "0x6d9b26C25993358dCa0ABE9BF6A26Ddb18583200",
    CHAIN_IDS["OPTIMISM"]: "0x55F51A0DF2714F3CcA7acBcd9d3552A66FF5953B",
    CHAIN_IDS["EVMOS"]: "0x8A0BB6E3456008195219Bf71E1Bb6E37b909c153",
}

MASTER_REGISTRY_ADDRESSES = {
    CHAIN_IDS["MAINNET"]: "0xc5ad17b98D7fe73B6dD3b0df5b3040457E68C045",
    CHAIN_IDS["ARBITRUM"]: "0xaB94A2c0D8F044AA439A5654f06b5797928396cF",
    CHAIN_IDS["OPTIMISM"]: "0x0E510c9b20a5D136E75f7FD2a5F344BD98f9d875",
    CHAIN_IDS["EVMOS"]: "0xBa684B8E05415726Ee1fFE197eaf1b82E4d44418",
}

SDL_ADDRESSES = {
    CHAIN_IDS["MAINNET"]: "0xf1Dc500FdE233A4055e25e5BbF516372BC4F6871",
    CHAIN_IDS["OPTIMISM"]: "0xAe31207aC34423C41576Ff59BFB4E036150f9cF7",
    CHAIN_IDS["ARBITRUM"]: "0x75C9bC761d88f70156DAf83aa010E84680baF131",
}

ALCX_ADDRESSES = {CHAIN_IDS["MAINNET"]
    : "0xdbdb4d16eda451d0503b854cf79d55697f90c8df"}

SDL_MINTER_ADDRESS = {
    CHAIN_IDS["MAINNET"]: "0x358fE82370a1B9aDaE2E3ad69D6cF9e503c96018",
}

SDL_DAO_COMMUNITY_VESTING_PROXY_ADDRESS = {
    CHAIN_IDS["MAINNET"]: "0x5DFbCeea7A5F6556356C7A66d2A43332755D68A5"
}

MINICHEF_ADDRESSES = {
    CHAIN_IDS["MAINNET"]: "0x691ef79e40d909C715BE5e9e93738B3fF7D58534",
    CHAIN_IDS["ARBITRUM"]: "0x2069043d7556B1207a505eb459D18d908DF29b55",
    CHAIN_IDS["EVMOS"]: "0x0232e0b6df048c8CC4037c52Bc90cf943c9C8cC6",
    CHAIN_IDS["OPTIMISM"]: "0x220d6bEedeA6a6317DaE19d39cd62EB7bb0ae5e4",
}

LP_MIGRATOR_ADDRESSES = {
    CHAIN_IDS["MAINNET"]: "0x46866D274E6D9015c5FDc098CE270803e11e3eF4",
}

DELO_MULTISIG_ADDRESSES = {
    CHAIN_IDS["MAINNET"]: "0x03D319a9921474B9cdE1fff1DBaFba778f9eFEb0",
}

DISPERSE_APP_ADDRESSES = {
    CHAIN_IDS["MAINNET"]: "0xD152f549545093347A162Dce210e7293f1452150",
}

ARBITRUM_L2_BRIDGE_ROUTER = {
    CHAIN_IDS["MAINNET"]: "0x72Ce9c846789fdB6fC1f34aC4AD25Dd9ef7031ef",
}

EVMOS_NOMAD_ERC20_BRIDGE_ROUTER = {
    CHAIN_IDS["MAINNET"]: "0x88A69B4E698A4B090DF6CF5Bd7B2D47325Ad30A3",
}

JUMP_RECEIVER_ADDRESS = {
    CHAIN_IDS["MAINNET"]: "0xCB8EFB0c065071E4110932858A84365A80C8feF0",
}

SMART_WALLET_CHECKER_ADDRESSES = {
    CHAIN_IDS["MAINNET"]: "0x4C6A2bE3D64048a0624568F91720a8f3884eBfd8",
}

VOTING_ESCROW_ADDRESSES = {
    CHAIN_IDS["MAINNET"]: "0xD2751CdBED54B87777E805be36670D7aeAe73bb2",
}

GAUGE_CONTROLLER_ADDRESS = {
    CHAIN_IDS["MAINNET"]: "0x99Cb6c36816dE2131eF2626bb5dEF7E5cc8b9B14",
}

MINTER = {
    CHAIN_IDS["MAINNET"]: "0x358fE82370a1B9aDaE2E3ad69D6cF9e503c96018",
}

# Multisig owners
OWNERS = [
    "0xD131F1BcDd547e067Af447dD3C36C99d6be9FdEB",  # Weston_Nelson
    "0xf872703F1C8f93fA186869Bac83BAC5A0c87C3c8",  # Scoopy Trooples
    "0x0AF91FA049A7e1894F480bFE5bBa20142C6c29a9",  # aurelius0x.eth
    "0xa83838221278f22ee5bAe3E523f34D42b066D67D",  # Damir Bandalo
    "0x0Cec743b8CE4Ef8802cAc0e5df18a180ed8402A7",  # yfi.milkyklim.eth
    "0x17e06ce6914E3969f7BD37D8b2a563890cA1c96e",  # Sam Kazemain
    "0x6F2A8Ee9452ba7d336b3fba03caC27f7818AeAD6",  # Mariano Conti
    "0x4E60bE84870FE6AE350B563A121042396Abe1eaF",  # DegenSpartan
]

OPTIMISM_STANDARD_BRIDGE = {
    CHAIN_IDS["MAINNET"]: "0x99C9fc46f92E8a1c0deC1b1747d010903E884bE1",
    CHAIN_IDS["OPTIMISM"]: "0x4200000000000000000000000000000000000010",
}

ARB_GATEWAY_ROUTER = {
    CHAIN_IDS["MAINNET"]: "0x72Ce9c846789fdB6fC1f34aC4AD25Dd9ef7031ef",
}

ARB_GENERIC_GATEWAY = {
    CHAIN_IDS["MAINNET"]: "0xa3A7B6F88361F48403514059F1F16C8E78d60EeC",
}

ARB_BRIDGE_INBOX = {
    CHAIN_IDS["MAINNET"]: "0x4Dbd4fc535Ac27206064B68FfCf827b0A60BAB3f",
}

HEDGEY_OTC = {
    CHAIN_IDS["MAINNET"]: "0xad337077480134028B7C68AF290E891ce28076Eb",
    CHAIN_IDS["ARBITRUM"]: "0xad337077480134028B7C68AF290E891ce28076Eb",
}

# 59,300 SDL/day in seconds
SIDECHAIN_TOTAL_EMISSION_RATE = 686342592592592592

GNOSIS_SAFE_BASE_URLS = {
    CHAIN_IDS["MAINNET"]: "https://safe-transaction-mainnet.safe.global",
    CHAIN_IDS["ARBITRUM"]: "https://safe-transaction-arbitrum.safe.global",
    CHAIN_IDS["OPTIMISM"]: "https://safe-transaction-optimism.safe.global",
    CHAIN_IDS["AURORA"]: "https://safe-transaction-aurora.safe.global",
    CHAIN_IDS["EVMOS"]: "https://transaction.safe.evmos.org",
}

# PoolType enum to match pool registry's field
PoolType = IntEnum('PoolType', ['BTC', 'ETH', 'USD', 'OTHERS'])


def assert_filename(file: str):
    """Asserts that a file follows naming convention and is being executed on the expected network"""
    filename = file.rsplit("/", 1)[1].split(".")[0]
    try:
        [_year, _month, _day, chain_id, _name] = filename.split("_")
    except ValueError:
        raise ValueError(
            f"Filename `{filename}` does not follow naming convention: `year_month_day_chainid_[file_name].py`"
        )
    chain = Chain()
    assert chain.id == int(
        chain_id
    ), f"Expected script to be run on network {chain_id}, but it was run on network {chain.id}"


def get_abi(file: str):
    """Attempts to load the ABI with given name from abis folder"""
    with open(f"abis/{file}.json") as f:
        abi = json.load(f)
        return abi


# Needed since different chains have different order of owner addrs
def intersection(lst1, lst2):

    temp = set(lst2)
    lst3 = [value for value in lst1 if value not in temp]
    return lst3


def get_deployment_details(chain_id: int, contract_name: str):
    """Returns the address and the ABI of the contract with the given name"""
    contract_json = json.load(open(
        f"saddle-contract/deployments/{DEPLOYMENT_FOLDER_NAMES[chain_id]}/{contract_name}.json"))
    return contract_json["address"], contract_json["abi"]


VESTING_ABI = get_abi("Vesting")
GAUGE_ABI = get_abi("Gauge")
NOMAD_GATEWAY_ABI = get_abi("NomadRouterImpl")
GNOSIS_SAFE_ABI = get_abi("GnosisSafeImpl")
POOL_REGISTRY_ABI = get_abi("PoolRegistry")
MINICHEF_ABI = get_abi("MiniChefV2")
SWAP_FLASH_LOAN_ABI = get_abi("SwapFlashLoan")
META_SWAP_ABI = get_abi("MetaSwap")
