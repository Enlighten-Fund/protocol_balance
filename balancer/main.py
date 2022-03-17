import json

import requests
from string import Template

from pycoingecko import CoinGeckoAPI

QUERY = """
{
  poolShares(where :{userAddress: "0x49a2dcc237a65cc1f412ed47e0594602f6141936", balance_gt: 0}) {
    poolId {
      symbol
      tokens{
        symbol
        address
        balance
      }
      totalShares
    }
    balance
  }
}
"""

url = 'https://api.thegraph.com/subgraphs/name/balancer-labs/balancer-v2'
test_address = '0x49a2dcc237a65cc1f412ed47e0594602f6141936'
cg = CoinGeckoAPI()


def get_value():
    r = requests.post(url, json={'query': QUERY})
    json_r = json.loads(r.text)
    pools = json_r['data']['poolShares']
    value = 0
    for pool in pools:
        symbol = pool['poolId']['symbol']
        balance = float(pool['balance'])
        totalShares = float(pool['poolId']['totalShares'])
        tokens = pool['poolId']['tokens']
        pool_value = 0
        for token in tokens:
            token_address = token['address']
            token_balance = float(token['balance'])
            token_value = get_aToken_price(token_address) * token_balance
            pool_value += token_value
        user_value = balance/totalShares * pool_value
        print(symbol, user_value)
        value += user_value
    print('get_value', value)
    return value

def get_aToken_price(contract_address):
    global price
    res = cg.get_token_price(id='ethereum', contract_addresses=contract_address,
                             vs_currencies='usd')
    for key in res.keys():
        price = res[key]['usd']
    return price

get_value()
# print(1118507.475704270163994643 * 4.55)