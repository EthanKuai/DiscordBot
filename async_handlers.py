import asyncio
import aiohttp
import signal
import json
import os

import discord

class handler:
	def __init__(self):
		self.loop = asyncio.get_event_loop()
		self.client = aiohttp.ClientSession(loop=self.loop)
		self.LINK_CNT = int(os.environ['LINK_CNT'])
		get_links()

	def get_links():
		self.LINKS = []
		try:
			for i in range(self.LINK_CNT):
				self.LINKS.append(os.environ['LINK'+str(i)])
		except:
			print("Failed to get links")
			exit()

	def write_links(link):
		LINKS.append(link)
		try:
			os.environ['LINK'+str(self.LINK_CNT)] = link
			self.LINK_CNT += 1
			os.environ['LINK_CNT'] = str(self.LINK_CNT)
			print("write_links: Successfully wrote new link")
			return True
		except:
			print("write_links: Failed to write link to environmental variables")
			return False

	def daily(self):
		asyncio.ensure_future(self.read_links())
		self.loop.run_forever()

	async def read_links(self):
		for link in self.LINKS:
			data = await web_json(link)
			if link.startswith("https://www.reddit.com"): await web_reddit(data)
			else: print(f'read_link: link {link} does not math any known APIs!')

	async def web_json(self, url):
		async with self.client.get(url) as response:
			assert response.status == 200
			return await response.read()

	async def web_reddit(self, data):
		message = discord.embed(title='')
		jdata = json.loads(data.decode('utf-8'))
		for i in jdata['data']['children']:
			score = i['data']['score']
			title = i['data']['title']
			link = i['data']['url']
			print(f'web_reddit: score={score}, title={title}, link={link}')
