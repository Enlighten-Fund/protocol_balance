# 0xdAC17F958D2ee523a2206206994597C13D831ec7
# 0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599
from web3 import Web3
from pycoingecko import CoinGeckoAPI
web3 = Web3()
cg = CoinGeckoAPI()
# res = cg.get_asset_platforms()
res = cg.get_token_price(id='ethereum', contract_addresses='0xdAC17F958D2ee523a2206206994597C13D831ec7', vs_currencies='usd')
# print('res', res)
for key in res.keys():
    print(res[key]['usd'])
