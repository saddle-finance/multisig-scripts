from brownie.network.state import Chain

CHAIN_IDS = {
    "MAINNET": 1,
    "ROPSTEN": 3,
    "OPTIMISM": 10,
    "HARDHAT": 31337,
    "ARBITRUM": 42161,
}

MULTISIG_ADDRESSES = {
    CHAIN_IDS["MAINNET"]: "0x3F8E527aF4e0c6e763e8f368AC679c44C45626aE",
    CHAIN_IDS["HARDHAT"]: "0x3F8E527aF4e0c6e763e8f368AC679c44C45626aE",
}

SDL_ADDRESSES = {
    CHAIN_IDS["MAINNET"]: "0xf1Dc500FdE233A4055e25e5BbF516372BC4F6871",
}

DELO_MULTISIG_ADDRESSES = {
    CHAIN_IDS["MAINNET"]: "0x03D319a9921474B9cdE1fff1DBaFba778f9eFEb0",
}

MINICHEF_ADDRESSES = {
    CHAIN_IDS["MAINNET"]: "0x691ef79e40d909C715BE5e9e93738B3fF7D58534",
    CHAIN_IDS["ARBITRUM"]: "0x2069043d7556B1207a505eb459D18d908DF29b55",
}

def assert_filename(file: str):
    """Asserts that a file follows naming convention and is being executed on the expected network"""
    filename = file.rsplit("/", 1)[1].split('.')[0]
    try:
        [_year, _month, _day, chain_id, _name] = filename.split('_')
    except ValueError:
        raise ValueError(f"Filename `{filename}` does not follow naming convention: `year_month_day_chainid_[file_name].py`")
    chain = Chain()
    assert chain.id == int(chain_id), f"Expected script to be run on network {chain_id}, but it was run on network {chain.id}"
