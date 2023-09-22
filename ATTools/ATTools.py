from argparse import Namespace
from types import SimpleNamespace as Namespace
from functools import wraps #pip install functools
from functools import partial
from types import FunctionType
from types import MethodType
from types import GeneratorType
from typing import Any
from types import CoroutineType
import asyncio #pip install asyncio
import aiohttp #pip install aiohttp
from tonconnect.connector import AsyncConnector
from dedust.api import API #pip install dedust
from dedust.tokens import Token #pip install dedust
import traceback
from xjet import JetAPI #pip install xjet
from TonTools import * #pip install tontools
import inspect
import functools #pip install functools
import os
from tonsdk.utils import Address, bytes_to_b64str #pip install tonsdk
from tonsdk.boc import begin_cell, Slice, Cell
from base64 import b64decode
from tonsdk.contract.token.ft import JettonMinter, JettonWallet
from tonsdk.utils import to_nano, bytes_to_b64str
from tonsdk.contract.wallet import Wallets, WalletVersionEnum

import logging


# DEV's:
# @shibdev (help)
# @beware_the_dead (main)
# @dalvgames (help)


# DATA BY:
# DeDust.io
# fck.dev
# ton.cat
# tonapi.io




# Wraper in Namespace for Payments() child methods
async def convert_to_namespace(data):
	if isinstance(data, dict):
		return Namespace(**{key: await convert_to_namespace(value) for key, value in data.items()})
	elif isinstance(data, list):
		return [await convert_to_namespace(item) for item in data]
	else:
		return data


def wrap_result_in_namespace(func):
	async def wrapper(*args, **kwargs):
		result = await func(*args, **kwargs)
		
		return await convert_to_namespace(result)
	
	return wrapper  



class Providers():

	async def providers(self, method_name):

		matching_methods = []
		def find_methods_in_class(class_obj):
			members = inspect.getmembers(class_obj)
			for name, member in members:
				if not '__' in name and name != 'providers':
					matching_methods.append(f"{class_obj.__qualname__}.{name}")

			for base_class in class_obj.__bases__:
				find_methods_in_class(base_class)

		find_methods_in_class(self.__class__)
		return matching_methods


	class DeDust():

		def __init__(self):
			self.url = 'https://api.dedust.io/v2'

		async def GetJettonInfo(self, contract: str = ''):
			return f'{self.url}/jettons/{contract}/metadata'


	class TonApi():

		def __init__(self):
			self.url = 'https://tonapi.io/v1'

		async def GetJettonInfo(self, contract: str = ''):
			return f'{self.url}/jetton/getInfo?account={contract}'


	class TonCat():

		def __init__(self):
			self.url = 'https://api.ton.cat/v2'

		async def GetJettonInfo(self, contract: str = ''):
			return f'{self.url}/contracts/jetton/{contract}'


	class Toncenter():

		def __init__(self):
			self.url = 'https://toncenter.com/api/v2'




# Respone DataType
class Response(Namespace):
	async def update(self):
		
		path = getattr(Rest, self.type)
		return await path(url=self.url, headers=self.headers, data=self.data, json=self.json_data)


# Rest requests
class Rest():

	async def __init__(self, response, text, json):
		self.response = response
		self.text = text
		self.json = json


	async def get(url: str, headers: dict = None, data: dict = None, json: dict = None):

		response_status = None
		response_text = None
		response_json = None

		async with aiohttp.ClientSession(headers=headers) as session:
			response = await session.get(url=url, json=json, data=data)

			response_status = response.status

			try:
				response_text = await response.text(encoding='UTF-8')
				response_json = await response.json()
			except Exception as e:
				#traceback.print_exc()
				pass

		return Response(type='get', url=url, headers=headers, json_data=json, data=data, status=response_status, text=response_text, json=response_json)


	async def post(url: str, headers: dict = None, data: dict = None, json: dict = None):

		response_status = None
		response_text = None
		response_json = None

		async with aiohttp.ClientSession(headers=headers) as session:
			response = await session.post(url=url, json=json, data=data)

			response_status = response.status

			try:
				response_text = await response.text(encoding='UTF-8')
				response_json = await response.json()
			except Exception as e:
				#traceback.print_exc()
				pass

		return Response(type='post', url=url, headers=headers, json_data=json, data=data, status=response_status, text=response_text, json=response_json)



# Jetton DataType
class Jetton(Namespace):
	async def update(self):

		return await Jettons.get(self.contract)


# Jetton decorator
class Jettons():

	def __init__(self):
		# Создаем экземпляр класса Providers
		provider_instance = Providers()

		# Добавляем метод find из Providers ко всем методам в классе M
		for method_name in dir(self.__class__.__name__):
			method = getattr(self.__class__.__name__, method_name)
			if callable(method) and not method_name.startswith("__"):
				partial_function = partial(provider_instance.provider, method_name)
				setattr(method, f'providers', partial_function)


	async def get(contract):

		try:
			logging.debug(contract)
			contract = await WrapData.CheckRaw(contract)
			lp_address = await Analyze.GetJettonLpAddress(contract)
			provider = Providers.TonCat
			resp = await Analyze.GetJettonInfo(contract, provider=provider)
			jet = await WrapData.WrapJettonInfoToUniversal(resp.json, provider)

			return Jetton(
				address=contract,
				raw_address=await WrapData.UnPackRaw(contract),
				lp_address=lp_address,
				name=jet.name,
				symbol=jet.symbol,
				description=jet.description,
				decimals=jet.decimals, 
				price=Analyze.GetJettonPrice(contract),
				liquidity=Analyze.GetJettonLiquidity(contract),
				graph_data=Analyze.GetJettonGraphData(jet.name),
				providers=Analyze.GetJettonProviders(lp_address)
			)

		except Exception as e:
			traceback.print_exc()
			return traceback.format_exc()
			pass


	async def CreateJettonMinter(address: str = '', jetton_content_uri: str = ''):
		minter = JettonMinter(admin_address=Address(address),
			jetton_content_uri=jetton_content_uri, #ex: 'https://raw.githubusercontent.com/yungwine/pyton-lessons/master/lesson-6/token_data.json'
			jetton_wallet_code_hex=JettonWallet.code)

		return minter


	async def CreateMintBody(address: str = '', mint_amount: int = 0, jetton_content_uri: str = ''):
		minter = await CreateJettonMinter(jetton_content_uri=jetton_content_uri)

		body = minter.CreateMintBody(destination=Address(address),
			jetton_amount=to_nano(int(mint_amount), 'ton'))
		return body


	async def CreateChangeOwnerBody(address: str = '', jetton_content_uri: str = ''):
		minter = await CreateJettonMinter(jetton_content_uri=jetton_content_uri)

		body = minter.CreateChangeAdminBody(
			new_admin_address=Address(address))
		return body


	async def CreateBurnBody(burn_amount: int = 0):
		body = JettonWallet().CreateBurnBody(
			jetton_amount=to_nano(int(burn_amount), 'ton'))
		return body




class WrapData():

	async def CheckRaw(contract: str = ''):

		if '0:' in str(contract):
			return await WrapData.PackRaw(contract)
		else:
			return contract


	async def PackRaw(contract: str = ''):

		return Address(contract).to_string(1, 1, 1)


	async def UnPackRaw(contract: str = ''):

		bytess = Address(contract).to_buffer()
		hex_string = '0:' + ''.join('{:02x}'.format(byte) for byte in bytess)
		return hex_string[:-8]


	async def WrapJettonInfoToUniversal(data: dict, provider: Providers):

		provider_name = os.path.basename(provider.__name__)

		ans = {}

		if provider_name == 'TonCat':
			logging.debug(data)
			data=data["jetton"]["metadata"]
			ans["name"] = data["name"]
			ans["description"] = data["description"]
			ans["symbol"] = data["symbol"]
			ans["decimals"] = data["decimals"]
			if data["image"]:
				ans["image"] = data["image"]["original"]
			else:
				ans["image"] = {}

		return Namespace(**ans)


# Analyze Data
class Analyze():

	def __init__(self):
		# Create an instance of the Providers class
		self.provider_instance = Providers()

		# Add the 'provider' attribute to wrapper methods
		for method_name in dir(self):
			method = getattr(self, method_name)
			if callable(method) and not method_name.startswith("__"):
				# Create a wrapper method that calls the original method
				def method_wrapper(*args, **kwargs):
					return method(*args, **kwargs)

				# Add the 'provider' attribute to the wrapper method
				partial_function = partial(self.provider_instance.providers, method_name)
				setattr(method_wrapper, 'providers', partial_function)

				# Set the 'provider' attribute on the original method
				setattr(self, method_name, method_wrapper)


	async def ResolveDomain(self, domain: str = ''):
		resp = await Rest.get(url=f'https://api.ton.cat/v2/contracts/dns/resolve?domain={domain}')
		return await convert_to_namespace(resp.json)


	async def GetPools(self):
		resp = await Rest.get(url=f'https://api.dedust.io/v2/pools')
		return resp.json


	async def GetTokenInPool(self, address: str = '', pools: dict = {}):
		pool = None
		jetton_index = None
		for pool in pools:
			ton, jetton = False, False
			for i, asset in enumerate(pool['assets']):
				if asset['type'] == 'native' and asset['metadata']['symbol'] == 'TON':
					ton = True
				elif asset['type'] == 'jetton' and asset['address'] == address:
					jetton = True
					jetton_index = i
			
			if ton and jetton:
				break
		
		return pool, jetton_index


	async def GetPoolReserves(self, pool: dict = {}):
		return tuple(map(int, pool['reserves']))


	async def GetInfoOfAddress(self, address: str = ''):

		address = await WrapData.CheckRaw(address)
		resp = await Rest.get(url=f'https://tonviewer.com/_next/data/{address}.json?value={address}')

		key = str(resp.text).split('"buildId":"')[1].split('"')[0]
		resp = await Rest.get(url=f'https://tonviewer.com/_next/data/{key}/{address}.json?value={address}')

		logging.debug(resp.json['pageProps'])
		return await convert_to_namespace(resp.json['pageProps'])


	async def GetTransactionInfo(self, hashs: str = '', include_msg_body: bool = True):

		resp = await Rest.get(url=f'https://toncenter.com/api/index/getTransactionByHash?tx_hash={hashs}&include_msg_body={include_msg_body}')
		
		if resp.json == []:
			await asyncio.sleep(1)
			hashs = hashs.replace("+", "%2B").replace("=", "%3D").replace(f'_', "%2F")
			resp = await Rest.get(url=f'https://toncenter.com/api/index/getTransactionByHash?tx_hash={hashs}&include_msg_body={include_msg_body}')

		return await convert_to_namespace(resp.json[0])


	async def GetJettonLpAddress(self, address: str = '', is_stable: bool = False): #by shibdev

		address = Address(address) if type(address) == str else address

		left_asset = bytes_to_b64str(begin_cell().store_uint(0, 4).end_cell().to_boc()) # NATIVE asset
		right_asset = bytes_to_b64str(begin_cell().store_uint(1, 4).store_int(address.wc, 8).store_bytes(address.hash_part).end_cell().to_boc())

		payload = {
		  "id": 1,
		  "jsonrpc": "2.0",
		  "method": "runGetMethod",
		  "params": {
			"address": "EQBfBWT7X2BHg9tXAxzhz2aKiNTU1tpt5NsiK0uSDW_YAJ67",
			"method": "get_pool_address",
			"stack": [
			  [
				"int",
				"1" if is_stable else "0"
			  ],
			  [
				"tvm.Slice",
				left_asset
			  ],
			  [
				"tvm.Slice",
				right_asset
			  ]
			]
		  }
		}

		r = await Rest.post(url="https://toncenter.com/api/v2/jsonRPC", json=payload)
		return Slice(Cell.one_from_boc(b64decode(r.json["result"]["stack"][0][1]["bytes"]))).read_msg_addr().to_string(1, 1, 1)


	async def GetJettonByName(self, token_name: str = ''): # Providers: TonAPI

		resp = await Rest.get(url=f'https://tonapi.io/v2/accounts/search?name={token_name}')
		return await convert_to_namespace(resp.json)


	async def GetJettonFullInfo(self, token_name: str = '', contract: str = ''): # Providers: FCK

		jetton_lists = await Rest.get(url=f'https://api.fck.foundation/api/v1/jettons?includeAll=false')
		filtered_list = [item for item in jetton_lists.json["data"] if item["name"] == token_name and await WrapData.PackRaw(item["name"]) == contract]
		return filtered_list[0]


	async def GetJettonPair(self, token_name: str = '', contract: str = ''): # Providers: FCK

		ids = await Analyze.GetJettonFullInfo(token_name, contract)

		jetton_pairs = await Rest.get(url=f'https://api.fck.foundation/api/v3/jettons/pairs?jetton_ids={ids["id"]}&limit=10')
		filtered_pair = jetton_pairs.json["pairs"].items()
		pair = next(iter(filtered_pair))[1][0]['id']

		return pair


	async def GetJettonInfo(self, contract: str = '', provider: Providers = Providers.TonCat):

		cf = current_function = inspect.currentframe().f_code
		url = getattr(provider(), str(cf.co_name))

		return await Rest.get(url=await url(contract))


	async def GetJettonPrice(self, contract: str = ''): # Providers: DEDUST | by dalvgames

		TOKEN = contract
		api = API()
		token = Token(api, TOKEN)
		
		return '{0:.9f}'.format(await token.get_price())


	async def GetJettonLiquidity(self, contract: str = ''): # Providers: DeDust

		pools = await Analyze.GetPools()
		pool, jetton_index = await Analyze.GetTokenInPool(contract, pools)
		ton_index = int(not jetton_index)
		reserves = await Analyze.GetPoolReserves(pool)
		return Namespace(tokens=format(reserves[jetton_index]/1e9, '.10f') if jetton_index != None else 0, ton=format(reserves[ton_index]/1e9, '.10f') if jetton_index != None else 0)


	async def GetJettonGraphData(self, token_name: str = '', contract: str = ''): # Providers: FCK

		pair = await Analyze.GetJettonPair(token_name, contract)
		return await Rest.get(url=f'https://api.fck.foundation/api/v3/analytics?pairs={pair}&page=1&period=h1&currency=TON')


	async def GetJettonProviders(self, lp_contract: str = ''): #by shibdev

		data = await Analyze.GetHoldersByContract(lp_contract)
		lp_price = await Analyze.GetLpPrice(lp_contract)

		providers = "".join(f"{i[0]}. <a href='https://tonscan.org/address/{i[1]}'>{i[1][0:4]}...{i[1][44:48]}</a>: {round(float(data[i[1]]), 3)} LP({round(float(data[i[1]]) * lp_price, 3)} TON)\n" for i in enumerate(data, start=1))


		return [{"address": i[1], "lp_balance": round(float(data[i[1]]), 3), "in_ton": round(float(data[i[1]]) * lp_price, 3)} for i in enumerate(data, start=1)]


	async def GetHoldersByContract(self, contract: str = '', limit: int = 30): # Providers: TonCat | by shibdev

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


	async def GetLpPrice(self, contract: str = ''): # Providers: TonCat | by shibdev

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

				jetton_resp = await Rest.post(url=f'https://toncenter.com/api/v2/jsonRPC', json=toncenter_payload)
				jetton_liquidity = int(jetton_resp.json["result"]["stack"][0][1], 16) / 1e9
				break

			except Exception as e:
				await asyncio.sleep(.5)
				#traceback.print_exc()

		return (jetton_liquidity) / lp_total_supply


	async def GetJettonwalletOwner(self, jettonwallet_address: str = ''):

		return await Rest.get(url=f'https://api.ton.cat/v2/contracts/jetton_wallet/{jettonwallet_address}')


	async def GetFullWalletBalance(self, address: str = ''):

		def filter_non_zero_balance(item):
			return item["balance"] != '0'

		resp = await Rest.get(f'https://tonapi.io/v1/jetton/getBalances?account={address}')
		resp.json['balances'].append(await WalletManager.GetBalanceByWallet(address))
		return await convert_to_namespace(list(filter(filter_non_zero_balance, resp.json['balances'])))


class Blockchain():

	async def SendBoc(boc: str = ''):

		resp = await Rest.post(url=f'https://toncenter.com/api/v2/sendBoc', json={"boc": boc})
		return resp.json


	async def RunGetMethod(address: str = '', method: str = '', stack: list = []):

		payload = {
			"address": address.to_string(1, 1, 1) if type(address) == Address else address,
			"method": method,
			"stack": stack
		}

		resp = await Rest.post(url='https://toncenter.com/api/v2/runGetMethod', json=payload)
		r = resp.json

		stack = []
		for s in r["result"]["stack"]:
			if s[0] == "num":
				stack.append({"type": "int", "value": int(s[1], 16)})
			elif s[0] == "null":
				stack.append({"type": "null"})
			elif s[0] == "cell":
				stack.append({"type": "cell", "value": Cell.one_from_boc(b64decode(s[1]["bytes"])).begin_parse()})
			elif s[0] == "slice":
				stack.append({"type": "slice", "value": Cell.one_from_boc(b64decode(s[1]["bytes"])).begin_parse()})
			elif s[0] == "builder":
				stack.append({"type": "builder", "value": Cell.one_from_boc(b64decode([1]["bytes"]))})
		return stack


class Wallet_():

	def __init__(self, toncenter_api_key: str = '', mnemonics: list = []):

		client = TonCenterClient(toncenter_api_key)
		wallet = Wallet(provider=client, mnemonics=mnemonics, version='v4r2')

		self.address = wallet.address
		self.balance = Analyze.GetFullWalletBalance(wallet.address)
		self.transactions = WalletManager.GetTransactions(wallet.address)
		self.nft = NFT.GetNFTOnWallet(address=wallet.address)
		self.wallet_obj = wallet


	async def Transfer(self, destination_address: str = '', token_name: str = '', amount: float = 0, message: str = '', fee: float = 0):

		if token_name == '':
			return await self.wallet_obj.transfer_ton(destination_address, amount, message)
		else:
			token = found_data = next((item for item in await self.balance if hasattr(item, 'metadata') and hasattr(item.metadata, 'name') and item.metadata.name == token_name), None)
			if token != None:
				return await self.wallet_obj.transfer_jetton(destination_address, token.jetton_address, amount, fee)
			else:
				return f'not found token {token_name} on your wallet!'


	async def MintJettons(self, mint_amount: int = 0, jetton_content_uri: str = ''):

		body = await Jettons.CreateMintBody(self.address, mint_amount, jetton_content_uri)
		minter = await Jettons.CreateJettonMinter(self.address, jetton_content_uri)
		seqno = await Blockchain.RunGetMethod(self.address, 'seqno')

		query = await self.wallet_obj.create_transfer_message(to_addr=minter.address.to_string(),
			amount=to_nano(0.04, 'ton'),
			seqno=int(seqno),
			payload=body
		)

		boc = bytes_to_b64str(query["message"].to_boc(False))
		return await Blockchain.SendBoc(boc)


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
		return {"balance": int(resp.json['result']['balance']), "metadata": {"address": address, "decimals": 9, "image": "", "name": "Toncoin", "symbol": "TON"}}



# NFT manage
class NFT():

	async def GetNFTOnWallet(address: str = '', provider: str = None):

		headers = {
			'Content-Type': 'application/json'
		}

		query = """
			query NftItemConnection($ownerAddress: String!, $first: Int!, $after: String) {
			  nftItemsByOwner(ownerAddress: $ownerAddress, first: $first, after: $after) {
				cursor
				items {
				  id
				  name
				  address
				  index
				  kind
				  image: content {
					type: __typename
					... on NftContentImage {
					  originalUrl
					  thumb: image {
						sized(width: 480, height: 480)
					  }
					}
					... on NftContentLottie {
					  preview: image {
						sized(width: 480, height: 480)
					  }
					}
					... on NftContentVideo {
					  cover: preview(width: 480, height: 480)
					}
				  }
				  collection {
					address
					name
					isVerified
				  }
				  sale {
					... on NftSaleFixPrice {
					  fullPrice
					}
				  }
				}
			  }
			 }
		"""

		data = {
			"query": query,
			"variables": {
				"ownerAddress": str(address),
				"first": 24
			}
		}

		resp = await Rest.post(url='https://api.getgems.io/graphql', json=data, headers=headers)

		return await convert_to_namespace(resp.json['data']['nftItemsByOwner'])


	async def GetNFTInfo(address: str = '', provider: str = None): # Provider: TonCat

		headers = {
			'Content-Type': 'application/json'
		}

		resp = await Rest.get(url=f'https://api.ton.cat/v2/contracts/nft_item/{address}', headers=headers)
		resp.json['collection_info'] = NFT.GetNFTCollectionInfo(address=resp.json['nft_item']['collection_address'])

		return await convert_to_namespace(resp.json)


	async def GetNFTCollectionInfo(address: str = '', provider: str = None): # Provider: TonCat

		headers = {
			'Content-Type': 'application/json'
		}

		resp = await Rest.get(url=f'https://api.ton.cat/v2/contracts/nft_collection/{address}', headers=headers)

		return await convert_to_namespace(resp.json)


	async def GetCurNFTsOnWallet(address: str = '', collection_address: str = '', provider: str = None): # Provider: TonCat

		headers = {
			'Content-Type': 'application/json'
		}

		resp = await Rest.get(url=f'https://tonapi.io/v1/nft/searchItems?owner={address}&collection={collection_address}&include_on_sale=true&limit=1000&offset=0', headers=headers)

		return await convert_to_namespace(resp.json)


# Payment systems
class Payments():


	class xJet():

		def __init__(self, api_key, private_key, network='mainnet'):
			self.api_key = api_key
			self.private_key = private_key
			self.network = network

			Payments.xJet.api = JetAPI(
				api_key=self.api_key,
				private_key=self.private_key,
				network=self.network
			)

			{setattr(Payments.xJet, name, wrap_result_in_namespace(method)) for name, method in vars(Payments.xJet).items() if callable(method) and name != '__init__'}


		# Backend Methods
		
		async def LongPool(self):
			try:

				headers = {
					'X-API-Key': self.api.api_key
				}

				response = await Rest.get(url='http://xjet.app/api/v1/account.events', headers=headers)

				return response.json

			except Exception as e:
				traceback.print_exc()
				return 'xjet error'





		# About
		
		async def Currencies(self):

			return await xjet.currencies()


		#
		async def Me(self):

			return await self.api.me()


		
		async def Balance(self):

			return await self.api.balance()


		
		async def SubmitDeposit(self):

			return await self.api.submit_deposit()


		
		async def Withdraw(self, address: str = '', currency: str = '', amount: float = 0):

			try:

				return await self.api.withdraw(address, currency, amount)

			except Exception as e:
				return 'xjet error'
				traceback.print_exc()


		
		async def Operations(self, limit: int = 0, offset: int = 0):

			try:

				return await self.api.operations(limit, offset)

			except Exception as e:
				return 'xjet error'
				traceback.print_exc()





		# Invoices
		
		async def CreateInvoice(self, currency: str = '', amount: float = 0, description: str = '', max_payments: int = 1):

			try:

				return await self.api.invoice_create(currency, amount, description, max_payments)

			except Exception as e:
				traceback.print_exc()
				return 'xjet error'


		
		async def InvoiceStatus(self, invoice_id: str = ''):

			try:

				return await self.api.invoice_status(invoice_id)

			except Exception as e:
				traceback.print_exc()
				return 'xjet error'


		
		async def InvoiceList(self):

			try:

				return await self.api.invoice_list()

			except Exception as e:
				traceback.print_exc()
				return 'xjet error'





		# Cheques
		
		async def CreateCheque(self, currency: str = '', amount: int = 0, expires: int = 0, description: str = '', activates_count: int = 0, groups_id: int = None, personal_id:int = 0, password: str = None):

			try:

				return await self.api.cheque_create(currency, amount, expires, description, activates_count, groups_id, personal_id, password) # create cheque

			except Exception as e:
				traceback.print_exc()
				return 'xjet error'


		
		async def ChequeStatus(self, cheque_id: str = ''):

			try:

				return await self.api.cheque_status(cheque_id)

			except Exception as e:
				traceback.print_exc()
				return 'xjet error'


		
		async def ChequeList(self):

			try:

				return await self.api.cheque_list() 

			except Exception as e:
				traceback.print_exc()
				return 'xjet error'


		
		async def ChequeCancel(self, cheque_id: str = ''):

			try:

				return await self.api.cheque_cancel(cheque_id)

			except Exception as e:
				traceback.print_exc()
				return 'xjet error'





		# NFT methods
		
		async def NftList(self):

			try:

				return await self.api.nft_list()

			except Exception as e:
				traceback.print_exc()
				return 'xjet error'


		
		async def NftTransfer(self, nft_address: str = '', destination_address: str = ''):

			try:

				return await self.api.nft_transfer(nft_address, destination_address)

			except Exception as e:
				traceback.print_exc()
				return 'xjet error'




		# Exchange methods
		
		async def ExchangePairs(self):

			try:

				return await self.api.exchange_pairs()

			except Exception as e:
				traceback.print_exc()
				return 'xjet error'


		
		async def ExchangeEstimate(self, tokens: list = ['left', 'right'], type: str = '', amount: int = 0):

			try:

				return await self.api.exchange_estimate(tokens, type, amount)

			except Exception as e:
				traceback.print_exc()
				return 'xjet error'


		
		async def ExchangeCreateOrder(self, tokens: list = ['left', 'right'], type: str = '', amount: int = 0, min_receive_amount: int = 0):

			try:

				return await self.api.exchange_create_order(tokens, type, amount, min_receive_amount)

			except Exception as e:
				traceback.print_exc()
				return 'xjet error'


		
		async def ExchangeOrderStatus(self, order_id: str = ''):

			try:

				return await self.api.exchange_order_status(order_id)

			except Exception as e:
				traceback.print_exc()
				return 'xjet error'



	
	class TonRocket():

		def __init__(self, api_key):
			self.api = api_key

			{setattr(Payments.TonRocket, name, wrap_result_in_namespace(method)) for name, method in vars(Payments.TonRocket).items() if callable(method) and name != '__init__'}


		# About
		
		async def Info(self):

			try:

				headers = {
					'accept': 'application/json',
					'Rocket-Pay-Key': str(self.api),
					'Content-Type': 'application/json',
				}

				url = 'https://pay.ton-rocket.com/app/info'
				resp = await Rest.get(url=url, headers=headers)

				return resp.json


			except Exception as e:
				traceback.print_exc()
				return 'tonrocket error'





		# App methods
		
		async def Transfer(self, user_id: int = 0, currency: str = '', amount: float = 0, transfer_id: str = '', description: str = ''):

			try:

				headers = {
					'accept': 'application/json',
					'Rocket-Pay-Key': str(self.api),
					'Content-Type': 'application/json',
				}

				data = {
					"tgUserId": user_id,
					"currency": currency,
					"amount": amount,
					"transferId": transfer_id,
					"description": description
				}

				url = 'https://pay.ton-rocket.com/app/transfer'
				resp = await Rest.post(url=url, headers=headers, json=data)

				return resp.json


			except Exception as e:
				traceback.print_exc()
				return 'tonrocket error'


		
		async def Withdrawal(self, destination_address: str = '', currency: str = '', amount: float = 0, withdrawal_id: str = '', comment: str = ''):

			try:

				headers = {
					'accept': 'application/json',
					'Rocket-Pay-Key': str(self.api),
					'Content-Type': 'application/json',
				}

				data = {
					"network": "TON",
					"address": destination_address,
					"currency": currency,
					"amount": amount,
					"withdrawalId": withdrawal_id,
					"comment": comment
				}

				url = 'https://pay.ton-rocket.com/app/withdrawal'
				resp = await Rest.post(url=url, headers=headers, json=data)

				return resp.json


			except Exception as e:
				traceback.print_exc()
				return 'tonrocket error'





		# Invoice methods
		
		async def CreateInvoice(self, amount: float = 0, minPayment: float = 0, numPayments: int = 0, currency: str = '', description: str = '', hiddenMessage: str = '', commentsEnabled: bool = False, callbackUrl: str = '', payload: str = '', expiredIn: int = 0):

			try:

				headers = {
					'accept': 'application/json',
					'Rocket-Pay-Key': str(self.api),
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
				resp = await Rest.post(url=url, headers=headers, json=data)

				return resp.json


			except Exception as e:
				traceback.print_exc()
				return 'tonrocket error'




		# Cheque methods
		
		async def CreateCheque(self, currency: str = '', chequePerUser: float = 0, usersNumber: int = 0, refProgram: int = 0, password: str = '', description: str = '', sendNotification: bool = True, enableCaptcha: bool = False, telegramResourcesIds: list = [], forPremium: bool = False, linkedWallet: bool = False, disabledLanguages: list = []):

			try:

				headers = {
					'accept': 'application/json',
					'Rocket-Pay-Key': str(self.api),
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
				resp = await Rest.post(url=url, headers=headers, json=data)

				return resp.json


			except Exception as e:
				traceback.print_exc()
				return 'tonrocket error'


	class CryptoBot():

		def __init__(self, api_key):
			self.api = api_key

			{setattr(Payments.CryptoBot, name, wrap_result_in_namespace(method)) for name, method in vars(Payments.CryptoBot).items() if callable(method) and name != '__init__'}


		# About
		async def Me(self):

			try:

				headers = {
					'accept': 'application/json',
					'Crypto-Pay-API-Token': str(self.api),
					'Content-Type': 'application/json',
				}

				url = 'https://pay.crypt.bot/api/getMe'
				resp = await Rest.get(url=url, headers=headers)

				return resp.json

			except Exception as e:
				traceback.print_exc()
				return 'cryptobot error'


		async def Balance(self):

			try:

				headers = {
					'accept': 'application/json',
					'Crypto-Pay-API-Token': str(self.api),
					'Content-Type': 'application/json',
				}

				url = 'https://pay.crypt.bot/api/getBalance'
				resp = await Rest.get(url=url, headers=headers)

				return resp.json

			except Exception as e:
				traceback.print_exc()
				return 'cryptobot error'





		# Invoice methods
		async def CreateInvoice(self, currency: str = '', amount: float = 0, description: str = '', hidden_message: str = '', paid_btn_name: str = '', paid_btn_url: str = '', payload: str = '', allow_comments: bool = False, allow_anonymous: bool = False, expires_in: int = 0):

			try:

				headers = {
					'accept': 'application/json',
					'Crypto-Pay-API-Token': str(self.api),
					'Content-Type': 'application/json',
				}

				data = {
					"asset": currency,
					"amount": str(amount),
					"description": description,
					"hidden_message": hidden_message,
					"paid_btn_name": paid_btn_name,
					"paid_btn_url": paid_btn_url,
					"payload": payload,
					"allow_comments": allow_comments,
					"allow_anonymous": allow_anonymous,
					"expires_in": expires_in
				}

				url = 'https://pay.crypt.bot/api/createInvoice'
				resp = await Rest.post(url=url, headers=headers, json=data)

				return resp.json

			except Exception as e:
				traceback.print_exc()
				return 'cryptobot error'


		async def InvoiceStatus(self, currency: str = '', invoice_ids: str = '', status: str = '', offset: int = 0, count: int = 0):

			try:

				headers = {
					'accept': 'application/json',
					'Crypto-Pay-API-Token': str(self.api),
					'Content-Type': 'application/json',
				}

				data = {
					"asset": currency,
					"invoice_ids": invoice_ids,
					"status": status,
					"offset": offset,
					"count": count
				}

				url = 'https://pay.crypt.bot/api/getInvoices'
				resp = await Rest.post(url=url, headers=headers, json=data)

				return resp.json

			except Exception as e:
				traceback.print_exc()
				return 'cryptobot error'





		# Transfer methods
		async def Transfer(self, user_id: int = 0, currency: str = '', amount: float = 0, spend_id: str = '', comment: str = '', disable_send_notification: bool = False):

			try:

				headers = {
					'accept': 'application/json',
					'Crypto-Pay-API-Token': str(self.api),
					'Content-Type': 'application/json',
				}

				data = {
					"user_id": user_id,
					"asset": currency,
					"amount": str(amount),
					"spend_id": spend_id,
					"comment": comment,
					"disable_send_notification": disable_send_notification
				}


				url = 'https://pay.crypt.bot/api/transfer'
				resp = await Rest.post(url=url, headers=headers, json=data)

				return resp.json

			except Exception as e:
				traceback.print_exc()
				return 'cryptobot error'




		# Exchange methods
		async def ExchangeRates(self):

			try:

				headers = {
					'accept': 'application/json',
					'Crypto-Pay-API-Token': str(self.api),
					'Content-Type': 'application/json',
				}

				url = 'https://pay.crypt.bot/api/getExchangeRates'
				resp = await Rest.get(url=url, headers=headers)

				return resp.json

			except Exception as e:
				traceback.print_exc()
				return 'cryptobot error'


		async def ExchangeRates(self, invoice_id: int = 0, status: str = '', hash: str = '', currency: str = '', amount: float = 0, fee: str = '', pay_url: str = '', description: str = '', created_at: str = '', usd_rate: str = '', allow_comments: bool = False, allow_anonymous: bool = False, expiration_date: str = '', paid_at: str = '', paid_anonymously: bool = False, comment: str = '', hidden_message: str = '', payload: str = '', paid_btn_name: str = '', paid_btn_url: str = ''):

			try:

				headers = {
					'accept': 'application/json',
					'Crypto-Pay-API-Token': str(self.api),
					'Content-Type': 'application/json',
				}

				data = {
					"invoice_id": invoice_id,
					"status": status,
					"hash": hash,
					"asset": currency,
					"amount": str(amount),
					"fee": fee,
					"pay_url": pay_url,
					"description": description,
					"created_at": created_at,
					"usd_rate": usd_rate,
					"allow_comments": allow_comments,
					"allow_anonymous": allow_anonymous,
					"expiration_date": expiration_date,
					"paid_at": paid_at,
					"paid_anonymously": paid_anonymously,
					"comment": comment,
					"hidden_message": hidden_message,
					"payload": payload,
					"paid_btn_name": paid_btn_name,
					"paid_btn_url": paid_btn_url
				}

				url = 'https://pay.crypt.bot/api/getCurrencies'
				resp = await Rest.get(url=url, headers=headers)

				return resp.json

			except Exception as e:
				traceback.print_exc()
				return 'cryptobot error'
