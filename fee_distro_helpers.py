from helpers import (
    CHAIN_IDS,
    get_abi
)
from collections import OrderedDict

MAX_POOL_LENGTH = 32

SUSHI_SDL_SLP_ADDRESSES = {
    CHAIN_IDS["MAINNET"]: "0x0C6F06b32E6Ae0C110861b8607e67dA594781961"
}

UNIV3_ROUTER_ADDRESSES = {
    CHAIN_IDS["MAINNET"]: "0xE592427A0AEce92De3Edee1F18E0157C05861564"
}

UNIV3_QUOTER_ADDRESSES = {
    CHAIN_IDS["MAINNET"]: "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6"
}

# chain_id -> token -> address
token_addresses = {
    CHAIN_IDS["MAINNET"]: {
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "FEI": "0x956F47F50A910163D8BF957Cf5846D573E7f87CA",
        "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        "LUSD": "0x5f98805A4E8be255a32880FDeC7F6728C6568bA0",
        "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "FRAX": "0x853d955aCEf822Db058eb8505911ED77F175b99e",
        "SUSD": "0x57Ab1ec28D129707052df4dF418D58a2D46d5f51",
        "ALUSD": "0xBC6DA0FE9aD5f3b0d58160288917AA56653660E9",
        "WCUSD": "0xad3E3Fc59dff318BecEaAb7D00EB4F68b1EcF195",
        "USX": "0x0a5E677a6A24b2F1A2Bf4F3bFfC443231d2fDEc8",
        "RENBTC": "0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D",
        "SBTC": "0xfE18be6b3Bd88A2D2A7f928d00292E7a9963CfC6",
        "TBTC": "0x18084fbA666a33d37592fA2633fD49a74DD93a88",
        "ALETH": "0x0100546F2cD4C9D97f798fFC9755E47865FF7Ee6",
        "SETH": "0x5e74C9036fb86BD7eCdcb084a0673EFc32eA31cb"
    },
    CHAIN_IDS["ARBITRUM"]: {
        "USDC": "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
        "USDT": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
        "FRAX": "0x17FC002b466eEc40DaE837Fc4bE5c67993ddBd6F",
        "MIM": "0xFEa7a6a0B346362BF88A9e4A88416B77a57D6c2A",
        "nUSD": "0x2913E812Cf0dcCA30FB28E6Cac3d2DCFF4497688",
        "USDs": "0xD74f5255D557944cf7Dd0E45FF521520002D5748"
    },
    CHAIN_IDS["OPTIMISM"]: {
        "USDC": "0x7F5c764cBc14f9669B88837ca1490cCa17c31607",
        "USDT": "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58",
        "FRAX": "0x2E3D870790dC77A83DD1d18184Acc7439A53f475",
        "SUSD": "0x8c6f28f2F1A3C87F0f938b96d27520d9751ec8d9",
        "USX": "0xbfD291DA8A403DAAF7e5E9DC1ec0aCEaCd4848B9"

    },
    CHAIN_IDS["EVMOS"]: {
        "USDC": "0xe46910336479F254723710D57e7b683F3315b22B",  # CEUSDC
        "USDT": "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58",  # CEUSDT
    },
    CHAIN_IDS["KAVA"]: {
        "USDC": "0xfa9343c3897324496a05fc75abed6bac29f8a40f",
        "USDT": "0xB44a9B6905aF7c801311e8F4E76932ee959c663C",
    },

}

univ3_fee_tier_dicts = {
    CHAIN_IDS["MAINNET"]: {
        token_addresses[CHAIN_IDS["MAINNET"]]["WETH"]: int(3000),
        token_addresses[CHAIN_IDS["MAINNET"]]["WBTC"]: int(3000),
        token_addresses[CHAIN_IDS["MAINNET"]]["FEI"]: int(500),
        token_addresses[CHAIN_IDS["MAINNET"]]["DAI"]: int(500),
        # token_addresses[CHAIN_IDS["MAINNET"]]["LUSD"]: int(500)
    }
}

# defines which tokens to swap to which target tokens using which swap on saddle
# chain_id -> token_from -> (token_to, swap/metaswap)
token_to_swap_dicts_saddle = {
    CHAIN_IDS["MAINNET"]: {
        # USDT : USDv2 Pool
        token_addresses[CHAIN_IDS["MAINNET"]]["USDT"]: (token_addresses[CHAIN_IDS["MAINNET"]]["USDC"], "0xaCb83E0633d6605c5001e2Ab59EF3C745547C8C7"),
        # FRAX : FraxBP Pool
        token_addresses[CHAIN_IDS["MAINNET"]]["FRAX"]: (token_addresses[CHAIN_IDS["MAINNET"]]["USDC"], "0x13Cc34Aa8037f722405285AD2C82FE570bfa2bdc"),
        # sUSD : FraxBP/sUSD Metapool
        token_addresses[CHAIN_IDS["MAINNET"]]["SUSD"]: (token_addresses[CHAIN_IDS["MAINNET"]]["USDC"], "0x69baA0d7c2e864b74173922Ca069Ac79d3be1556"),
        # DAI : USDv2 Pool
        token_addresses[CHAIN_IDS["MAINNET"]]["DAI"]: (token_addresses[CHAIN_IDS["MAINNET"]]["USDC"], "0xaCb83E0633d6605c5001e2Ab59EF3C745547C8C7"),
        # alUSD : FraxBP/alUSD Metapool
        token_addresses[CHAIN_IDS["MAINNET"]]["ALUSD"]: (token_addresses[CHAIN_IDS["MAINNET"]]["USDC"], "0xFB516cF3710fC6901F2266aAEB8834cF5e4E9558"),
        # WCUSD : WCUSD/USDv2 Metapool
        token_addresses[CHAIN_IDS["MAINNET"]]["WCUSD"]: (token_addresses[CHAIN_IDS["MAINNET"]]["USDC"], "0x3F1d224557afA4365155ea77cE4BC32D5Dae2174"),
        # USX : USDC-USX Pool
        token_addresses[CHAIN_IDS["MAINNET"]]["USX"]: (token_addresses[CHAIN_IDS["MAINNET"]]["USDC"], "0x2bFf1B48CC01284416E681B099a0CDDCA0231d72"),
        # renBTC : wBTC
        # token_addresses[CHAIN_IDS["MAINNET"]]["RENBTC"]: (token_addresses[CHAIN_IDS["MAINNET"]]["WBTC"], "0xdf3309771d2BF82cb2B6C56F9f5365C8bD97c4f2"),
        # sBTC : wBTC
        # token_addresses[CHAIN_IDS["MAINNET"]]["SBTC"]: (token_addresses[CHAIN_IDS["MAINNET"]]["WBTC"], "0xdf3309771d2BF82cb2B6C56F9f5365C8bD97c4f2"),
        # tBTC : wBTC
        # token_addresses[CHAIN_IDS["MAINNET"]]["TBTC"]: (token_addresses[CHAIN_IDS["MAINNET"]]["WBTC"], "0xfa9ED0309Bf79Eb84C847819F0B3CB84F6d351Af"),
        # alETH : WETH
        token_addresses[CHAIN_IDS["MAINNET"]]["ALETH"]: (token_addresses[CHAIN_IDS["MAINNET"]]["WETH"], "0xa6018520EAACC06C30fF2e1B3ee2c7c22e64196a"),
        # sETH : WETH
        token_addresses[CHAIN_IDS["MAINNET"]]["SETH"]: (token_addresses[CHAIN_IDS["MAINNET"]]["WETH"], "0xa6018520EAACC06C30fF2e1B3ee2c7c22e64196a"),
    },
    CHAIN_IDS["ARBITRUM"]: {
        # USDC : Arb USD Pool
        # token_addresses[CHAIN_IDS["ARBITRUM"]]["USDC"]: (token_addresses[CHAIN_IDS["ARBITRUM"]]["USDC"], "0xBea9F78090bDB9e662d8CB301A00ad09A5b756e9"),
        # USDT : Arb USDV2 Pool
        token_addresses[CHAIN_IDS["ARBITRUM"]]["USDT"]: (token_addresses[CHAIN_IDS["ARBITRUM"]]["USDC"], "0xfeEa4D1BacB0519E8f952460A70719944fe56Ee0"),
        # FRAX : Arb FRAXBP Pool
        token_addresses[CHAIN_IDS["ARBITRUM"]]["FRAX"]: (token_addresses[CHAIN_IDS["ARBITRUM"]]["USDC"], "0x401AFbc31ad2A3Bc0eD8960d63eFcDEA749b4849"),
        # MIM : Arb USD Pool
        token_addresses[CHAIN_IDS["ARBITRUM"]]["MIM"]: (token_addresses[CHAIN_IDS["ARBITRUM"]]["USDC"], "0xBea9F78090bDB9e662d8CB301A00ad09A5b756e9"),
        # nUSD : Arb USD Pool
        token_addresses[CHAIN_IDS["ARBITRUM"]]["nUSD"]: (token_addresses[CHAIN_IDS["ARBITRUM"]]["USDC"], "0xBea9F78090bDB9e662d8CB301A00ad09A5b756e9"),
        # USDs : Arb FRAXBP/USDS Metapool
        token_addresses[CHAIN_IDS["ARBITRUM"]]["USDs"]: (token_addresses[CHAIN_IDS["ARBITRUM"]]["USDC"], "0xa5bD85ed9fA27ba23BfB702989e7218E44fd4706"),
    },
    CHAIN_IDS["OPTIMISM"]: {
        # USDC : Opt FRAXBP Pool
        # token_addresses[CHAIN_IDS["OPTIMISM"]]["USDC"]: (token_addresses[CHAIN_IDS["OPTIMISM"]]["USDC"], "0xF6C2e0aDc659007Ba7c48446F5A4e4E94dfe08b5"),
        # USDT : Opt FRAXBP/USDT Metapool
        token_addresses[CHAIN_IDS["OPTIMISM"]]["USDT"]: (token_addresses[CHAIN_IDS["OPTIMISM"]]["USDC"], "0xa9a84238098Dc3d1529228E6c74dBE7EbdF117a5"),
        # FRAX : Opt FRAXBP Pool
        token_addresses[CHAIN_IDS["OPTIMISM"]]["FRAX"]: (token_addresses[CHAIN_IDS["OPTIMISM"]]["USDC"], "0xF6C2e0aDc659007Ba7c48446F5A4e4E94dfe08b5"),
        # sUSD : Opt FRAXBP/sUSD Metapool
        token_addresses[CHAIN_IDS["OPTIMISM"]]["SUSD"]: (token_addresses[CHAIN_IDS["OPTIMISM"]]["USDC"], "0x250184dDDEC6d38E28ac12B481c9016867226E9D"),
        # USX: Opt FRAXBP/USX Metapool
        token_addresses[CHAIN_IDS["OPTIMISM"]]["USX"]: (token_addresses[CHAIN_IDS["OPTIMISM"]]["USDC"], "0xe184F7E575a5Beb8f2409E8e2218Cd770ddDa2A6"),
    },
    CHAIN_IDS["EVMOS"]: {
        # ceUSDC : Evmos USDT Pool
        # token_addresses[CHAIN_IDS["EVMOS"]]["USDT"]: (token_addresses[CHAIN_IDS["EVMOS"]]["USDC"], "0x79cb59c7B6bd0e5ef99189efD9065500eAbc1a4b"),
        # ceUSDT : Evmos USDT Pool
        # token_addresses[CHAIN_IDS["EVMOS"]]["USDT"]: (token_addresses[CHAIN_IDS["EVMOS"]]["USDC"], "0x79cb59c7B6bd0e5ef99189efD9065500eAbc1a4b"),
    },
    CHAIN_IDS["KAVA"]: {
        # USDC : USDT Pool
        token_addresses[CHAIN_IDS["KAVA"]]["USDC"]: (token_addresses[CHAIN_IDS["KAVA"]]["USDC"], "0x5847f8177221268d279Cf377D0E01aB3FD993628"),
        # USDT : USDT Pool
        token_addresses[CHAIN_IDS["KAVA"]]["USDT"]: (token_addresses[CHAIN_IDS["KAVA"]]["USDC"], "0x5847f8177221268d279Cf377D0E01aB3FD993628"),
    },
}

# chain_id -> swap -> metaswapDeposit dict
swap_to_deposit_dicts_saddle = {
    CHAIN_IDS["MAINNET"]: OrderedDict([
        # FraxBP Pool
        ("0x13Cc34Aa8037f722405285AD2C82FE570bfa2bdc", ""),
        # Frax 3Pool Pool
        ("0x8cAEa59f3Bf1F341f89c51607E4919841131e47a", ""),
        # Saddle D4Pool Pool
        ("0xC69DDcd4DFeF25D8a793241834d4cc4b3668EAD6", ""),
        # Saddle USX Pool
        ("0x2bFf1B48CC01284416E681B099a0CDDCA0231d72", ""),
        # Saddle s/w/renBTCV2 Pool
        ("0xdf3309771d2BF82cb2B6C56F9f5365C8bD97c4f2", ""),
        # FraxBP/alUSD Metapool
        ("0xFB516cF3710fC6901F2266aAEB8834cF5e4E9558",
         "0xe9154791883Df07e1328B636BCedfcCb80fefa38"),
        # FraxBP/sUSD Metapool
        ("0x69baA0d7c2e864b74173922Ca069Ac79d3be1556",
         "0x7D6c760cBde5a9Ad47510A86b9DCc58F9473CdD8"),
        # FraxBP/USDT Metapool
        ("0xC765Cd3d015626244AD63B5FB63a97c5634643b9",
         "0xAbf69CDE7B3725c12B8703005342EB5DD8a95D61"),
        # FraxBP/USX Metapool
        ("0x1dcB69a2b9148C641a43F731fCee123e2be30bAb",
         "0x4F0E41a37cE2ff1fA654cC93Eb03F9d16E65fD11"),
        # Saddle sUSD Metapool
        ("0x4568727f50c7246ded8C39214Ed6FF3c157f080D",
         "0xB98fd1f66884cD5786b37cDE040B9f0cf763866f"),
        # WCUSD Metapool
        ("0x3F1d224557afA4365155ea77cE4BC32D5Dae2174",
         "0x9898D87368DE0Bf1f10bbea8dE46c00cC3a2F9F1"),
        # Saddle USD Pool
        ("0xaCb83E0633d6605c5001e2Ab59EF3C745547C8C7", ""),
        # Saddle alETH Pool
        ("0xa6018520EAACC06C30fF2e1B3ee2c7c22e64196a", ""),
        # Saddle TBTC Metapool
        ("0xfa9ED0309Bf79Eb84C847819F0B3CB84F6d351Af",
         "0x4946DE721ce70D4B7aa226aA0Fe869C935769388")
    ]),
    CHAIN_IDS["ARBITRUM"]: OrderedDict([
        # Arb USD Pool
        ("0xBea9F78090bDB9e662d8CB301A00ad09A5b756e9", ""),
        # Arb USDV2 Pool
        ("0xfeEa4D1BacB0519E8f952460A70719944fe56Ee0", ""),
        # Arb USDS Metapool
        ("0x5dD186f8809147F96D3ffC4508F3C82694E58c9c",
         "0xDCA5b16A96f984ffb2A3022cfF339eb049126101"),
        # Arb FRAXBP Pool
        ("0x401AFbc31ad2A3Bc0eD8960d63eFcDEA749b4849", ""),
        # Arb FRAXBP/USDS Metapool
        ("0xa5bD85ed9fA27ba23BfB702989e7218E44fd4706",
         "0x1D434f50acf16BA013BE3536e9A3CDb5D7d4e694"),
        # Arb FRAXBP/USDT Metapool
        ("0xf8504e92428d65E56e495684A38f679C1B1DC30b",
         "0xc8DFCFC329E19fDAF43a338aD6038dBA02a5079B"),
    ]),
    CHAIN_IDS["OPTIMISM"]: OrderedDict([
        # Opt USD Pool
        ("0x5847f8177221268d279Cf377D0E01aB3FD993628", ""),
        # Opt FRAXBP Pool
        ("0xF6C2e0aDc659007Ba7c48446F5A4e4E94dfe08b5", ""),
        # Opt FRAXBP/sUSD Metapool
        ("0x250184dDDEC6d38E28ac12B481c9016867226E9D",
         "0xdf815Ea6b066Ac9f3107d8863a6c19aA2a5d24d3"),
        # Opt FRAXBP/USDT Metapool
        ("0xa9a84238098Dc3d1529228E6c74dBE7EbdF117a5",
         "0x3F1d224557afA4365155ea77cE4BC32D5Dae2174"),
        # Opt USD/FRAX Metapool
        ("0xc55E8C79e5A6c3216D4023769559D06fa9A7732e",
         "0x88Cc4aA0dd6Cf126b00C012dDa9f6F4fd9388b17"),
        # Opt FRAXBP/USX Metapool
        ("0xe184F7E575a5Beb8f2409E8e2218Cd770ddDa2A6",
         "0xB10Ac31a6e613c6fcB5522c19f4bdBCFFa94f89d")
    ]),
    CHAIN_IDS["EVMOS"]: OrderedDict([
        # Evmos USDT Pool (paused)
        # "0x79cb59c7B6bd0e5ef99189efD9065500eAbc1a4b": "",
        # Evmos 4Pool (paused)
        # "0x81272C5c573919eF0C719D6d63317a4629F161da": "",
        # Evmos Frax3Pool (paused)
        # "0x21d4365834B7c61447e142ef6bCf01136cBD01c6": "",
        # Evmos 3Pool (paused)
        # "0x1275203FB58Fc25bC6963B13C2a1ED1541563aF0": "",
        # Evmos BTC Pool (paused)
        # "0x7003102c75587E8D29c56124060463Ef319407D0": "",
        # Evmos tBTC Metapool (paused)
        # "0xdb5c5A6162115Ce9a188E7D773C4D011F421BbE5": "0xFdA5D2ad8b6d3884AbB799DA66f57175E8706941",
    ]),
    CHAIN_IDS["KAVA"]: OrderedDict([
        # Kava USDT Pool
        ("0x5847f8177221268d279Cf377D0E01aB3FD993628", ""),
        # Kava 3Pool (paused)
        # "0xA500b0e1360462eF777804BCAe6CE2BfB524dD2e": "",
    ]),
}

# defines, in order, which tokens to swap to which target tokens using which swap on curve
# chain_id -> token_from -> (token_to, swap/metaswap)
token_to_swap_dicts_curve = {
    CHAIN_IDS["MAINNET"]: OrderedDict([
        # renBTC : WBTC, Curve sBTC V1 pool
        (token_addresses[CHAIN_IDS["MAINNET"]]["RENBTC"], (token_addresses[CHAIN_IDS["MAINNET"]]
         ["WBTC"], "0x7fC77b5c7614E1533320Ea6DDc2Eb61fa00A9714")),
        # sBTC : WBTC, Curve sBTC V1 pool
        (token_addresses[CHAIN_IDS["MAINNET"]]["SBTC"], (token_addresses[CHAIN_IDS["MAINNET"]]
         ["WBTC"], "0x7fC77b5c7614E1533320Ea6DDc2Eb61fa00A9714")),
        # tBTC : wBTC Curve metapool
        (token_addresses[CHAIN_IDS["MAINNET"]]["TBTC"], (token_addresses[CHAIN_IDS["MAINNET"]]
         ["WBTC"], "0xfa65aa60a9D45623c57D383fb4cf8Fb8b854cC4D")),
        # LUSD : USDC Curve LUSD/3pool metapool
        (token_addresses[CHAIN_IDS["MAINNET"]]["LUSD"], (token_addresses[CHAIN_IDS["MAINNET"]]
         ["USDC"], "0xEd279fDD11cA84bEef15AF5D39BB4d4bEE23F0cA")),
        # FEI : USDC Curve LUSD/3pool metapool
        (token_addresses[CHAIN_IDS["MAINNET"]]["FEI"], (token_addresses[CHAIN_IDS["MAINNET"]]
         ["USDC"], "0x06cb22615BA53E60D67Bf6C341a0fD5E718E1655")),
        # wBTC : USDT Curve TriCrypto2 pool
        (token_addresses[CHAIN_IDS["MAINNET"]]["WBTC"], (token_addresses[CHAIN_IDS["MAINNET"]]
         ["USDT"], "0xD51a44d3FaE010294C616388b506AcdA1bfAAE46")),
        # WETH : USDC Curve TriCrypto2 pool
        (token_addresses[CHAIN_IDS["MAINNET"]]["WETH"], (token_addresses[CHAIN_IDS["MAINNET"]]
         ["USDT"], "0xD51a44d3FaE010294C616388b506AcdA1bfAAE46")),
        # USDT: USDC Curve 3pool pool
        (token_addresses[CHAIN_IDS["MAINNET"]]["USDT"], (token_addresses[CHAIN_IDS["MAINNET"]]
         ["USDC"], "0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7")),
    ])
}
# used to indicate whether a swap is a metaswap or not
# note: we don't actually use deposit contracts with curve, but it keeps the code consistent with saddle swaps
swap_to_deposit_dicts_curve = {
    CHAIN_IDS["MAINNET"]: OrderedDict([
        # sBTC : WBTC, Curve sBTC V1 pool
        ("0x7fC77b5c7614E1533320Ea6DDc2Eb61fa00A9714", ""),
        # TriCrypto2 pool
        ("0xD51a44d3FaE010294C616388b506AcdA1bfAAE46", ""),
        # Curve 3pool pool
        ("0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7", ""),
        # Curve tBTC metapool, note: deposit contract is for tBTVv2 (not tBTCv1), but doesnt matter
        ("0xfa65aa60a9D45623c57D383fb4cf8Fb8b854cC4D",
         "0xaa82ca713D94bBA7A89CEAB55314F9EfFEdDc78c"),
        # Curve LUSD metapool, @dev: not actually a deposit contract, but doesnt matter (non-empty indicates meta pool)
        ("0xEd279fDD11cA84bEef15AF5D39BB4d4bEE23F0cA",
         "0xEd279fDD11cA84bEef15AF5D39BB4d4bEE23F0cA"),
        # Curve FEI metapool, @dev: not actually a deposit contract, but doesnt matter (non-empty indicates meta pool)
        ("0x06cb22615BA53E60D67Bf6C341a0fD5E718E1655",
         "0x06cb22615BA53E60D67Bf6C341a0fD5E718E1655")
    ]),
}

# some older curve metaswaps don't expose base_pool, so we need to hardcode them
# metaswap -> (base_pool, coins_array_argument_type)
metaswap_to_base_swap_dicts_curve = {
    CHAIN_IDS["MAINNET"]: OrderedDict([
        # tBTC V1 pool : sBTC base pool
        ("0xfa65aa60a9D45623c57D383fb4cf8Fb8b854cC4D",
         "0x7fC77b5c7614E1533320Ea6DDc2Eb61fa00A9714"),
        # LUSD metapool: 3pool pool
        ("0xEd279fDD11cA84bEef15AF5D39BB4d4bEE23F0cA",
         "0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7"),
        # FEI meta pool: 3pool pool
        ("0x06cb22615BA53E60D67Bf6C341a0fD5E718E1655",
         "0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7")
    ])
}

# curve_base_pool -> argument_types
base_pool_abi_types_curve = {
    CHAIN_IDS["MAINNET"]: OrderedDict([
        # sBTC base pool
        ("0x7fC77b5c7614E1533320Ea6DDc2Eb61fa00A9714", "int128"),
        # 3pool
        ("0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7", "mixed"),
        # Trycrypto2 pool
        ("0xD51a44d3FaE010294C616388b506AcdA1bfAAE46", "uint256")
    ])
}


# token_from -> token_to dict, for using UniswapV3
token_to_token_univ3_dicts = {
    CHAIN_IDS["MAINNET"]: {
        # LUSD : USDC
        token_addresses[CHAIN_IDS["MAINNET"]]["LUSD"]: token_addresses[CHAIN_IDS["MAINNET"]]["USDC"],
        # WBTC : USDC
        token_addresses[CHAIN_IDS["MAINNET"]]["WBTC"]: token_addresses[CHAIN_IDS["MAINNET"]]["USDC"],
        # WBTC : USDC
        token_addresses[CHAIN_IDS["MAINNET"]]["SBTC"]: token_addresses[CHAIN_IDS["MAINNET"]]["USDC"],
        # WBTC : USDC
        token_addresses[CHAIN_IDS["MAINNET"]]["RENBTC"]: token_addresses[CHAIN_IDS["MAINNET"]]["USDC"],
        # WETH : USDC
        token_addresses[CHAIN_IDS["MAINNET"]]["WETH"]: token_addresses[CHAIN_IDS["MAINNET"]]["USDC"],
        # FEI: USDC
        token_addresses[CHAIN_IDS["MAINNET"]]["FEI"]: token_addresses[CHAIN_IDS["MAINNET"]]["USDC"],
    }
}

# chain_id -> token_from -> route_type_tuple
univ3_route_type_tuples = {
    CHAIN_IDS["MAINNET"]: {
        # FEI to USDC (FEI -> DAI -> USDC)
        token_addresses[CHAIN_IDS["MAINNET"]]["FEI"]: ['address', 'uint24', 'address', 'uint24', 'address'],
        token_addresses[CHAIN_IDS["MAINNET"]]["SBTC"]: ['address', 'uint24', 'address', 'uint24', 'address'],
        token_addresses[CHAIN_IDS["MAINNET"]]["RENBTC"]: ['address', 'uint24', 'address', 'uint24', 'address'],
    },
}

# chain_id -> token_from -> route_string_tuple
univ3_route_string_tuples = {
    CHAIN_IDS["MAINNET"]: {
        # FEI to USDC (FEI -> DAI -> USDC)
        token_addresses[CHAIN_IDS["MAINNET"]]["FEI"]:
            (str(token_addresses[CHAIN_IDS["MAINNET"]]["FEI"]),
                univ3_fee_tier_dicts[CHAIN_IDS["MAINNET"]
                                     ][token_addresses[CHAIN_IDS["MAINNET"]]["FEI"]],
             str(token_addresses[CHAIN_IDS["MAINNET"]]["DAI"]),
                univ3_fee_tier_dicts[CHAIN_IDS["MAINNET"]
                                     ][token_addresses[CHAIN_IDS["MAINNET"]]["DAI"]],
             str(token_addresses[CHAIN_IDS["MAINNET"]]["USDC"])),
    }
}


# for Arbitrum single token bridging (not in use atm)
L1_TO_L2_ERC20_ADDRESSES = {
    "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48": {  # USDC
        CHAIN_IDS["MAINNET"]: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        CHAIN_IDS["ARBITRUM"]: "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
        CHAIN_IDS["EVMOS"]: "0x51e44FfaD5C2B122C8b635671FCC8139dc636E82",
        CHAIN_IDS["OPTIMISM"]: "0x7f5c764cbc14f9669b88837ca1490cca17c31607",
    },
    "0xdAC17F958D2ee523a2206206994597C13D831ec7": {  # USDT
        CHAIN_IDS["MAINNET"]: "0xdac17f958d2ee523a2206206994597c13d831ec7",
        CHAIN_IDS["ARBITRUM"]: "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
        CHAIN_IDS["EVMOS"]: "0x7FF4a56B32ee13D7D4D405887E0eA37d61Ed919e",
        CHAIN_IDS["OPTIMISM"]: "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58",
    },
    "0x853d955aCEf822Db058eb8505911ED77F175b99e": {  # FRAX
        CHAIN_IDS["MAINNET"]: "0x853d955aCEf822Db058eb8505911ED77F175b99e",
        CHAIN_IDS["ARBITRUM"]: "0x17FC002b466eEc40DaE837Fc4bE5c67993ddBd6F",
        CHAIN_IDS["EVMOS"]: "0xE03494D0033687543a80c9B1ca7D6237F2EA8BD8",
        CHAIN_IDS["OPTIMISM"]: "0x2E3D870790dC77A83DD1d18184Acc7439A53f475",
    },
    "0x6B175474E89094C44Da98b954EedeAC495271d0F": {  # DAI
        CHAIN_IDS["MAINNET"]: "0x6B175474E89094C44Da98b954EedeAC495271d0F",
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
    "0xD74f5255D557944cf7Dd0E45FF521520002D5748": {  # USDS
        CHAIN_IDS["ARBITRUM"]: "0xD74f5255D557944cf7Dd0E45FF521520002D5748",
    },
    "0xfE18be6b3Bd88A2D2A7f928d00292E7a9963CfC6": {  # SBTC
        CHAIN_IDS["MAINNET"]: "0xfE18be6b3Bd88A2D2A7f928d00292E7a9963CfC6",
    },
    "0x0100546F2cD4C9D97f798fFC9755E47865FF7Ee6": {  # ALETH
        CHAIN_IDS["MAINNET"]: "0x0100546F2cD4C9D97f798fFC9755E47865FF7Ee6",
    },
    "0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D": {  # RENBTC
        CHAIN_IDS["MAINNET"]: "0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D",
        CHAIN_IDS["EVMOS"]: "0xb1a8C961385B01C3aA782fba73E151465445D319",
    },
    "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599": {  # WBTC
        CHAIN_IDS["MAINNET"]: "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        CHAIN_IDS["EVMOS"]: "0xF80699Dc594e00aE7bA200c7533a07C1604A106D",
    },
    "0xad3E3Fc59dff318BecEaAb7D00EB4F68b1EcF195": {  # WCUSD
        CHAIN_IDS["MAINNET"]: "0xad3E3Fc59dff318BecEaAb7D00EB4F68b1EcF195",
        CHAIN_IDS["EVMOS"]: "0xF80699Dc594e00aE7bA200c7533a07C1604A106D",
    },
    "0x18084fbA666a33d37592fA2633fD49a74DD93a88": {  # TBTC
        CHAIN_IDS["MAINNET"]: "0x18084fbA666a33d37592fA2633fD49a74DD93a88",
        CHAIN_IDS["EVMOS"]: "0x8d395AfFC1767141387ffF45aF88a074614E7Ccf",
        CHAIN_IDS["OPTIMISM"]: "0x220d6bEedeA6a6317DaE19d39cd62EB7bb0ae5e4",
    },
    "0x1B84765dE8B7566e4cEAF4D0fD3c5aF52D3DdE4F": {  # NUSD
        CHAIN_IDS["MAINNET"]: "0x1B84765dE8B7566e4cEAF4D0fD3c5aF52D3DdE4F",
        CHAIN_IDS["ARBITRUM"]: "0x2913E812Cf0dcCA30FB28E6Cac3d2DCFF4497688",
    },
    "0x99D8a9C45b2ecA8864373A26D1459e3Dff1e17F3": {  # MIM
        CHAIN_IDS["MAINNET"]: "0x99D8a9C45b2ecA8864373A26D1459e3Dff1e17F3",
        CHAIN_IDS["ARBITRUM"]: "0xFEa7a6a0B346362BF88A9e4A88416B77a57D6c2A",
    },
    "0x0a5E677a6A24b2F1A2Bf4F3bFfC443231d2fDEc8": {  # USX
        CHAIN_IDS["MAINNET"]: "0x0a5E677a6A24b2F1A2Bf4F3bFfC443231d2fDEc8",
    }
}
