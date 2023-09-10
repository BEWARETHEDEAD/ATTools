from argparse import Namespace
from types import SimpleNamespace as Namespace
import asyncio #pip install asyncio
import aiohttp #pip install aiohttp
from tonconnect.connector import AsyncConnector #pip install tonconnect
from dedust.api import API #pip install dedust
from dedust.tokens import Token #pip install dedust
import traceback
from xjet import JetAPI
from TonTools import * #pip install tontools

# DEV's:
# @dmitriypyc (help)
# @beware_the_dead (main)
# @dalvgames (help)


# DATA BY:
# DeDust.io
# fck.dev
# ton.cat




# Respone DataType
class Response(Namespace):
	async def update(self):
		
		path = getattr(Rest, self.type)
		return await path(url=self.url, headers=self.headers, data=self.data)


# Rest requests
class Rest():

	async def __init__(self, response, text, json):
		self.response = response
		self.text = text
		self.json = json


	async def get(url: str, headers: dict = None, data: dict = None):

		response_status = None
		response_text = None
		response_json = None

		async with aiohttp.ClientSession(headers=headers) as session:
			response = await session.get(url=url, json=data)

			response_status = response.status

			response_text = await response.text(encoding='UTF-8')
			response_json = await response.json()

		return Response(type='get', url=url, headers=headers, data=data, status=response_status, text=response_text, json=response_json)


	async def post(url: str, headers: dict = None, data: dict = None):

		response_status = None
		response_text = None
		response_json = None

		async with aiohttp.ClientSession(headers=headers) as session:
			response = await session.post(url=url, json=data)

			response_status = response.status

			response_text = await response.text(encoding='UTF-8')
			response_json = await response.json()

		return Response(type='post', url=url, headers=headers, data=data, status=response_status, text=response_text, json=response_json)



# Jetton DataType
class Jetton(Namespace):
	async def update(self):

		return await Jettons.get(self.contract)


# Jetton decorator
class Jettons():

	async def get(contract):

		resp = await Analyze.GetJettonInfo(contract)
		js = resp.json
		jetton_full_info = await Analyze.GetJettonFullInfo(js["name"])
		js["contract"] = contract
		js["lp_contract"] = jetton_full_info["dedust_lp_address"]

		return Jetton(
			**js, 
			price=Analyze.GetJettonPrice(contract),
			liquidity=Analyze.GetJettonLiquidity(js["name"]),
			graph_data=Analyze.GetJettonGraphData(js["name"]),
			providers=Analyze.GetJettonProviders(js["lp_contract"])
		)



# Analyze Data
class Analyze():

	async def GetJettonFullInfo(token_name: str): # Providers: FCK

		jetton_lists = await Rest.get(url=f'https://api.fck.foundation/api/v1/jettons?includeAll=false')
		filtered_list = [item for item in jetton_lists.json["data"] if item["name"] == token_name]
		return filtered_list[0]


	async def GetJettonPair(token_name: str): # Providers: FCK

		ids = await Analyze.GetJettonFullInfo(token_name)

		jetton_pairs = await Rest.get(url=f'https://api.fck.foundation/api/v3/jettons/pairs?jetton_ids={ids["id"]}&limit=10')
		filtered_pair = jetton_pairs.json["pairs"].items()
		pair = next(iter(filtered_pair))[1][0]['id']

		return pair


	async def GetJettonInfo(contract: str): # Providers: DEDUST

		return await Rest.get(url=f'https://api.dedust.io/v2/jettons/{contract}/metadata')


	async def GetJettonPrice(contract: str): # Providers: DEDUST | by dalvgames

		TOKEN = contract
		api = API()
		token = Token(api, TOKEN)
		
		return '{0:.9f}'.format(await token.get_price())


	async def GetJettonLiquidity(token_name: str): # Providers: FCK

		pair = await Analyze.GetJettonPair(token_name)
		return await Rest.get(url=f'https://api.fck.foundation/api/v3/analytics/liquidity?pairs={pair}&source=DeDust&period=h1')


	async def GetJettonGraphData(token_name: str): # Providers: FCK

		pair = await Analyze.GetJettonPair(token_name)
		return await Rest.get(url=f'https://api.fck.foundation/api/v3/analytics?pairs={pair}&page=1&period=h1&currency=TON')


	async def GetJettonProviders(lp_contract: str): #by dmitriypyk

		data = await Analyze.GetHoldersByContract(lp_contract)
		lp_price = await Analyze.GetLpPrice(lp_contract)

		providers = "".join(f"{i[0]}. <a href='https://tonscan.org/address/{i[1]}'>{i[1][0:4]}...{i[1][44:48]}</a>: {round(float(data[i[1]]), 3)} LP({round(float(data[i[1]]) * lp_price, 3)} TON)\n" for i in enumerate(data, start=1))


		return [{"address": i[1], "lp_balance": round(float(data[i[1]]), 3), "in_ton": round(float(data[i[1]]) * lp_price, 3)} for i in enumerate(data, start=1)]


	async def GetHoldersByContract(contract: str, limit: int = 30): # Providers: TonCat | by dmitriypyk

		holders = None
		result = {}

		holders_resp = await Rest.get(url=f'https://api.ton.cat/v2/contracts/jetton_minter/{contract}/holders')

		if holders_resp.json != None:
			for i in holders_resp.json["holders"][:limit]:
				if float(i["balance_normalized"]) > 0:
					result[i["holder_address"]] = i["balance_normalized"]
			return result

		else:

			return None


	async def GetLpPrice(contract: str): # Providers: TonCat | by dmitriypyk

		for i in range(3):

			jetton_liquidity = None
			lp_total_supply = None

			try:

				minter_resp = await Rest.get(url=f'https://api.ton.cat/v2/contracts/jetton_minter/{contract}')
				lp_total_supply = int(minter_resp.json["jetton"]["total_supply"]) / 1e9


				toncenter_payload = {
					"id": 1,
					"jsonrpc": "2.0",
					"method": "runGetMethod",
					"params": {
						"address": contract,
						"method": "get_reserves",
						"stack": []
					}
				}

				jetton_resp = await Rest.post(url=f'https://toncenter.com/api/v2/jsonRPC', data=toncenter_payload)
				jetton_liquidity = int(jetton_resp.json["result"]["stack"][0][1], 16) / 1e9
				break

			except Exception as e:
				await asyncio.sleep(.5)
				#traceback.print_exc()

		return (jetton_liquidity) / lp_total_supply


	async def GetJettonwalletOwner(jettonwallet_address):

		return await Rest.get(url=f'https://api.ton.cat/v2/contracts/jetton_wallet/{jettonwallet_address}')



# Wallet DataType
class Wallet_DT(Namespace):

	async def transfer(self):

		pass


# Wallet decorator
class Wallets():

	async def init(api_key, mnemonics):

		client = TonCenterClient(api_key)
		wallet = Wallet(provider=client, mnemonics=mnemonics, version='v4r2')

		return Wallet_DT(
			address=wallet.address,
			balance=WalletManager.GetBalanceByWallet(wallet.address),
			transactions=WalletManager.GetTransactions(wallet.address)
		)



# Wallet manage
class WalletManager():

	async def TonConnect(url_path_to_json: str, provider: str, payload: str): # by davlgames

		connector = AsyncConnector(url_path_to_json)
		connect_url = await connector.connect(provider, payload)

		return connector, connect_url


	async def GetTransactions(address, limit=50, offset=0):

		return await Rest.get(url=f'https://api.ton.cat/v2/contracts/address/{address}/transactions?limit={limit}&offset={offset}')


	async def GetInfoByWallet(address):

		return await Rest.get(url=f'https://api.ton.cat/v2/explorer/getWalletInformation?address={address}')


	async def GetBalanceByWallet(address):

		resp = await WalletManager.GetInfoByWallet(address)
		return int(resp.json['result']['balance'])/(10**9)


# Payment systems
class Payments():

	class xJet():

		api = None

		@classmethod
		async def CreateInvoice(cls, currency: str = '', amount: float = 0, description: str = '', max_payments: int = 1):

			try:

				invoice = await cls.api.invoice_create(currency, amount, description, max_payments)

				return invoice

			except Exception as e:
				traceback.print_exc()
				return 'xjet error'


		@classmethod
		async def CreateCheque(cls, currency: str = '', amount: int = 0, expires: int = 0, description: str = '', activates_count: int = 0, groups_id: int = None, personal_id:int = 0, password: str = None):

			try:

				cheque = await cls.api.cheque_create(currency, amount, expires, description, activates_count, groups_id, personal_id, password) # create cheque

				return cheque

			except Exception as e:
				traceback.print_exc()
				return 'xjet error'


	class TonRocket():

		api = None

		@classmethod
		async def CreateInvoice(cls, amount: float = 0, minPayment: float = 0, numPayments: int = 0, currency: str = '', description: str = '', hiddenMessage: str = '', commentsEnabled: bool = False, callbackUrl: str = '', payload: str = '', expiredIn: int = 0):

			try:

				headers = {
					'accept': 'application/json',
					'Rocket-Pay-Key': str(cls.api),
					'Content-Type': 'application/json',
				}

				data = {
					"amount": amount,
					"minPayment": minPayment,
					"numPayments": numPayments,
					"currency": currency,
					"description": description,
					"hiddenMessage": hiddenMessage,
					"commentsEnabled": commentsEnabled,
					"callbackUrl": callbackUrl,
					"payload": payload,
					"expiredIn": expiredIn
				}

				url = 'https://pay.ton-rocket.com/tg-invoices'
				resp = await Rest.post(url=url, headers=headers, data=data)

				return resp.json


			except Exception as e:
				traceback.print_exc()
				return 'tonrocket error'


		@classmethod
		async def CreateCheque(cls, currency: str = '', chequePerUser: float = 0, usersNumber: int = 0, refProgram: int = 0, password: str = '', description: str = '', sendNotification: bool = True, enableCaptcha: bool = False, telegramResourcesIds: list = [], forPremium: bool = False, linkedWallet: bool = False, disabledLanguages: list = []):

			try:

				headers = {
					'accept': 'application/json',
					'Rocket-Pay-Key': str(cls.api),
					'Content-Type': 'application/json',
				}

				data = {
					"currency": currency,
					"chequePerUser": chequePerUser,
					"usersNumber": usersNumber,
					"refProgram": refProgram,
					"password": password,
					"description": description,
					"sendNotification": sendNotification,
					"enableCaptcha": enableCaptcha,
					"telegramResourcesIds": telegramResourcesIds,
					"forPremium": forPremium,
					"linkedWallet": linkedWallet,
					"disabledLanguages": disabledLanguages
				}

				url = 'https://pay.ton-rocket.com/multi-cheques'
				resp = await Rest.post(url=url, headers=headers, data=data)

				return resp.json


			except Exception as e:
				traceback.print_exc()
				return 'tonrocket error'