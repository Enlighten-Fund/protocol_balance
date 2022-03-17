import json
import requests
from pycoingecko import CoinGeckoAPI
from web3 import Web3

url = 'https://api.yearn.finance/v1/chains/1/vaults/all'
r = requests.get(url)
json_r = json.loads(r.text)
pools = []
for pool in json_r:
    if pool['tvl']['total_assets'] > 0 and pool['tvl']['price'] > 0:
        # print(pool)
        pools.append({'address': pool['address'], 'display_name': pool['display_name'], 'token_address': pool['token']['address'],
                      'token_decimals': pool['token']['decimals'], 'totalSupply': pool['tvl']['total_assets'],
                      'token_price': pool['tvl']['price']})
eth_rpc = "https://mainnet.infura.io/v3/e33bed8725094964a525516e1c50e0a8"
web3 = Web3(Web3.HTTPProvider(eth_rpc))

pool_abi = """
[
    {
        "constant": true, 
        "inputs": [ ], 
        "name": "balance", 
        "outputs": [
            {
                "internalType": "uint256", 
                "name": "", 
                "type": "uint256"
            }
        ], 
        "payable": false, 
        "stateMutability": "view", 
        "type": "function"
        }, 
    {
        "constant": true, 
        "inputs": [
            {
                "internalType": "address", 
                "name": "account", 
                "type": "address"
            }
        ], 
        "name": "balanceOf", 
        "outputs": [
            {
                "internalType": "uint256", 
                "name": "", 
                "type": "uint256"
            }
        ], 
        "payable": false, 
        "stateMutability": "view", 
        "type": "function"
    },
    {
        "inputs": [ ], 
        "name": "bal", 
        "outputs": [
            {
                "internalType": "uint256", 
                "name": "", 
                "type": "uint256"
            }
        ], 
        "stateMutability": "view", 
        "type": "function"
    },
     {
        "name": "totalAssets", 
        "outputs": [
            {
                "type": "uint256", 
                "name": ""
            }
        ], 
        "inputs": [ ], 
        "stateMutability": "view", 
        "type": "function", 
        "gas": 4003
    },
    {
        "constant": true, 
        "inputs": [ ], 
        "name": "getPricePerFullShare", 
        "outputs": [
            {
                "internalType": "uint256", 
                "name": "", 
                "type": "uint256"
            }
        ], 
        "payable": false, 
        "stateMutability": "view", 
        "type": "function"
    },
     {
        "constant":true,
        "inputs":[],
        "name":"decimals",
        "outputs":[{"name":"","type":"uint8"}],
        "type":"function"
      },
      {
        "name": "pricePerShare", 
        "outputs": [
            {
                "type": "uint256", 
                "name": ""
            }
        ], 
        "inputs": [ ], 
        "stateMutability": "view", 
        "type": "function", 
        "gas": 12412
    }
]
"""

cg = CoinGeckoAPI()
test_address_type_v1 = '0x1cd9839a99f1e8eabcaa9e27acc499eaf03ec6b8'
test_address_type_v2 = '0xa67ec8737021a7e91e883a3277384e6018bb5776'

def get_value(account_address):
    pools_value = 0
    index = 0
    for pool in pools:
        index += 1
        # print(pool)
        print('index', index)
        pool_value = getPoolValue(pool, account_address)
        pools_value += pool_value

def getPoolValue(pool, account_address):
    pool_address = pool['address']
    display_name = pool['display_name']
    token_address = pool['token_address']
    token_decimals = pool['token_decimals']
    token_price = pool['token_price']
    totalSupply = pool['totalSupply']
    contract_pool = web3.eth.contract(address=pool_address, abi=pool_abi)
    account_balance = contract_pool.functions.balanceOf(web3.toChecksumAddress(account_address)).call()
    if account_balance == 0:
        return 0
    print('-----------')
    print('-----------')
    print('pool_address', pool_address)
    print('token_decimals', token_decimals)
    pool_token_decimals = contract_pool.functions.decimals().call()
    print('pool_token_decimals', pool_token_decimals)
    pool_token_price = get_pool_token_price(contract_pool, token_decimals)
    print('account_balance', account_balance, 'pool_token_price', pool_token_price, 'token_price', token_price, 'totalSupply', totalSupply)
    token_amount = account_balance * pool_token_price / (10 ** pool_token_decimals)
    print('display_name', display_name, 'token_amount', token_amount)
    # if token_address in crv_price:
    #     value = token_amount * crv_price[token_address]
    #     print('crv pool value', value)
    # else:
    value = token_amount * token_price
    print('token pool', value)
    return value


def get_pool_token_price(contract_pool, token_decimals):
    try:
        pool_token_price = contract_pool.functions.getPricePerFullShare().call() / (10 ** 18)
        print('pool v1')
    except Exception as e:
        pool_token_price = contract_pool.functions.pricePerShare().call() / (10 ** 18)
        print('pool v2')
    return pool_token_price

def get_aToken_price(contract_address):
    global price
    res = cg.get_token_price(id='ethereum', contract_addresses=contract_address,
                             vs_currencies='usd')
    for key in res.keys():
        price = res[key]['usd']
    return price

# TODO v3未完成
get_value(test_address_type_v2)

