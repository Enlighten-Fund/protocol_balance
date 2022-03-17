import math

from web3 import Web3
rpc = "https://rpc.goerli.mudit.blog/"
asserts = ['0x3fb4601911871b635011aF01eDda5854F27560ce',
           '0xA6282Dc28e45782a80119eE99aF0FC9C77972eA4',
           '0x3A61F2CAa1CAbf360581DB5047d6F6161D2bF38D',
           '0x048e4FbA85e97c04061938fB38E583FE9F4dDD9F',
           '0x3A61F2CAa1CAbf360581DB5047d6F6161D2bF38D',
           '0x048e4FbA85e97c04061938fB38E583FE9F4dDD9F',
           '0x499d11E0b6eAC7c0593d8Fb292DCBbF815Fb29Ae',
           '0xdFBd9ED34C8Bc8Ec6640a005471bF9F9A70cD8D5',
           '0xd35CCeEAD182dcee0F148EbaC9447DA2c4D449c4']
contract_address = '0xEcacf2A05B6ef6b1AD36F29E48F36F0629f2B083'
web3 = Web3(Web3.HTTPProvider(rpc))
erc20_min_abi = """
[
	{
		"inputs": [
			{
				"internalType": "address[]",
				"name": "assets",
				"type": "address[]"
			},
			{
				"internalType": "address",
				"name": "acc_addr",
				"type": "address"
			}
		],
		"name": "fetch_tokens",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "balances",
				"type": "uint256[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]
"""

# 查询erc20的信息
def get_erc20_info_batch(account_address):
    erc20_contract = web3.eth.contract(address=web3.toChecksumAddress(contract_address), abi=erc20_min_abi)
    balances = erc20_contract.functions.fetch_tokens(asserts,web3.toChecksumAddress(account_address)).call()
    print(balances)

get_erc20_info_batch('0x572efefacd35f8acf0ba8d0a89332e8b3a52c6ac')