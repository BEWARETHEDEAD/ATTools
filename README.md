 # ATools
Tools For TON

cur: v.0.1.1

**Installation**
```shell
pip install git+https://github.com/BEWARETHEDEAD/ATools.git
```


**Navigation**
- [Rest Requests](#rest-requests)
- [Jettons](#jettons)
    - [Jetton Analyze](#jetton-analyze)
- [Wallet](#wallet)
  
## Rest Requests
```python
import ATools

response = await ATools.Rest.get(url: str, headers: dict, data: dict, json: dict) 
# or
response = await ATools.Rest.post(url: str, headers: dict, data: dict, json: dict)

# answer data

status_code = response.status
json_answer = response.json
text_answer = response.text

# sending a repeated request by a variable reference

response = await response.update()
```

## Jettons
```python
import ATools

jetton = await ATools.Jettons.get(contract: str)

# answer data

jetton_info = jetton.jetton_full_info
jetton_contract = jetton.contract
jetton_lp_contract = jetton.lp_contract

jetton_price = await jetton.price
jetton_liquidity = await jetton.liquidity
jetton_graph_data = await jetton.graph_data
jetton_providers = await jetton.providers

# sending a repeated request by a variable reference

jetton = await jetton.update()
```

## Jetton Analyze
```python
import ATools


jetton_full_info = await ATools.Analyze.GetJettonFullInfo(token_name: str)
jetton_pair = await ATools.Analyze.GetJettonPair(token_name: str)
jetton_info = await ATools.Analyze.GetJettonInfo(contract: str)
jetton_price = await ATools.Analyze.GetJettonPrice(contract: str)
jetton_liquidity = await ATools.Analyze.GetJettonLiquidity(token_name: str)
jetton_graph_data = await ATools.Analyze.GetJettonGraphData(token_name: str)
jetton_providers = await ATools.Analyze.GetJettonProviders(lp_contract: str)
jetton_holders = await ATools.Analyze.GetHoldersByContract(contract: str, limit: int)
jetton_lp_price = await ATools.Analyze.GetLpPrice(contract: str)

jettonwallet_owner = await ATools.Analyze.GetJettonwalletOwner(jettonwallet_address: str)
```

## Wallet
```python
import ATools


wallet = await ATools.Wallets(toncenter_api_key: str, mnemonics: str)

# answer data

wallet_address = wallet.address
wallet_balance = await wallet.balance
wallet_transactions = await wallet.transactions
```
