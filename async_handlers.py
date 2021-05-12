import discord
from discord.ext import commands, tasks


import asyncpg
import asyncio
import aiohttp
import json
import os
import datetime


class web_crawler:
	def __init__(self):
		self.MAX_CHAR = 250
		self.loop = asyncio.get_event_loop()
		self.client = aiohttp.ClientSession(loop=self.loop)
		self.LINK_CNT = int(os.environ['LINK_CNT'])
		self.read_links()

	def trim(self, s: str, maxlen = -1):
		if maxlen == -1: maxlen = self.MAX_CHAR # not allowed in header :(
		if len(s) > maxlen: s = s[:maxlen-3]+"..."
		#elif len(s) == 0: s = '\u200b' # discord.Embed fuzzyness
		return s

	def read_links(self):
		self.LINKS = []
		try:
			for i in range(self.LINK_CNT):
				self.LINKS.append(os.environ['LINK'+str(i)])
		except:
			print("Failed to get links")
			exit()

	def write_links(self, link: str):
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

	async def view_links(self):
		messages = []
		for link in self.LINKS:
			data = await self.web_json(link)
			if link.startswith("https://www.reddit.com"): messages.append(await self.web_reddit(data))
			else: print(f'handler.read_link: link "{link}" does not match any known APIs!')
		return messages

	async def web_json(self, url: str):
		async with self.client.get(url) as response:
			assert response.status == 200
			return await response.read()

	async def web_reddit(self, data):
		jdata = json.loads(data.decode('utf-8'))['data']['children']
		subreddit = jdata[0]['data']['subreddit_name_prefixed']
		message = discord.Embed(title=f"Reddit's top today: {subreddit}", colour=discord.Colour(0x3e038c))
		description = ""

		for i in jdata:
			link = "https://reddit.com" + i['data']['permalink'].strip()
			score = i['data']['score']
			title = self.trim("**"+i['data']['title'].strip()+"**")
			desc = self.trim(i['data']['selftext'].strip())
			moreinfo = i['data']['url'].strip()
			#print(f'web_reddit: score={score}, title={title}, link={link}')
			if desc == '':
				#message.add_field(name=f'[{title}]({link})', value=f'Score: {score}', inline=False)
				description = f'[{title}]({link})\nScore: {score}\n'
			else:
				#message.add_field(name=f'[{title}]({link})', value=f'{desc}\nScore: {score}', inline=False)
				description = f'[{title}]({link})\n{desc}\nScore: {score}\n'
		message.description = description.strip()
		return message


class MyCog(commands.Cog):
	def __init__(self, bot: commands.bot, web_bot: web_crawler, GUILDID: int, CHANNELID: int):
		self.bot = bot
		self.web_bot = web_bot
		self.GUILDID = GUILDID
		self.CHANNELID = CHANNELID
		self.lock = asyncio.Lock()
		self.daily_briefing.add_exception_type(asyncpg.PostgresConnectionError)
		self.daily_briefing.start()

	@tasks.loop(hours=24.0, minutes = 0.0)
	async def daily_briefing(self):
		await self.channel_db.send("Your daily briefing up and coming!")
		#loop.run_until_complete(asyncio.gather(self.view_links_async()))
		messages = await self.web_bot.view_links()
		for m in messages:
			await self.channel_db.send(embed = m)

	@daily_briefing.before_loop
	async def daily_briefing_before(self):
		print('Waiting for bot to connect...')
		await self.bot.wait_until_ready()
		print('Bot connected, cog now ready!')
		self.channel_db = self.bot.get_guild(self.GUILDID).get_channel(self.CHANNELID)

	@daily_briefing.after_loop
	async def daily_briefing_cancel(self):
		if self.daily_briefing.is_being_cancelled():
			#do sth
			pass

	def cog_unload(self):
		self.daily_briefing.cancel()
