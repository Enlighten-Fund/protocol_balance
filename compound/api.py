import requests

url = 'https://api.compound.finance/api/v2/account'
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
r = requests.get(url=url, headers=headers, params={'addresses': ['0x28537D30dc4384Bbd3B570c28bd60703bB15f2B7']})
print(r.text)