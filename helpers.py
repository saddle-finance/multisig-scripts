from brownie.network.state import Chain

CHAIN_IDS = {
    "MAINNET": 1,
    "ROPSTEN": 3,
    "OPTIMISM": 10,
    "HARDHAT": 31337,
    "ARBITRUM": 42161,
    "EVMOS": 9001,
}

MULTISIG_ADDRESSES = {
    CHAIN_IDS["MAINNET"]: "0x3F8E527aF4e0c6e763e8f368AC679c44C45626aE",
    CHAIN_IDS["HARDHAT"]: "0x3F8E527aF4e0c6e763e8f368AC679c44C45626aE",
    CHAIN_IDS["ARBITRUM"]: "0x8e6e84DDab9d13A17806d34B097102605454D147",
    CHAIN_IDS["EVMOS"]: "0x25e73a609751E3289EAE21A6Dae431ff1E6fE261",
    CHAIN_IDS["OPTIMISM"]: "0x91804c72076aDd9fAB49b2c1e1A61A7503199599",
}

SDL_ADDRESSES = {
    CHAIN_IDS["MAINNET"]: "0xf1Dc500FdE233A4055e25e5BbF516372BC4F6871",
    CHAIN_IDS["OPTIMISM"]: "0xae31207ac34423c41576ff59bfb4e036150f9cf7",
}

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

L1_TO_L2_ERC20_ADDRESSES = {
    "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48": {  # USDC
        CHAIN_IDS["MAINNET"]: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        CHAIN_IDS["ARBITRUM"]: "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
        CHAIN_IDS["EVMOS"]: "0x51e44FfaD5C2B122C8b635671FCC8139dc636E82",
        CHAIN_IDS["OPTIMISM"]: "0x7f5c764cbc14f9669b88837ca1490cca17c31607",
    },
    "0xdac17f958d2ee523a2206206994597c13d831ec7": {  # USDT
        CHAIN_IDS["MAINNET"]: "0xdac17f958d2ee523a2206206994597c13d831ec7",
        CHAIN_IDS["ARBITRUM"]: "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9",
        CHAIN_IDS["EVMOS"]: "0x7FF4a56B32ee13D7D4D405887E0eA37d61Ed919e",
        CHAIN_IDS["OPTIMISM"]: "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58",
    },
    "0x853d955aCEf822Db058eb8505911ED77F175b99e": {  # FRAX
        CHAIN_IDS["MAINNET"]: "0x853d955aCEf822Db058eb8505911ED77F175b99e",
        CHAIN_IDS["ARBITRUM"]: "0x17FC002b466eEc40DaE837Fc4bE5c67993ddBd6F",
        CHAIN_IDS["EVMOS"]: "0xE03494D0033687543a80c9B1ca7D6237F2EA8BD8",
        CHAIN_IDS["OPTIMISM"]: "0x2E3D870790dC77A83DD1d18184Acc7439A53f475",
    },
    "0x6b175474e89094c44da98b954eedeac495271d0f": {  # DAI
        CHAIN_IDS["MAINNET"]: "0x6b175474e89094c44da98b954eedeac495271d0f",
        CHAIN_IDS["EVMOS"]: "0x63743ACF2c7cfee65A5E356A4C4A005b586fC7AA",
        CHAIN_IDS["OPTIMISM"]: "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1",
    },
    "0x5f98805A4E8be255a32880FDeC7F6728C6568bA0": {  # LUSD
        CHAIN_IDS["MAINNET"]: "0x5f98805A4E8be255a32880FDeC7F6728C6568bA0",
    },
    "0x57Ab1ec28D129707052df4dF418D58a2D46d5f51": {  # SUSD
        CHAIN_IDS["MAINNET"]: "0x57Ab1ec28D129707052df4dF418D58a2D46d5f51",
        CHAIN_IDS["OPTIMISM"]: "0x8c6f28f2F1A3C87F0f938b96d27520d9751ec8d9",
    },
    "0xd74f5255d557944cf7dd0e45ff521520002d5748": {  # USDS
        CHAIN_IDS["ARBITRUM"]: "0xd74f5255d557944cf7dd0e45ff521520002d5748",
    },
    "0xfe18be6b3bd88a2d2a7f928d00292e7a9963cfc6": {  # SBTC
        CHAIN_IDS["MAINNET"]: "0xfe18be6b3bd88a2d2a7f928d00292e7a9963cfc6",
    },
    "0x0100546F2cD4C9D97f798fFC9755E47865FF7Ee6": {  # ALETH
        CHAIN_IDS["MAINNET"]: "0x0100546F2cD4C9D97f798fFC9755E47865FF7Ee6",
    },
    "0xeb4c2781e4eba804ce9a9803c67d0893436bb27d": {  # RENBTC
        CHAIN_IDS["MAINNET"]: "0xeb4c2781e4eba804ce9a9803c67d0893436bb27d",
        CHAIN_IDS["EVMOS"]: "0xb1a8C961385B01C3aA782fba73E151465445D319",
    },
    "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599": {  # WBTC
        CHAIN_IDS["MAINNET"]: "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
        CHAIN_IDS["EVMOS"]: "0xF80699Dc594e00aE7bA200c7533a07C1604A106D",
    },
    "0xad3e3fc59dff318beceaab7d00eb4f68b1ecf195": {  # WCUSD
        CHAIN_IDS["MAINNET"]: "0xad3e3fc59dff318beceaab7d00eb4f68b1ecf195",
        CHAIN_IDS["EVMOS"]: "0xF80699Dc594e00aE7bA200c7533a07C1604A106D",
    },
    "0x18084fbA666a33d37592fA2633fD49a74DD93a88": {  # TBTC
        CHAIN_IDS["MAINNET"]: "0x18084fbA666a33d37592fA2633fD49a74DD93a88",
        CHAIN_IDS["EVMOS"]: "0x8d395AfFC1767141387ffF45aF88a074614E7Ccf",
        CHAIN_IDS["OPTIMISM"]: "0x220d6bEedeA6a6317DaE19d39cd62EB7bb0ae5e4",
    }
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
    CHAIN_IDS["ARBITRUM"]: "0x5288c571Fd7aD117beA99bF60FE0846C4E84F933",
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

MAINNET_POOL_ADDRESS_TO_POOL_NAME = {
    "0x13Cc34Aa8037f722405285AD2C82FE570bfa2bdc": "FRAXBP Pool",
    "0x8cAEa59f3Bf1F341f89c51607E4919841131e47a": "Frax 3Pool",
    "0xC69DDcd4DFeF25D8a793241834d4cc4b3668EAD6": "Saddle D4Pool",
    "0x2bFf1B48CC01284416E681B099a0CDDCA0231d72": "Saddle USX Pool",
    "0xdf3309771d2BF82cb2B6C56F9f5365C8bD97c4f2": "Saddle s/w/renBTCV2 Pool",
    "0xFB516cF3710fC6901F2266aAEB8834cF5e4E9558": "alUSDFRAX Metapool",
    "0x69baA0d7c2e864b74173922Ca069Ac79d3be1556": "sUSDFRAX Metapool",
    "0xC765Cd3d015626244AD63B5FB63a97c5634643b9": "FRAXUSDT Metapool",
    "0x4568727f50c7246ded8C39214Ed6FF3c157f080D": "Saddle sUSD Metapool",
    "0x3F1d224557afA4365155ea77cE4BC32D5Dae2174": "WCUSD Metapool",
    "0xaCb83E0633d6605c5001e2Ab59EF3C745547C8C7": "Saddle USD Pool",
    "0xa6018520EAACC06C30fF2e1B3ee2c7c22e64196a": "Saddle alETH Pool",
    "0xfa9ED0309Bf79Eb84C847819F0B3CB84F6d351Af": "Saddle TBTC Metapool",
}

ARBITRUM_POOL_ADDRESS_TO_POOL_NAME = {
    "0xfeEa4D1BacB0519E8f952460A70719944fe56Ee0": "Arb USDV2 Pool",
    "0x5dD186f8809147F96D3ffC4508F3C82694E58c9c": "Arb USDS Metapool",
    "0x401AFbc31ad2A3Bc0eD8960d63eFcDEA749b4849": "Arb FRAXBP Pool",
    "0xa5bD85ed9fA27ba23BfB702989e7218E44fd4706": "Arb FRAXBP/USDS Metapool",
    "0xf8504e92428d65E56e495684A38f679C1B1DC30b": "Arb FRAXBP/USDT Metapool",
}

OPTIMISM_POOL_ADDRESS_TO_POOL_NAME = {
    "0x5847f8177221268d279Cf377D0E01aB3FD993628": "Opt USD Pool",
    "0xF6C2e0aDc659007Ba7c48446F5A4e4E94dfe08b5": "Opt FRAXBP Pool",
    "0x250184dDDEC6d38E28ac12B481c9016867226E9D": "Opt FRAXBP/sUSD Metapool",
    "0xa9a84238098Dc3d1529228E6c74dBE7EbdF117a5": "Opt FRAXBP/USDT Metapool",
    "0xc55E8C79e5A6c3216D4023769559D06fa9A7732e": "Opt USD/FRAX Metapool",
}

EVMOS_POOL_ADDRESS_TO_POOL_NAME = {
    "0x1275203FB58Fc25bC6963B13C2a1ED1541563aF0": "Evmos 3Pool",
    "0x81272C5c573919eF0C719D6d63317a4629F161da": "Evmos 4Pool",
    "0x7003102c75587E8D29c56124060463Ef319407D0": "Evmos BTC Pool",
    "0x21d4365834B7c61447e142ef6bCf01136cBD01c6": "Evmos Frax3Pool",
    "0xdb5c5A6162115Ce9a188E7D773C4D011F421BbE5": "Evmos tBTC Metapool",
}

KAVA_POOL_ADDRESS_TO_POOL_NAME = {
    "0xA500b0e1360462eF777804BCAe6CE2BfB524dD2e": "Kava 3Pool",
}

VESTING_ABI = [
    {
        "inputs": [],
        "name": "release",
        "outputs":  [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "newBeneficiary", "type": "address"}
        ],
        "name": "changeBeneficiary",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]

GAUGE_ABI = [
    {
        "stateMutability": "view",
        "type": "function",
        "name": "name",
        "inputs": [],
        "outputs": [{"name": "", "type": "string"}],
    }
]

SWAP_ABI = [
    {
        "inputs": [],
        "name": "withdrawAdminFees",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "internalType": "uint8",
                "name": "index",
                "type": "uint8"
            }
        ],
        "name": "getToken",
        "outputs": [
            {
                "internalType": "contract IERC20",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "swapStorage",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "initialA",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "futureA",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "initialATime",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "futureATime",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "swapFee",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "adminFee",
                "type": "uint256"
            },
            {
                "internalType": "contract LPToken",
                "name": "lpToken",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {
                "name": "",
                "type": "uint8"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "name": "balance",
                "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
]

ARBITRUM_GATEWAY_ROUTER_ABI = [
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "_token",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "_to",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "_amount",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "_maxGas",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "_gasPriceBid",
                "type": "uint256"
            },
            {
                "internalType": "bytes",
                "name": "_data",
                "type": "bytes"
            }
        ],
        "name": "outboundTransfer",
        "outputs": [
            {
                "internalType": "bytes",
                "name": "",
                "type": "bytes"
            }
        ],
        "stateMutability": "payable",
        "type": "function"
    }
]

NOMAD_GATEWAY_ABI = [
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "_token",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "_amount",
                "type": "uint256"
            },
            {
                "internalType": "uint32",
                "name": "_destination",
                "type": "uint32"
            },
            {
                "internalType": "bytes32",
                "name": "_recipient",
                "type": "bytes32"
            },
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "name": "send",
        "outputs": [

        ],
        "stateMutability":"nonpayable",
        "type":"function"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "token",
                "type": "address"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "from",
                "type": "address"
            },
            {
                "indexed": True,
                "internalType": "uint32",
                "name": "toDomain",
                "type": "uint32"
            },
            {
                "indexed": False,
                "internalType": "bytes32",
                "name": "toId",
                "type": "bytes32"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "bool",
                "name": "fastLiquidityEnabled",
                "type": "bool"
            }
        ],
        "name": "Send",
        "type": "event"
    }
]


# 59,300 SDL/day in seconds
SIDECHAIN_TOTAL_EMISSION_RATE = 686342592592592592


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
