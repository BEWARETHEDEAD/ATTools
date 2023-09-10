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
