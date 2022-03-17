import json
import requests
from web3 import Web3

from curve.veCRV import get_ve_crv_balance

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
  },
{
    "name": "lp_token", 
    "outputs": [
        {
            "type": "address", 
            "name": ""
        }
    ], 
    "inputs": [ ], 
    "stateMutability": "view", 
    "type": "function", 
    "gas": 1481
}
]
"""
base_url = 'https://api.curve.fi'
eth_rpc = "https://mainnet.infura.io/v3/e33bed8725094964a525516e1c50e0a8"
web3 = Web3(Web3.HTTPProvider(eth_rpc))
factory_crypto_url = '/api/getPools/ethereum/factory-crypto'
main_url = '/api/getPools/ethereum/main'
crypto_url = '/api/getPools/ethereum/crypto'
factory_url = '/api/getPools/ethereum/factory'
# pool_list_url = '/api/getPoolList'
# factory_pools_url = '/api/getFactoryV2Pools'

test_address = '0xb258ad4125e84068f3a47fbbc4f6aced2bc148ec'

def get_factory_crypto_balance(account_address):
    value = 0
    result = requests.get(url=base_url+factory_crypto_url)
    pools = result.json()['data']['poolData']
    # print(len(pools))
    for pool in pools:
        if float(pool['usdTotal']) > 0:
            lp_address = pool['lpTokenAddress']
            print('lpTokenAddress', lp_address)
            usdTotal = pool['usdTotal']
            pool_value, symbol = get_factory_crypto_pool_value(account_address, lp_address, usdTotal)
            print(symbol, pool_value)
            value += pool_value
    return value

def get_factory_crypto_pool_value(account_address, lp_address, usdTotal):
    contract_pool = web3.eth.contract(address=web3.toChecksumAddress(lp_address), abi=erc20_min_abi)
    account_balance = contract_pool.functions.balanceOf(web3.toChecksumAddress(account_address)).call()
    symbol = contract_pool.functions.symbol().call()
    if account_balance == 0:
        return 0, symbol
    totalSupply = contract_pool.functions.totalSupply().call()

    pool_value = account_balance / totalSupply * usdTotal
    return pool_value, symbol

def get_main_balance(account_address):
    value = 0
    result = requests.get(url=base_url + main_url)
    print(result.text)
    pools = result.json()['data']['poolData']
    print(len(pools))
    for pool in pools:
        if float(pool['usdTotal']) > 0 and 'gaugeAddress' in pool:
            gaugeAddress = pool['gaugeAddress']
            usdTotal = pool['usdTotal']
            pool_value, symbol = get_main_pool_value(account_address, gaugeAddress, usdTotal)
            print(symbol, pool_value)
            value += pool_value
    return value

def get_main_pool_value(account_address, gauge_address, usdTotal):
    gauge = web3.eth.contract(address=web3.toChecksumAddress(gauge_address), abi=erc20_min_abi)
    lp_token_address = gauge.functions.lp_token().call()
    print('lp_token_address', lp_token_address)
    lp_token = web3.eth.contract(address=web3.toChecksumAddress(lp_token_address), abi=erc20_min_abi)
    account_balance = lp_token.functions.balanceOf(web3.toChecksumAddress(account_address)).call()
    symbol = lp_token.functions.symbol().call()
    if account_balance == 0:
        return 0, symbol
    totalSupply = lp_token.functions.totalSupply().call()
    pool_value = account_balance / totalSupply * usdTotal
    return pool_value, symbol

def get_crypto_balance(account_address):
    value = 0
    result = requests.get(url=base_url + crypto_url)
    pools = result.json()['data']['poolData']
    print(len(pools))
    for pool in pools:
        if float(pool['usdTotal']) > 0:
            lpTokenAddress = pool['lpTokenAddress']
            usdTotal = pool['usdTotal']
            pool_value, symbol = get_factory_crypto_pool_value(account_address, lpTokenAddress, usdTotal)
            print(symbol, pool_value)
            value += pool_value
    return value

def get_factory_balance(account_address):
    value = 0
    result = requests.get(url=base_url + factory_url)
    pools = result.json()['data']['poolData']
    print(len(pools))
    for pool in pools:
        if float(pool['usdTotal']) > 0:
            lpTokenAddress = pool['address']
            usdTotal = pool['usdTotal']
            pool_value, symbol = get_factory_crypto_pool_value(account_address, lpTokenAddress, usdTotal)
            print(symbol, pool_value)
            value += pool_value
    return value

def get_balance(account_address):
    value_factory_pool = get_factory_balance(account_address)
    value_crypto_pool = get_crypto_balance(account_address)
    value_main_pool = get_main_balance(account_address)
    value_factory_crypto_pool = get_factory_crypto_balance(account_address)
    ve_crv_value = get_ve_crv_balance(account_address)
    value = value_factory_pool + value_crypto_pool + value_main_pool + value_factory_crypto_pool + ve_crv_value
    print('value', value)

# TODO 第三方farming的池子没找到
get_balance(test_address)