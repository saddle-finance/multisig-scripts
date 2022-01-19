from brownie.network.state import Chain
from enum import Enum

def assert_filename(file: str):
    """Asserts that a file follows naming convention and is being executed on the expected network"""
    filename = file.rsplit("/", 1)[1].split('.')[0]
    try:
        [_year, _month, _day, chain_id, _name] = filename.split('_')
    except ValueError:
        raise ValueError(f"Filename `{filename}` does not follow naming convention: `year_month_day_chainid_[file_name].py`")
    chain = Chain()
    assert chain.id == int(chain_id), f"Expected script to be run on network {chain_id}, but it was run on network {chain.id}"

class ChainId(Enum):
    """Enum of supported chain IDs"""
    MAINNET = 1
    ROPSTEN = 3
    OPTIMISM = 10
    HARDHAT = 31337
    ARBITRUM = 42161
    
# class MultisigAddresses(Enum):
#     """Enum of supported multisig addresses"""
#     ChainId.MAINNET = "0x3F8E527aF4e0c6e763e8f368AC679c44C45626aE"

MultisigAddresses = {
    ChainId.MAINNET: "0x3F8E527aF4e0c6e763e8f368AC679c44C45626aE",
}