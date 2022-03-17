from web3 import Web3
bsc_rpc = "https://bsc-dataseed.binance.org/"
web3 = Web3(Web3.HTTPProvider(bsc_rpc))
#  'address': '0x28537D30dc4384Bbd3B570c28bd60703bB15f2B7'
filter = web3.eth.filter({'fromBlock': 15532779, 'toBlock': 15532779, 'address': web3.toChecksumAddress('0x58F876857a02D6762E0101bb5C46A8c1ED44Dc16')})
for transaction in filter.get_all_entries():
    result = Web3.toJSON(transaction)
    print(result)