import json
import math

from pycoingecko import CoinGeckoAPI
from web3 import Web3
eth_rpc = "https://mainnet.infura.io/v3/e33bed8725094964a525516e1c50e0a8"
web3 = Web3(Web3.HTTPProvider(eth_rpc))
address_LiquidityProtectionStore = '0xf5fab5dbd2f3bf675de4cb76517d4767013cfb55'
test_address = '0x81841b6a7a4759e1a3b2d15350dce01ea745293f'
event_ProtectionAdded_sign = '0x3ad050950cfb9657a985fbfebb84c6e7c799d8c08e4fc412cb84e9bd2e68f8cd'
event_ProtectionRemoved_sign = '0xeafbca2ddc06778be021087babbeda29033997e4e461abdc6d5bf30a0f14a025'
cg = CoinGeckoAPI()
bnt_address = '0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C'
stakingRewards_address = '0x318fEA7e45A7D3aC5999DA7e1055F5982eEB3E67'
stakingRewards_min_abi = """
[{
    "inputs": [
        {
            "internalType": "address", 
            "name": "provider", 
            "type": "address"
        }
    ], 
    "name": "pendingRewards", 
    "outputs": [
        {
            "internalType": "uint256", 
            "name": "", 
            "type": "uint256"
        }
    ], 
    "stateMutability": "view", 
    "type": "function"
}]
"""
erc20_min_abi = """
[
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

def address_to_data(address: str):
    return address.replace('0x', '0x000000000000000000000000')

def data_to_address(data: str):
    return data.replace('0x000000000000000000000000', '0x')

def get_erc20_real_amount(erc20_address, amount):
    erc20_contract = web3.eth.contract(address=web3.toChecksumAddress(erc20_address), abi=erc20_min_abi)
    decimals = erc20_contract.functions.decimals().call()
    real_amount = amount / math.pow(10, decimals)
    symbol = erc20_contract.functions.symbol().call()
    return real_amount, symbol

def get_aToken_price(contract_address):
    global price
    res = cg.get_token_price(id='ethereum', contract_addresses=contract_address,
                             vs_currencies='usd')
    for key in res.keys():
        price = res[key]['usd']
    return price

def get_bancor_add(address):
    filter = web3.eth.filter({'fromBlock': 0, 'toBlock': 'latest',
                              'address': web3.toChecksumAddress(address_LiquidityProtectionStore),
                              'topics': [event_ProtectionAdded_sign,
                                         address_to_data(address)]})
    bancor_add = 0
    for transaction in filter.get_all_entries():
        result = Web3.toJSON(transaction)
        # print(result)
        json_event = json.loads(result)
        _reserveToken = data_to_address(json_event['topics'][3])
        event_data = json_event['data']
        _poolAmount = int(event_data.replace('0x', '')[0: 64], 16)
        _reserveAmount = int(event_data.replace('0x', '')[64: 128], 16)
        # print('_reserveAmount', _reserveAmount)
        real_amount, symbol = get_erc20_real_amount(_reserveToken, _reserveAmount)
        print('add', symbol, 'amount', real_amount)
        price = get_aToken_price(_reserveToken)
        bancor_add += (price*real_amount)
        # print('bancor_balance', bancor_balance)
    return bancor_add

def get_bancor_remove(address):
    filter = web3.eth.filter({'fromBlock': 0, 'toBlock': 'latest',
                              'address': web3.toChecksumAddress(address_LiquidityProtectionStore),
                              'topics': [event_ProtectionRemoved_sign,
                                         address_to_data(address)]})
    bancor_remove = 0
    for transaction in filter.get_all_entries():
        result = Web3.toJSON(transaction)
        # print(result)
        json_event = json.loads(result)
        _reserveToken = data_to_address(json_event['topics'][3])
        event_data = json_event['data']
        _poolAmount = int(event_data.replace('0x', '')[0: 64], 16)
        _reserveAmount = int(event_data.replace('0x', '')[64: 128], 16)
        # print('_reserveAmount', _reserveAmount)
        real_amount, symbol = get_erc20_real_amount(_reserveToken, _reserveAmount)
        print('remove', symbol, 'amount', real_amount)
        price = get_aToken_price(_reserveToken)
        bancor_remove += (price*real_amount)
    return bancor_remove

def get_reward(account_address):
    reward_contract = web3.eth.contract(address=web3.toChecksumAddress(stakingRewards_address),
                                        abi=stakingRewards_min_abi)
    amount = reward_contract.functions.pendingRewards(web3.toChecksumAddress(account_address)).call()
    real_amount = amount / math.pow(10, 18)
    price = get_aToken_price(bnt_address)
    value = price * real_amount
    print('reward bnt amount', real_amount, 'price', price, 'value', value)
    return value

def get_bancor_value(address):
    asset_value = get_bancor_add(address) - get_bancor_remove(address)
    print('asset_value', asset_value)
    reward_value = get_reward(address)
    print('reward_value', reward_value)
    value = asset_value + reward_value
    return value

value = get_bancor_value(test_address)
print('bancor value', value)