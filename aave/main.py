import json
import math

from web3 import Web3
from pycoingecko import CoinGeckoAPI
eth_rpc = "https://mainnet.infura.io/v3/e33bed8725094964a525516e1c50e0a8"
aave_lending_pool_contract_address = "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9"
test_address = '0x9cd9f38caf08999e660af70d11bb9ce08f16bc42'
web3 = Web3(Web3.HTTPProvider(eth_rpc))
cg = CoinGeckoAPI()
stk_aave_address = '0x4da27a545c0c5B758a6BA100e3a049001de870f5'
aave_address = '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9'
aave_incentives_controller_address = '0xd784927Ff2f95ba542BfC824c8a8a98F3495f6b5'
reward_min_abi = """
[{
    "inputs": [
        {
            "internalType": "address[]", 
            "name": "assets", 
            "type": "address[]"
        }, 
        {
            "internalType": "address", 
            "name": "user", 
            "type": "address"
        }
    ], 
    "name": "getRewardsBalance", 
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
# 1.资产 2.负债 3.rewards 4.stkAAVE
def get_aave_value(account_address):
    reward_assets = []
    aave_balance = 0
    # 1.拿到lendingPool中所有支持的token
    with open("lending_pool_abi.json", encoding='utf-8') as f:
        lending_pool_abi = json.load(f)
    lending_pool_contract = web3.eth.contract(address=web3.toChecksumAddress(aave_lending_pool_contract_address), abi=lending_pool_abi)
    asset_list = lending_pool_contract.functions.getReservesList().call()
    # 2.找到这些token所对应的aToken、stableDebtToken、variableDebtToken的地址
    for asset_address in asset_list:
        reserve_data = lending_pool_contract.functions.getReserveData(asset_address).call()
        aToken_address = reserve_data[-5]
        stableDebtToken_address = reserve_data[-4]
        variableDebtToken_address = reserve_data[-3]
        # print('aToken', aToken_address, 'stableDebtToken_address', stableDebtToken_address,
        #       'variableDebtToken_address', variableDebtToken_address)
        aToken_balance, aToken_symbol = get_erc20_info(account_address, aToken_address)
        stableDebtToken_balance, stableDebtToken_symbol = get_erc20_info(account_address, stableDebtToken_address)
        variableDebtToken_balance,  variableDebtToken_symbol= get_erc20_info(account_address, variableDebtToken_address)
        if aToken_balance > 0:
            reward_assets.append(aToken_address)
        elif stableDebtToken_balance > 0:
            reward_assets.append(stableDebtToken_address)
        elif variableDebtToken_balance > 0:
            reward_assets.append(variableDebtToken_address)
        else:
            continue
        print(aToken_symbol, 'aToken_balance', aToken_balance, 'stableDebtToken_balance',
              stableDebtToken_balance, 'variableDebtToken_balance', variableDebtToken_balance)
        price = get_aToken_price(aToken_address)
        # 3. 余额 = 资产 - 债务
        aave_asset_balance = price * (aToken_balance - stableDebtToken_balance - variableDebtToken_balance)
        print('asset', aToken_symbol, 'balance', aave_asset_balance)
        # 4. 计入总余额
        aave_balance += aave_asset_balance
    reward_value = get_rewards(reward_assets, account_address)
    aave_balance += reward_value
    # stk-aave_contract
    stk_aave_value = get_stk_aave_value(account_address)
    aave_balance += stk_aave_value
    return aave_balance

def get_stk_aave_value(account_address):
    real_balance, symbol = get_erc20_info(account_address, stk_aave_address)
    price = get_aToken_price(aave_address)
    value = price * real_balance
    print('stk aave_contract amount', real_balance, 'price', price, 'value', value)
    return value

def get_rewards(reward_assets, account_address):
    reward_contract = web3.eth.contract(address=web3.toChecksumAddress(aave_incentives_controller_address), abi=reward_min_abi)
    amount = reward_contract.functions.getRewardsBalance(reward_assets, web3.toChecksumAddress(account_address)).call()
    real_amount, symbol = get_erc20_real_amount(amount, stk_aave_address)
    price = get_aToken_price(aave_address)
    value = price * real_amount
    print('get_rewards', symbol, 'price', price, 'amount', real_amount, 'value', value)
    return value



def get_aToken_price(contract_address):
    global price
    res = cg.get_token_price(id='ethereum', contract_addresses=contract_address,
                             vs_currencies='usd')
    for key in res.keys():
        price = res[key]['usd']
    return price

# 查询erc20的信息
def get_erc20_info(account_address, erc20_address):
    erc20_contract = web3.eth.contract(address=web3.toChecksumAddress(erc20_address), abi=erc20_min_abi)
    balance = erc20_contract.functions.balanceOf(web3.toChecksumAddress(account_address)).call()
    decimals = erc20_contract.functions.decimals().call()
    real_balance = balance / math.pow(10, decimals)
    symbol = erc20_contract.functions.symbol().call()
    return real_balance, symbol

def get_erc20_real_amount(amount, erc20_address):
    erc20_contract = web3.eth.contract(address=web3.toChecksumAddress(erc20_address), abi=erc20_min_abi)
    decimals = erc20_contract.functions.decimals().call()
    real_amount = amount / math.pow(10, decimals)
    symbol = erc20_contract.functions.symbol().call()
    return real_amount, symbol

value = get_aave_value(test_address)
print(value)