import asyncio
import aiohttp
import json
import os

import discord

class handler:
	def __init__(self):
		self.MAX_CHAR = 200
		self.loop = asyncio.get_event_loop()
		self.client = aiohttp.ClientSession(loop=self.loop)
		self.LINK_CNT = int(os.environ['LINK_CNT'])
		self.get_links()

	def get_links(self):
		self.LINKS = []
		try:
			for i in range(self.LINK_CNT):
				self.LINKS.append(os.environ['LINK'+str(i)])
		except:
			print("Failed to get links")
			exit()

	def write_links(self, link):
		self.LINKS.append(link)
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
		messages = []
		for link in self.LINKS:
			data = await self.web_json(link)
			if link.startswith("https://www.reddit.com"): messages.append(await self.web_reddit(data))
			else: print(f'handler.read_link: link "{link}" does not match any known APIs!')
		return messages

	async def web_json(self, url):
		async with self.client.get(url) as response:
			assert response.status == 200
			return await response.read()

	async def web_reddit(self, data):
		jdata = json.loads(data.decode('utf-8'))['data']['children']
		subreddit = jdata[0]['data']['subreddit_name_prefixed']
		message = discord.Embed(title=f"Reddit's top today: {subreddit}", colour=discord.Colour(0x3e038c))

		for i in jdata:
			title = "**"+i['data']['title'].strip()+"**"
			desc = i['data']['selftext'].strip()
			link = i['data']['url'].strip()
			score = i['data']['score'].strip()

			if len(desc) > self.MAX_CHAR: desc = desc[:self.MAX_CHAR-3]+"..."
			message.add_field(name=f'[{title}]({link})', value=desc, inline=False)
			print(f'web_reddit: score={score}, title={title}, link={link}')
		return message
