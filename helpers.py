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
    # https://gnosis-safe.io/app/eth:0x3F8E527aF4e0c6e763e8f368AC679c44C45626aE/home
    CHAIN_IDS["HARDHAT"]: "0x3F8E527aF4e0c6e763e8f368AC679c44C45626aE",
    CHAIN_IDS["ARBITRUM"]: "0x8e6e84DDab9d13A17806d34B097102605454D147",
    # https://gnosis-safe.io/app/arb1:0x8e6e84DDab9d13A17806d34B097102605454D147/home
    CHAIN_IDS["EVMOS"]: "0x25e73a609751E3289EAE21A6Dae431ff1E6fE261",
    # https://safe.evmos.org/evmos:0x25e73a609751E3289EAE21A6Dae431ff1E6fE261/balances
    CHAIN_IDS["OPTIMISM"]: "0x91804c72076aDd9fAB49b2c1e1A61A7503199599",
    # https://gnosis-safe.io/app/oeth:0x91804c72076aDd9fAB49b2c1e1A61A7503199599/home
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

VESTING_ABI = [
    {
        "inputs": [],
        "name": "release",
        "outputs": [],
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

NOMAD_GATEWAY_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "_token", "type": "address"},
            {"internalType": "uint256", "name": "_amount", "type": "uint256"},
            {"internalType": "uint32", "name": "_destination", "type": "uint32"},
            {"internalType": "bytes32", "name": "_recipient", "type": "bytes32"},
            {"internalType": "bool", "name": "", "type": "bool"},
        ],
        "name": "send",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "token",
                "type": "address",
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "from",
                "type": "address",
            },
            {
                "indexed": True,
                "internalType": "uint32",
                "name": "toDomain",
                "type": "uint32",
            },
            {
                "indexed": False,
                "internalType": "bytes32",
                "name": "toId",
                "type": "bytes32",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256",
            },
            {
                "indexed": False,
                "internalType": "bool",
                "name": "fastLiquidityEnabled",
                "type": "bool",
            },
        ],
        "name": "Send",
        "type": "event",
    },
]


# 59,300 SDL/day in seconds
SIDECHAIN_TOTAL_EMISSION_RATE = 686342592592592592

GNOSIS_SAFE_ABI = [
    {"inputs": [], "stateMutability": "nonpayable", "type": "constructor"},
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "address",
                "name": "owner",
                "type": "address",
            }
        ],
        "name": "AddedOwner",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "bytes32",
                "name": "approvedHash",
                "type": "bytes32",
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "owner",
                "type": "address",
            },
        ],
        "name": "ApproveHash",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "address",
                "name": "handler",
                "type": "address",
            }
        ],
        "name": "ChangedFallbackHandler",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "address",
                "name": "guard",
                "type": "address",
            }
        ],
        "name": "ChangedGuard",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "threshold",
                "type": "uint256",
            }
        ],
        "name": "ChangedThreshold",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "address",
                "name": "module",
                "type": "address",
            }
        ],
        "name": "DisabledModule",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "address",
                "name": "module",
                "type": "address",
            }
        ],
        "name": "EnabledModule",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "bytes32",
                "name": "txHash",
                "type": "bytes32",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "payment",
                "type": "uint256",
            },
        ],
        "name": "ExecutionFailure",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "module",
                "type": "address",
            }
        ],
        "name": "ExecutionFromModuleFailure",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "module",
                "type": "address",
            }
        ],
        "name": "ExecutionFromModuleSuccess",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "bytes32",
                "name": "txHash",
                "type": "bytes32",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "payment",
                "type": "uint256",
            },
        ],
        "name": "ExecutionSuccess",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "address",
                "name": "owner",
                "type": "address",
            }
        ],
        "name": "RemovedOwner",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "sender",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "value",
                "type": "uint256",
            },
        ],
        "name": "SafeReceived",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "initiator",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "address[]",
                "name": "owners",
                "type": "address[]",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "threshold",
                "type": "uint256",
            },
            {
                "indexed": False,
                "internalType": "address",
                "name": "initializer",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "address",
                "name": "fallbackHandler",
                "type": "address",
            },
        ],
        "name": "SafeSetup",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "bytes32",
                "name": "msgHash",
                "type": "bytes32",
            }
        ],
        "name": "SignMsg",
        "type": "event",
    },
    {"stateMutability": "nonpayable", "type": "fallback"},
    {
        "inputs": [],
        "name": "VERSION",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "owner", "type": "address"},
            {"internalType": "uint256", "name": "_threshold", "type": "uint256"},
        ],
        "name": "addOwnerWithThreshold",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "hashToApprove", "type": "bytes32"}
        ],
        "name": "approveHash",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "bytes32", "name": "", "type": "bytes32"},
        ],
        "name": "approvedHashes",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "_threshold", "type": "uint256"}
        ],
        "name": "changeThreshold",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "dataHash", "type": "bytes32"},
            {"internalType": "bytes", "name": "data", "type": "bytes"},
            {"internalType": "bytes", "name": "signatures", "type": "bytes"},
            {
                "internalType": "uint256",
                "name": "requiredSignatures",
                "type": "uint256",
            },
        ],
        "name": "checkNSignatures",
        "outputs": [],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "dataHash", "type": "bytes32"},
            {"internalType": "bytes", "name": "data", "type": "bytes"},
            {"internalType": "bytes", "name": "signatures", "type": "bytes"},
        ],
        "name": "checkSignatures",
        "outputs": [],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "prevModule", "type": "address"},
            {"internalType": "address", "name": "module", "type": "address"},
        ],
        "name": "disableModule",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "domainSeparator",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "module", "type": "address"}],
        "name": "enableModule",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "value", "type": "uint256"},
            {"internalType": "bytes", "name": "data", "type": "bytes"},
            {
                "internalType": "enum Enum.Operation",
                "name": "operation",
                "type": "uint8",
            },
            {"internalType": "uint256", "name": "safeTxGas", "type": "uint256"},
            {"internalType": "uint256", "name": "baseGas", "type": "uint256"},
            {"internalType": "uint256", "name": "gasPrice", "type": "uint256"},
            {"internalType": "address", "name": "gasToken", "type": "address"},
            {"internalType": "address", "name": "refundReceiver", "type": "address"},
            {"internalType": "uint256", "name": "_nonce", "type": "uint256"},
        ],
        "name": "encodeTransactionData",
        "outputs": [{"internalType": "bytes", "name": "", "type": "bytes"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "value", "type": "uint256"},
            {"internalType": "bytes", "name": "data", "type": "bytes"},
            {
                "internalType": "enum Enum.Operation",
                "name": "operation",
                "type": "uint8",
            },
            {"internalType": "uint256", "name": "safeTxGas", "type": "uint256"},
            {"internalType": "uint256", "name": "baseGas", "type": "uint256"},
            {"internalType": "uint256", "name": "gasPrice", "type": "uint256"},
            {"internalType": "address", "name": "gasToken", "type": "address"},
            {
                "internalType": "address payable",
                "name": "refundReceiver",
                "type": "address",
            },
            {"internalType": "bytes", "name": "signatures", "type": "bytes"},
        ],
        "name": "execTransaction",
        "outputs": [{"internalType": "bool", "name": "success", "type": "bool"}],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "value", "type": "uint256"},
            {"internalType": "bytes", "name": "data", "type": "bytes"},
            {
                "internalType": "enum Enum.Operation",
                "name": "operation",
                "type": "uint8",
            },
        ],
        "name": "execTransactionFromModule",
        "outputs": [{"internalType": "bool", "name": "success", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "value", "type": "uint256"},
            {"internalType": "bytes", "name": "data", "type": "bytes"},
            {
                "internalType": "enum Enum.Operation",
                "name": "operation",
                "type": "uint8",
            },
        ],
        "name": "execTransactionFromModuleReturnData",
        "outputs": [
            {"internalType": "bool", "name": "success", "type": "bool"},
            {"internalType": "bytes", "name": "returnData", "type": "bytes"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "getChainId",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "start", "type": "address"},
            {"internalType": "uint256", "name": "pageSize", "type": "uint256"},
        ],
        "name": "getModulesPaginated",
        "outputs": [
            {"internalType": "address[]", "name": "array", "type": "address[]"},
            {"internalType": "address", "name": "next", "type": "address"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "getOwners",
        "outputs": [{"internalType": "address[]", "name": "", "type": "address[]"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "offset", "type": "uint256"},
            {"internalType": "uint256", "name": "length", "type": "uint256"},
        ],
        "name": "getStorageAt",
        "outputs": [{"internalType": "bytes", "name": "", "type": "bytes"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "getThreshold",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "value", "type": "uint256"},
            {"internalType": "bytes", "name": "data", "type": "bytes"},
            {
                "internalType": "enum Enum.Operation",
                "name": "operation",
                "type": "uint8",
            },
            {"internalType": "uint256", "name": "safeTxGas", "type": "uint256"},
            {"internalType": "uint256", "name": "baseGas", "type": "uint256"},
            {"internalType": "uint256", "name": "gasPrice", "type": "uint256"},
            {"internalType": "address", "name": "gasToken", "type": "address"},
            {"internalType": "address", "name": "refundReceiver", "type": "address"},
            {"internalType": "uint256", "name": "_nonce", "type": "uint256"},
        ],
        "name": "getTransactionHash",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "module", "type": "address"}],
        "name": "isModuleEnabled",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "owner", "type": "address"}],
        "name": "isOwner",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "nonce",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "prevOwner", "type": "address"},
            {"internalType": "address", "name": "owner", "type": "address"},
            {"internalType": "uint256", "name": "_threshold", "type": "uint256"},
        ],
        "name": "removeOwner",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "value", "type": "uint256"},
            {"internalType": "bytes", "name": "data", "type": "bytes"},
            {
                "internalType": "enum Enum.Operation",
                "name": "operation",
                "type": "uint8",
            },
        ],
        "name": "requiredTxGas",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "handler", "type": "address"}],
        "name": "setFallbackHandler",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "guard", "type": "address"}],
        "name": "setGuard",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address[]", "name": "_owners", "type": "address[]"},
            {"internalType": "uint256", "name": "_threshold", "type": "uint256"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "bytes", "name": "data", "type": "bytes"},
            {"internalType": "address", "name": "fallbackHandler", "type": "address"},
            {"internalType": "address", "name": "paymentToken", "type": "address"},
            {"internalType": "uint256", "name": "payment", "type": "uint256"},
            {
                "internalType": "address payable",
                "name": "paymentReceiver",
                "type": "address",
            },
        ],
        "name": "setup",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "name": "signedMessages",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "targetContract", "type": "address"},
            {"internalType": "bytes", "name": "calldataPayload", "type": "bytes"},
        ],
        "name": "simulateAndRevert",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "prevOwner", "type": "address"},
            {"internalType": "address", "name": "oldOwner", "type": "address"},
            {"internalType": "address", "name": "newOwner", "type": "address"},
        ],
        "name": "swapOwner",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {"stateMutability": "payable", "type": "receive"},
]

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


# Needed since different chains have different order of owner addrs
def intersection(lst1, lst2):

    temp = set(lst2)
    lst3 = [value for value in lst1 if value not in temp]
    return lst3
