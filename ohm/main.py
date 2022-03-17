# sOHM , gOHM
import json
import time
from threading import Thread

from web3 import Web3
from pycoingecko import CoinGeckoAPI
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

test_address_sOHM = '0xcccb1df40bacc9d5d9dc15679d029ce52dc21617'
test_address_gOHM = '0x04b35d8eb17729b2c4a4224d07727e2f71283b73'
address_ohm_stake = '0xB63cac384247597756545b500253ff8E607a8020'
address_gOHM = '0x0ab87046fBb341D058F17CBC4c1133F25a20a52f'
address_sOHM = '0x04906695D6D12CF5459975d7C3C03356E4Ccd460'
address_ohm = '0x64aa3364f17a4d01c6f1751fd97c2bd3d7e7f1d5'
eth_rpc = "https://mainnet.infura.io/v3/e33bed8725094964a525516e1c50e0a8"
web3 = Web3(Web3.HTTPProvider(eth_rpc))
contract_gOHM = web3.eth.contract(address=web3.toChecksumAddress(address_gOHM), abi=erc20_min_abi)
contract_sOHM = web3.eth.contract(address=web3.toChecksumAddress(address_sOHM), abi=erc20_min_abi)
cg = CoinGeckoAPI()
event_stake_sign = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
event_gohm_unstake_sign = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
address_0 = '0x0000000000000000000000000000000000000000'
g_ohm_price_info = {}
test_address = '0x04b35d8eb17729b2c4a4224d07727e2f71283b73'

def address_to_data(address: str):
    return address.replace('0x', '0x000000000000000000000000')

def data_to_address(data: str):
    return data.replace('0x000000000000000000000000', '0x')
#
# def get_erc20_real_amount(erc20_address, amount):
#     erc20_contract = web3.eth.contract(address=web3.toChecksumAddress(erc20_address), abi=erc20_min_abi)
#     decimals = erc20_contract.functions.decimals().call()
#     real_amount = amount / (10 ** decimals)
#     symbol = erc20_contract.functions.symbol().call()
#     return real_amount, symbol
#
# def get_aToken_price(contract_address):
#     global price
#     res = cg.get_token_price(id='ethereum', contract_addresses=contract_address,
#                              vs_currencies='usd')
#     for key in res.keys():
#         price = res[key]['usd']
#     return price
#
# def get_ohm_stake(address):
#     filter = web3.eth.filter({'fromBlock': 0, 'toBlock': 'latest',
#                               'address': web3.toChecksumAddress(address_ohm),
#                               'topics': [event_stake_sign,
#                                          address_to_data(address),
#                                          address_to_data(address_ohm_stake)]})
#     staked_amount = 0
#     for transaction in filter.get_all_entries():
#         result = Web3.toJSON(transaction)
#         print('result', result)
#         json_event = json.loads(result)
#         event_data = json_event['data']
#         amount = int(event_data.replace('0x', ''), 16)
#         print('amount', amount)
#         staked_amount += amount
#     return staked_amount
#
# def get_ohm_unstake(address):
#     filter = web3.eth.filter({'fromBlock': 0, 'toBlock': 'latest',
#                               'address': web3.toChecksumAddress(address_gOHM),
#                               'topics': [event_gohm_unstake_sign,
#                                          address_to_data(address_gOHM),
#                                          address_to_data(address)]})
#     unStaked_amount = 0
#     for transaction in filter.get_all_entries():
#         result = Web3.toJSON(transaction)
#         print('result', result)
#         json_event = json.loads(result)
#         event_data = json_event['data']
#         amount = int(event_data.replace('0x', ''), 16)
#         print('amount', amount)
#         unStaked_amount += amount
#     return staked_amount

# def get_bancor_remove(address):
#     filter = web3.eth.filter({'fromBlock': 0, 'toBlock': 'latest',
#                               'address': web3.toChecksumAddress(address_LiquidityProtectionStore),
#                               'topics': [event_ProtectionRemoved_sign,
#                                          address_to_data(address)]})
#     bancor_remove = 0
#     for transaction in filter.get_all_entries():
#         result = Web3.toJSON(transaction)
#         # print(result)
#         json_event = json.loads(result)
#         _reserveToken = data_to_address(json_event['topics'][3])
#         event_data = json_event['data']
#         _poolAmount = int(event_data.replace('0x', '')[0: 64], 16)
#         _reserveAmount = int(event_data.replace('0x', '')[64: 128], 16)
#         # print('_reserveAmount', _reserveAmount)
#         real_amount, symbol = get_erc20_real_amount(_reserveToken, _reserveAmount)
#         print('remove', symbol, 'amount', real_amount)
#         price = get_aToken_price(_reserveToken)
#         bancor_remove += (price*real_amount)
#     return bancor_remove


def get_aToken_price(contract_address):
    global price
    res = cg.get_token_price(id='ethereum', contract_addresses=contract_address,
                             vs_currencies='usd')
    for key in res.keys():
        price = res[key]['usd']
    return price

def get_sOHM_value(address):
    amount = contract_sOHM.functions.balanceOf(web3.toChecksumAddress(address)).call()
    decimals = contract_sOHM.functions.decimals().call()
    symbol = contract_sOHM.functions.symbol().call()
    price = get_aToken_price(address_ohm)
    value = price * amount / (10 ** decimals)
    print('sOHM_value', value)
    return value

def get_gOHM_value(address):
    amount = contract_gOHM.functions.balanceOf(web3.toChecksumAddress(address)).call()
    decimals = contract_gOHM.functions.decimals().call()
    symbol = contract_gOHM.functions.symbol().call()
    price = get_aToken_price(address_gOHM)
    value = price * amount / (10 ** decimals)
    print('gOHM_value', value)
    return value

def get_OHM_value(address):
    value = get_gOHM_value(address) + get_sOHM_value(address)
    print('value', value)

get_OHM_value(test_address)