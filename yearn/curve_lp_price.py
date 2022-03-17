import math

from pycoingecko import CoinGeckoAPI
from web3 import Web3

eth_rpc = "https://mainnet.infura.io/v3/e33bed8725094964a525516e1c50e0a8"


web3 = Web3(Web3.HTTPProvider(eth_rpc))
stable_factory_pool_registry_address = '0xB9fC157394Af804a3578134A6585C0dc9cc990d4'
crypto_pool_registry_address = '0x8F942C20D02bEfc377D41445793068908E2250D0'
crypto_factory_pool_registry_address = '0xF18056Bbd320E96A48e3Fbf8bC061322531aac99'
main_pool_registry_address = '0x90E00ACe148ca3b23Ac1bC8C240C2a7Dd9c2d7f5'

pool_registry_abi = '''
[
    {
        "stateMutability": "view", 
        "type": "function", 
        "name": "pool_list", 
        "inputs": [
            {
                "name": "arg0", 
                "type": "uint256"
            }
        ], 
        "outputs": [
            {
                "name": "", 
                "type": "address"
            }
        ], 
        "gas": 2217
    },
    {
        "stateMutability": "view", 
        "type": "function", 
        "name": "pool_count", 
        "inputs": [ ], 
        "outputs": [
            {
                "name": "", 
                "type": "uint256"
            }
        ], 
        "gas": 2138
    },
    {
        "stateMutability": "view", 
        "type": "function", 
        "name": "get_n_coins", 
        "inputs": [
            {
                "name": "_pool", 
                "type": "address"
            }
        ], 
        "outputs": [
            {
                "name": "", 
                "type": "uint256"
            }
        ], 
        "gas": 2699
    },
    {
        "stateMutability": "view", 
        "type": "function", 
        "name": "get_coins", 
        "inputs": [
            {
                "name": "_pool", 
                "type": "address"
            }
        ], 
        "outputs": [
            {
                "name": "", 
                "type": "address[4]"
            }
        ], 
        "gas": 9164
    },
    {
        "stateMutability": "view", 
        "type": "function", 
        "name": "get_balances", 
        "inputs": [
            {
                "name": "_pool", 
                "type": "address"
            }
        ], 
        "outputs": [
            {
                "name": "", 
                "type": "uint256[4]"
            }
        ], 
        "gas": 20435
    },
    {
        "stateMutability": "view", 
        "type": "function", 
        "name": "get_lp_token", 
        "inputs": [
            {
                "name": "arg0", 
                "type": "address"
            }
        ], 
        "outputs": [
            {
                "name": "", 
                "type": "address"
            }
        ], 
        "gas": 2473
    },
    {
        "stateMutability": "view", 
        "type": "function", 
        "name": "get_virtual_price_from_lp_token", 
        "inputs": [
            {
                "name": "_token", 
                "type": "address"
            }
        ], 
        "outputs": [
            {
                "name": "", 
                "type": "uint256"
            }
        ], 
        "gas": 1927
    }
]
'''

erc20_min_abi = """
[
  {
    "constant":true,
    "inputs":[{"name":"_owner","type":"address"}],
    "name":"balanceOf",
    "outputs":[{"name":"balance","type":"uint256"}],
    "type":"function"
  },
  {
    "constant":true,
    "inputs":[],
    "name":"decimals",
    "outputs":[{"name":"","type":"uint8"}],
    "type":"function"
  },
  {
	"constant": true,
	"inputs": [],
	"name": "symbol",
	"outputs": [{
		"name": "",
		"type": "string"
	}],
	"payable": false,
	"stateMutability": "view",
	"type": "function"
  },
  {
        "stateMutability": "view", 
        "type": "function", 
        "name": "totalSupply", 
        "inputs": [ ], 
        "outputs": [
            {
                "name": "", 
                "type": "uint256"
            }
        ], 
        "gas": 3378
    }
]
"""

pool_abi = '''
[
{
    "stateMutability": "view", 
    "type": "function", 
    "name": "lp_price", 
    "inputs": [ ], 
    "outputs": [
        {
            "name": "", 
            "type": "uint256"
        }
    ]
}
]
'''

cg = CoinGeckoAPI()
lp_price_set = {}
def get_stable_factory_pool_price():
    value = 0
    # 1. get pool address
    contract_pool_registry = web3.eth.contract(address=web3.toChecksumAddress(stable_factory_pool_registry_address), abi=pool_registry_abi)
    pool_count = contract_pool_registry.functions.pool_count().call()
    print('pool_count', pool_count)
    for index in range(0, pool_count):
        # 2. get lp address
        pool_address = contract_pool_registry.functions.pool_list(index).call()
        print('index', index, 'pool_address', pool_address)
        # 3. balance of account
        contract_pool = web3.eth.contract(address=pool_address, abi=erc20_min_abi)
        decimals = contract_pool.functions.decimals().call()
        totalSupply = contract_pool.functions.totalSupply().call()
        price = get_stable_factory_lp_price(contract_pool_registry, totalSupply, pool_address, decimals)
        if price:
            lp_price_set[web3.toChecksumAddress(pool_address)] = price
            print('----pool_price----', pool_address, price)
    return value

def get_stable_factory_lp_price(contract_pool_registry, totalSupply, pool_address, decimals):
    if totalSupply == 0:
        return 0
    total_value = 0
    n = contract_pool_registry.functions.get_n_coins(pool_address).call()
    coins = contract_pool_registry.functions.get_coins(pool_address).call()
    balances = contract_pool_registry.functions.get_balances(pool_address).call()
    for index in range(0, n):
        coin_address = coins[index]
        if coin_address == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
            return None
        coin_balance = balances[index]
        real_amount, symbol = get_erc20_real_amount(coin_balance, coin_address)
        print('coin_address', coin_address, 'coin_balance', coin_balance, 'real_amount', real_amount, 'symbol', symbol)
        token_price = get_aToken_price(coin_address)
        if not token_price:
            return None
        print('token_price', token_price)
        total_value += real_amount * token_price
        print('real_amount', real_amount, 'symbol', symbol, 'price', token_price)
    lp_price = total_value / (totalSupply / math.pow(10, decimals))
    print('lp_price', lp_price)
    return lp_price

def get_aToken_price(contract_address):
    try:
        global price
        res = cg.get_token_price(id='ethereum', contract_addresses=contract_address,
                                 vs_currencies='usd')
        for key in res.keys():
            price = res[key]['usd']
        return price
    except Exception as e:
        return None

def get_erc20_real_amount(amount, erc20_address):
    erc20_contract = web3.eth.contract(address=web3.toChecksumAddress(erc20_address), abi=erc20_min_abi)
    decimals = erc20_contract.functions.decimals().call()
    real_amount = amount / math.pow(10, decimals)
    symbol = erc20_contract.functions.symbol().call()
    return real_amount, symbol


def get_crypto_factory_pool_price():
    value = 0
    # 1. get pool address
    contract_pool_registry = web3.eth.contract(address=web3.toChecksumAddress(crypto_factory_pool_registry_address), abi=pool_registry_abi)
    pool_count = contract_pool_registry.functions.pool_count().call()
    print('pool_count', pool_count)
    for index in range(0, pool_count):
        # 2. get lp address
        pool_address = contract_pool_registry.functions.pool_list(index).call()
        # 4. price of token
        contract_pool = web3.eth.contract(address=pool_address, abi=pool_abi)
        price = contract_pool.functions.lp_price().call() / 1e18
        if price:
            lp_price_set[web3.toChecksumAddress(pool_address)] = price
            print('----pool_price----', pool_address, price)
    return value

def get_crypto_pool_price():
    # 1. get pool address
    contract_pool_registry = web3.eth.contract(address=web3.toChecksumAddress(crypto_pool_registry_address), abi=pool_registry_abi)
    pool_count = contract_pool_registry.functions.pool_count().call()
    print('pool_count', pool_count)
    for index in range(0, pool_count):
        # 2. get lp address
        pool_address = contract_pool_registry.functions.pool_list(index).call()
        lp_token_address = contract_pool_registry.functions.get_lp_token(pool_address).call()
        # 4. price of lp_token
        price = contract_pool_registry.functions.get_virtual_price_from_lp_token(lp_token_address).call() / 1e18
        if price:
            lp_price_set[web3.toChecksumAddress(pool_address)] = price
            print('----pool_price----', pool_address, price)

def get_main_pool_balance():
    value = 0
    # 1. get pool address
    contract_pool_registry = web3.eth.contract(address=web3.toChecksumAddress(main_pool_registry_address), abi=pool_registry_abi)
    pool_count = contract_pool_registry.functions.pool_count().call()
    for index in range(0, pool_count):
        # 2. get lp address
        pool_address = contract_pool_registry.functions.pool_list(index).call()
        lp_token_address = contract_pool_registry.functions.get_lp_token(pool_address).call()
        price = contract_pool_registry.functions.get_virtual_price_from_lp_token(lp_token_address).call() / 1e18
        if price:
            lp_price_set[web3.toChecksumAddress(pool_address)] = price
            print('----pool_price----', pool_address, price)
    return value

def get_crv_lp_price():
    get_stable_factory_pool_price()
    get_crypto_factory_pool_price()
    get_crypto_pool_price()
    get_main_pool_balance()
    print(lp_price_set)

get_crv_lp_price()