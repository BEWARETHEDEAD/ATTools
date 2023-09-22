 # ATTools
Analyticks Ton Tools

cur: v.0.2.0

# ⚙️ UTILITIES:
  [🤖][TON Inspect](https://t.me/toninsbot) (@toninsbot)

**Installation**
```shell
pip install git+https://github.com/BEWARETHEDEAD/ATTools.git
```

```shell
pip install ATTools
```

# ⏳ Soon ...
- Payment Systems:
    - Wallet Pay
    - integration to telegram-bot by injection (?)
 
- Wallet:
    - NFT transfers
 
- NFT:
    - NFT transfers

- Data Providers (new block)
    - choise data-provider


# 🧭 Navigation
- [🔗 Rest Requests](#-rest-requests)
-
- [📦 Wrap Data](#-wrap-data)
    - [Check Raw](#check-raw)
    - [Pack Raw](#pack-raw)
    - [UnPack Raw](#unpack-raw)
- 
- [🌕 Jettons](#-jettons)
    - [Jetton Analyze](#jetton-analyze)
-
- [🔎 Analyze](#-analyze)
- 
- [🔗 Blockchain](#-blockchain)
-     
- [👛 Wallet](#-wallet)
    - [Wallet Manager](#wallet-manager)
-
- [🏦 Payment Systems](#-payment-systems)
    - [🟥 xJetSwap](#-xjetswap)
        - [xJet About](#xjet-about)
        - [xJet Invoices](#xjet-invoices)
        - [xJet Cheques](#xjet-cheques)
        - [xJet NFT](#xjet-nft)
        - [xJet Exchange](#xjet-exchange)

    - [🟦 TonRocket](#-tonrocket)
        - [TonRocket About](#tonrocket-about)
        - [TonRocket Invoices](#tonrocket-invoices)
        - [TonRocket Cheques](#tonrocket-cheques)
     
    - [🔵 CryptoBot](#-cryptobot)
        - [CryptoBot About](#cryptobot-about)
        - [CryptoBot Invoices](#cryptobot-invoices)
        - [CryptoBot Exchange](#cryptobot-exchange)
     
- [🖼 NFT](#-nft)

## 🔗 Rest Requests
```python
import ATTools

response = await ATTools.Rest.get(url: str, headers: dict, data: dict, json: dict) 
# or
response = await ATTools.Rest.post(url: str, headers: dict, data: dict, json: dict)

# answer data

status_code = response.status
json_answer = response.json
text_answer = response.text

# sending a repeated request by a variable reference

response = await response.update()
```

## 📦 Wrap Data
   ### Check Raw
   ```python
   import ATTools

   bounceable_address = await ATTools.WrapData.CheckRaw(contract: str)
   ```
   ### Pack Raw
   ```python
   import ATTools

   bounceable_address = await ATTools.WrapData.PackRaw(contract: str)
   ```
   ### UnPack Raw
   ```python
   import ATTools

   non_bounceable_address = await ATTools.WrapData.UnPackRaw(contract: str)
   ```

## 🌕 Jettons
```python
import ATTools

jetton = await ATTools.Jettons.get(contract: str)

# answer data

address = jetton.address
raw_address = jetton.raw_address
lp_address = jetton.lp_address
name = jetton.name
symbol = jetton.symbol
description = jetton.description
decimals = jetton.decimals
price = await jetton.price
liquidity = await jetton.liquidity
graph_data = await jetton.graph_data
liquidity_providers = await jetton.providers

# sending a repeated request by a variable reference
jetton = await jetton.update()

# another jettons methods
minter = await ATTools.Jettons.CreateJettonMinter(address: str)
mint_body = await ATTools.Jettons.CreateMintBody(address: str, mint_amount: int)
change_owner_body = await ATTools.Jettons.CreateChangeOwnerBody(address: str)
burn_body = await ATTools.Jettons.CreateBurnBody(burn_amount: int)
```

## Jetton Analyze
```python
import ATTools

jetton_by_name = await ATTools.Analyze.GetJettonByName(token_name: str)

jetton_full_info = await ATTools.Analyze.GetJettonFullInfo(token_name: str)
jetton_pair = await ATTools.Analyze.GetJettonPair(token_name: str)
jetton_info = await ATTools.Analyze.GetJettonInfo(contract: str)
jetton_price = await ATTools.Analyze.GetJettonPrice(contract: str)
jetton_liquidity = await ATTools.Analyze.GetJettonLiquidity(token_name: str)
jetton_graph_data = await ATTools.Analyze.GetJettonGraphData(token_name: str)
jetton_providers = await ATTools.Analyze.GetJettonProviders(lp_contract: str)
jetton_holders = await ATTools.Analyze.GetHoldersByContract(contract: str, limit: int)
jetton_lp_price = await ATTools.Analyze.GetLpPrice(contract: str)
jetton_lp_address = await ATTools.Analyze.GetJettonLpAddress(address: str, is_stable: bool)

jettonwallet_owner = await ATTools.Analyze.GetJettonwalletOwner(jettonwallet_address: str)
```

## 🔎 Analyze
```python
import ATTools

address_info = await ATTools.Analyze.GetInfoOfAddress(address: str)
dedust_pools = await ATTOols.Analyze.GetPools()
address_from_domain = await ATTools.Analyze.ResolveDomain(domain: str)
```

## 🔗 Blockchain
```python
import ATTools

send_boc = await ATTools.Blockchain.SendBoc(boc: str)
```

## 👛 Wallet
```python
import ATTools


wallet = ATTools.Wallets(toncenter_api_key: str, mnemonics: list)

# Transfer TON
await wallet.Transfer(destination_address: str, amount: float)

# Transfer Jetton
await wallet.Transfer(destination_address: str, token_name: str, amount: float, fee: float)


# answer data

wallet_address = wallet.address
wallet_balance = await wallet.balance
wallet_transactions = await wallet.transactions
wallet_nfts = await wallet.nft

# mint jettons
min_new_jetton = await wallet.MintJettons(mint_amount: int, jetton_content_uri: str)
#ex: 'https://raw.githubusercontent.com/yungwine/pyton-lessons/master/lesson-6/token_data.json'
```

## Wallet Manager
```python
import ATTools


tonconnect_obj = await ATTools.WalletManager.TonConnect(url_path_to_json: str, provider: str, payload: str)

# answer data

connector, connect_url = tonconnect_obj

# connected wallet address

address = await connector.get_address()



wallet_transactions = await ATTools.WalletManager.GetTransactions(address: str, limit: int, offset: int)
wallet_info = await ATTools.WalletManager.GetInfoByWallet(address: str)
wallet_ton_balance = await ATTools.WalletManager.GetBalanceByWallet(address: str)
wallet_full_balance = await ATTools.Analyze.GetFullWalletBalance(address: str)
```


# 🏦 Payment Systems

- ## 🟥 xJetSwap
    - ### xJet About
      ```python
      import ATTools

      
      xJet = ATTools.Payments.xJet(
          api_key: str,
          private_key: str
      )
      
      # Backend Methods
      longpool = await xJet.LongPool()
      
      
      
      # About
      currencys = await xJet.Currencies()
      me = await xJet.Me()
      balance = await xJet.Balance()
      sumbit_deposit = await xJet.SubmitDeposit()
      
      withdraw = await xJet.Withdraw(address: str, currency: str, amount: float)
      operations = await xJet.Operations(limit: int, offset: int)
      ```
      
    - ### xJet Invoices
      ```python
      import ATTools

      
      xJet = ATTools.Payments.xJet(
          api_key: str,
          private_key: str
      )

      # Invoices
      invoice = await xJet.CreateInvoice(
          currency: str, 
          amount: float, 
          description: str, 
          max_payments: int
      )
      invoice_status = await xJet.InvoiceStatus(invoice_id: str)
      invoice_list = await xJet.InvoiceList()
      ```
      
    - ### xJet Cheques
      ```python
      import ATTools

      
      xJet = ATTools.Payments.xJet(
          api_key: str,
          private_key: str
      )
      
      # Cheques
      cheque = await xJet.CreateCheque(
          currency: str, 
          amount: int, 
          expires: int, 
          description: str, 
          activates_count: int, 
          groups_id: int, 
          personal_id: int, 
          password: str
      )
      cheque_status = await xJet.ChequeStatus(cheque_id: str)
      cheque_list = await xJet.ChequeList()
      cheque_cancel = await xJet.ChequeCancel(cheque_id: str)

      ```
      
    - ### xJet NFT
      ```python
      import ATTools

      
      xJet = ATTools.Payments.xJet(
          api_key: str,
          private_key: str
      )

      # NFT methods
      nft_list = await xJet.NftList()
      nft_transfer = await xJet.NftTransfer(nft_address: str, destination_address: str)

      ```
      
    - ### xJet Exchange
      ```python
      import ATTools

      
      xJet = ATTools.Payments.xJet(
          api_key: str,
          private_key: str
      )

      # Exchange methods
      exchange_pairs = await xJet.ExchangePairs()
      exchange_estimate = await xJet.ExchangeEstimate(
          tokens: list = ['left', 'right'], 
          type: str = 'buy' or 'sell', 
          amount: int
      )
      exchange_create_order = await xJet.ExchangeCreateOrder(
          tokens: list = ['left', 'right'], 
          type: str = 'buy' or 'sell', 
          amount: int, 
          min_receive_amount: int
      )
      exchange_order_status = await xJet.ExchangeOrderStatus(order_id: str)
      ```
      
- ## 🟦 TonRocket
    - ### TonRocket About
      ```python
      import ATTools

      TR = ATTools.Payments.TonRocket(
          api_key: str
      )

      # About
      info = await TR.Info()
      transfer = await TR.Transfer(
          user_id: int, 
          currency: str, 
          amount: float, 
          transfer_id: str, 
          description: str
      )
      withdrawal = await TR.Withdrawal(
          destination_address: str, 
          currency: str, 
          amount: float, 
          withdrawal_id: str, 
          comment: str
      )

      ```
      
    - ### TonRocket Invoices
      ```python
      import ATTools

      TR = ATTools.Payments.TonRocket(
          api_key: str
      )
      
      # Invoice methods
      invoice = await TR.CreateInvoice(
          amount: float, 
          minPayment: float, 
          numPayments: int, 
          currency: str, 
          description: str, 
          hiddenMessage: str, 
          commentsEnabled: bool, 
          callbackUrl: str, 
          payload: str, 
          expiredIn: int
      )

      ```

    - ### TonRocket Cheques
      ```python
      import ATTools

      TR = ATTools.Payments.TonRocket(
          api_key: str
      )
      
      # Cheque methods
      cheque = await TR.CreateCheque(
          currency: str, 
          chequePerUser: float, 
          usersNumber: int, 
          refProgram: int, 
          password: str, 
          description: str, 
          sendNotification: bool, 
          enableCaptcha: bool, 
          telegramResourcesIds: list, 
          forPremium: bool, 
          linkedWallet: bool, 
          disabledLanguages: list
      )
      ```
      
- ## 🔵 CryptoBot
  - ### CryptoBot About
      ```python
      import ATTools

      CB = ATTools.Payments.CryptoBot(
          api_key: str
      )

      # About
      me = await CB.Me()
      balance = await CB.Balance()
      transfer = await CB.Transfer(
          user_id: int, 
          currency: str, 
          amount: float, 
          spend_id: str, 
          comment: str, 
          disable_send_notification: bool
      )
      ```
      
  - ### Cryptobot Invoices
      ```python
      import ATTools

      CB = ATTools.Payments.Cryptobot(
          api_key: str
      )

      invoice = await CB.CreateInvoice(
          currency: str, 
          amount: float, 
          description: str, 
          hidden_message: str, 
          paid_btn_name: str, 
          paid_btn_url: str, 
          payload: str, 
          allow_comments: bool, 
          allow_anonymous: bool, 
          expires_in: int
      )
      invoice_status = await CB.InvoiceStatus(
          currency: str, 
          invoice_ids: str, 
          status: str, 
          offset: int, 
          count: int
      )
      ```

  - ### Cryptobot Exchange
      ```python
      import ATTools

      CB = ATTools.Payments.Cryptobot(
          api_key: str
      )

      exchange_rates = await CB.ExchangeRates()
      exchange_currencies = await CB.ExchangeCurrencies(
          invoice_id: int, 
          status: str, 
          hash: str, 
          currency: str, 
          amount: float, 
          fee: str, 
          pay_url: str, 
          description: str, 
          created_at: str, 
          usd_rate: str, 
          allow_comments: bool, 
          allow_anonymous: bool, 
          expiration_date: str, 
          paid_at: str, 
          paid_anonymously: bool, 
          comment: str, 
          hidden_message: str, 
          payload: str, 
          paid_btn_name: str, 
          paid_btn_url: str
      )
      ```

# 🖼 NFT
```python
import ATTools


nfts_on_wallet = await ATTools.NFT.GetNFTOnWallet(address: str)
nfts_info = await ATTools.NFT.GetNFTInfo(address: str)
collection_info = await ATTools.NFT.GetNFTCollectionInfo(address: str)
```
