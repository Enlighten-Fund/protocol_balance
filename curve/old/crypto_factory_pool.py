import math

from web3 import Web3

eth_rpc = "https://mainnet.infura.io/v3/e33bed8725094964a525516e1c50e0a8"


web3 = Web3(Web3.HTTPProvider(eth_rpc))
pool_registry_address = '0xF18056Bbd320E96A48e3Fbf8bC061322531aac99'
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
    },
    {
        "stateMutability": "view", 
        "type": "function", 
        "name": "get_token", 
        "inputs": [
            {
                "name": "_pool", 
                "type": "address"
            }
        ], 
        "outputs": [
            {
                "name": "", 
                "type": "address"
            }
        ]
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

# const
# main_registry = await address_getter_contract.methods.get_address(0).call()
# const
# factory_registry = await address_getter_contract.methods.get_address(3).call()
# const
# crypto_registry = await address_getter_contract.methods.get_address(5).call()
# const
# crypto_factory_registry = (blockchainId === 'ethereum') ? await address_getter_contract.methods.get_address(
#     6).call(): null


def get_crypto_factory_pool_balance(account_address):
    value = 0
    # 1. get pool address
    contract_pool_registry = web3.eth.contract(address=web3.toChecksumAddress(pool_registry_address), abi=pool_registry_abi)
    pool_count = contract_pool_registry.functions.pool_count().call()
    print('pool_count', pool_count)
    for index in range(0, pool_count):
        # 2. get lp address
        pool_address = contract_pool_registry.functions.pool_list(index).call()
        token_address = contract_pool_registry.functions.get_token(pool_address).call()
        print('index', index, 'pool_address', pool_address, 'token_address', token_address)
        # 3. balance of account
        contract_token = web3.eth.contract(address=token_address, abi=erc20_min_abi)
        balance = contract_token.functions.balanceOf(web3.toChecksumAddress(account_address)).call()
        if balance == 0:
            continue
        symbol = contract_token.functions.symbol().call()
        decimals = contract_token.functions.decimals().call()
        # 4. price of token
        contract_pool = web3.eth.contract(address=pool_address, abi=pool_abi)
        price = contract_pool.functions.lp_price().call() / 1e18
        print('symbol', symbol, 'balance', balance, 'decimals', decimals, 'price', price)
        lp_value = (balance / math.pow(10, decimals)) * price
        print('lp_value', lp_value)
        value += lp_value
    print('value', value)
    return value