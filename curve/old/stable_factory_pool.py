import math

from pycoingecko import CoinGeckoAPI
from web3 import Web3

eth_rpc = "https://mainnet.infura.io/v3/e33bed8725094964a525516e1c50e0a8"


web3 = Web3(Web3.HTTPProvider(eth_rpc))
pool_registry_address = '0xB9fC157394Af804a3578134A6585C0dc9cc990d4'
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
cg = CoinGeckoAPI()

def get_stable_factory_pool_balance(account_address):
    value = 0
    # 1. get pool address
    contract_pool_registry = web3.eth.contract(address=web3.toChecksumAddress(pool_registry_address), abi=pool_registry_abi)
    pool_count = contract_pool_registry.functions.pool_count().call()
    print('pool_count', pool_count)
    for index in range(0, pool_count):
        # 2. get lp address
        pool_address = contract_pool_registry.functions.pool_list(index).call()
        print('index', index, 'pool_address', pool_address)
        # 3. balance of account
        contract_pool = web3.eth.contract(address=pool_address, abi=erc20_min_abi)
        balance = contract_pool.functions.balanceOf(web3.toChecksumAddress(account_address)).call()
        if balance == 0:
            continue
        print('balance', balance)
        symbol = contract_pool.functions.symbol().call()
        print('symbol', symbol)
        decimals = contract_pool.functions.decimals().call()
        print('decimals', decimals)
        totalSupply = contract_pool.functions.totalSupply().call()
        print('totalSupply', totalSupply)
        if totalSupply == 0:
            continue
        # 4. price of lp_token
        price = get_lp_price(contract_pool_registry, totalSupply, pool_address, decimals)
        if not price:
            continue
        print('symbol', symbol, 'balance', balance, 'decimals', decimals)
        lp_value = (balance / math.pow(10, decimals)) * price
        print('lp_value', lp_value)
        value += lp_value
        print('--------------')
        print('--------------')
        print('--------------')
    print('value', value)

    return value

def get_lp_price(contract_pool_registry, totalSupply, pool_address, decimals):
    total_value = 0
    n = contract_pool_registry.functions.get_n_coins(pool_address).call()
    print('n', n)
    coins = contract_pool_registry.functions.get_coins(pool_address).call()
    print('coins', coins)
    balances = contract_pool_registry.functions.get_balances(pool_address).call()
    print('balances', balances)
    for index in range(0, n):
        coin_address = coins[index]
        if coin_address == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE' :
            return None
        if coin_address == '0x0000000000000000000000000000000000000000' :
            continue
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