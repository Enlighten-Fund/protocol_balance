from pycoingecko import CoinGeckoAPI
from web3 import Web3
eth_rpc = "https://mainnet.infura.io/v3/e33bed8725094964a525516e1c50e0a8"
web3 = Web3(Web3.HTTPProvider(eth_rpc))
address_vecrv = '0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2'
address_crv = '0xd533a949740bb3306d119cc777fa900ba034cd52'
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
cg = CoinGeckoAPI()
def get_ve_crv_balance(account_address):
    contract_vecrv = web3.eth.contract(address=web3.toChecksumAddress(address_vecrv), abi=erc20_min_abi)
    amount = contract_vecrv.functions.balanceOf(web3.toChecksumAddress(account_address)).call()
    symbol = contract_vecrv.functions.symbol().call()
    decimals = contract_vecrv.functions.decimals().call()
    price = get_aToken_price(address_crv)
    value = price * amount / (10 ** decimals)
    print('value', value)
    return value

def get_aToken_price(contract_address):
    global price
    res = cg.get_token_price(id='ethereum', contract_addresses=contract_address,
                             vs_currencies='usd')
    for key in res.keys():
        price = res[key]['usd']
    return price
