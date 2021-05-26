import json
import asyncio
import aiohttp
import requests


class web_accessor:
	def __init__(self):
		self.loop = asyncio.get_event_loop()
		self.client = aiohttp.ClientSession(loop=self.loop)
		self.session = requests.Session()

	# reads & returns json of url [aiohttp no params/requests with params]
	async def web_json(self, url: str, params = -1):
		if params == -1:
			async with self.client.get(url) as response:
				assert response.status == 200
				data = await response.read()
				return json.loads(data.decode('utf-8'))
		else:
			data = self.session.get(url=url, params=params)
			return data.json()
