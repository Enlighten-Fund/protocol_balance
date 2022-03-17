import math

test_address = '0x99fd1378ca799ed6772fe7bcdc9b30b389518962'
from pycoingecko import CoinGeckoAPI
from web3 import Web3
eth_rpc = "https://mainnet.infura.io/v3/3cec0fc4a69f46d7bf0231243071cf13"
web3 = Web3(Web3.HTTPProvider(eth_rpc))

from asset import cAsset_list
from asset import asset_list

ctoken_abi = """
[
  {
        "constant": true, 
        "inputs": [
            {
                "name": "account", 
                "type": "address"
            }
        ], 
        "name": "borrowBalanceStored", 
        "outputs": [
            {
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

comptroller_address = '0xBafE01ff935C7305907c33BF824352eE5979B526'
comptroller_abi ="""
[
{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"compBorrowSpeeds","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},
{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"compBorrowState","outputs":[{"internalType":"uint224","name":"index","type":"uint224"}
]
"""

compound_address = '0xc00e94Cb662C3520282E6f5717214004A7f26888'
compound_lens_address = '0xdCbDb7306c6Ff46f77B349188dC18cEd9DF30299'
compound_lens_abi = '''
[
    {
        "constant": false, 
        "inputs": [
            {
                "internalType": "contract Comp", 
                "name": "comp", 
                "type": "address"
            }, 
            {
                "internalType": "contract ComptrollerLensInterface", 
                "name": "comptroller", 
                "type": "address"
            }, 
            {
                "internalType": "address", 
                "name": "account", 
                "type": "address"
            }
        ], 
        "name": "getCompBalanceMetadataExt", 
        "outputs": [
            {
                "components": [
                    {
                        "internalType": "uint256", 
                        "name": "balance", 
                        "type": "uint256"
                    }, 
                    {
                        "internalType": "uint256", 
                        "name": "votes", 
                        "type": "uint256"
                    }, 
                    {
                        "internalType": "address", 
                        "name": "delegate", 
                        "type": "address"
                    }, 
                    {
                        "internalType": "uint256", 
                        "name": "allocated", 
                        "type": "uint256"
                    }
                ], 
                "internalType": "struct CompoundLens.CompBalanceMetadataExt", 
                "name": "", 
                "type": "tuple"
            }
        ], 
        "payable": false, 
        "stateMutability": "nonpayable", 
        "type": "function"
    }
]
'''


cg = CoinGeckoAPI()

def get_compound_value(account_address):
    total_value = 0
    for index, c_asset in enumerate(cAsset_list):
        amount, amount_borrow, symbol = get_erc20_info(account_address, c_asset)
        c_price = get_token_price(c_asset)
        c_value = c_price * amount
        print('symbol', symbol, 'supply value', c_value)
        total_value += c_value
        asset = asset_list[index]
        price = get_token_price(asset)
        real_amount_borrow = get_erc20_real_amount(amount_borrow, asset)
        b_value = price * real_amount_borrow
        print('symbol', symbol, 'borrow value', b_value)
        total_value -= b_value
    print('total_value', total_value)

def get_compound_reward(account_address):
    compound_lens_contract = web3.eth.contract(address=web3.toChecksumAddress(compound_lens_address), abi=compound_lens_abi)
    metadata = compound_lens_contract.functions.getCompBalanceMetadataExt(web3.toChecksumAddress(compound_address), web3.toChecksumAddress(comptroller_address), web3.toChecksumAddress(account_address)).call()
    print(metadata)


# 查询erc20的信息
def get_erc20_info(account_address, erc20_address):
    erc20_contract = web3.eth.contract(address=web3.toChecksumAddress(erc20_address), abi=ctoken_abi)
    balance = erc20_contract.functions.balanceOf(web3.toChecksumAddress(account_address)).call()
    borrow_balance = erc20_contract.functions.borrowBalanceStored(web3.toChecksumAddress(account_address)).call()
    decimals = erc20_contract.functions.decimals().call()
    real_balance = balance / math.pow(10, decimals)
    symbol = erc20_contract.functions.symbol().call()
    return real_balance, borrow_balance, symbol


def get_token_price(contract_address):
    global price
    res = cg.get_token_price(id='ethereum', contract_addresses=contract_address,
                             vs_currencies='usd')
    for key in res.keys():
        price = res[key]['usd']
    return price

def get_erc20_real_amount(amount, erc20_address):
    erc20_contract = web3.eth.contract(address=web3.toChecksumAddress(erc20_address), abi=ctoken_abi)
    decimals = erc20_contract.functions.decimals().call()
    real_amount = amount / math.pow(10, decimals)
    return real_amount

# TODO get reward 失败
# get_compound_reward(test_address)

get_compound_value(test_address)