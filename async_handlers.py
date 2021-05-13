from logging import error
import discord
from discord.ext import commands, tasks


from datetime import datetime, timezone, timedelta
import asyncpg
import asyncio
import aiohttp
import json
import os
import re


class web_crawler:
	def __init__(self):
		self.MAX_CHAR = 170
		self.loop = asyncio.get_event_loop()
		self.client = aiohttp.ClientSession(loop=self.loop)
		self.LINK_CNT = int(os.environ['LINK_CNT'])
		self.read_links()

	def trim(self, s: str, maxlen: int = -1):
		if maxlen == -1: maxlen = self.MAX_CHAR # not allowed in header :(
		out = ''
		s = re.split(';\n', s.strip())
		for ss in s:
			ss = ss.strip()
			if ss == '' or ss == '&gt' or ss == '&amp': continue # reddit formatting
			if ss[0] == '#' and len(ss) == 6: continue # color code
			maxlen -= len(ss) + 1
			if maxlen >= -1:
				out += ss + ' '
			else:
				out += ss[:maxlen]
				break
		if maxlen >= -1: out = out[:-1]
		else: out = out[:-3] + "..."
		return out

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
		description = ""

		for i in jdata:
			link = "https://reddit.com" + i['data']['permalink'].strip()
			score = i['data']['score']
			comments = i['data']['num_comments']
			author = self.trim(i['data']['author'], 27)
			title = self.trim("**"+i['data']['title'])+"**"
			desc = self.trim(i['data']['selftext'])
			subreddit = i['data']['subreddit_name_prefixed']

			description += f'[{title}]({link})\n'
			if desc != '': description += f'{desc}\n'
			description += f'Score: {score} Comments: {comments} Author: {author}\n\n'

		message = discord.Embed(title=f"Reddit's top today: {subreddit}",\
			description = description.strip(), colour=discord.Colour(0x3e038c))
		return message


class MyCog(commands.Cog):
	def __init__(self, bot: commands.bot, web_bot: web_crawler, GUILDID: int, CHANNELID: int, TIME: int):
		self.bot = bot
		self.web_bot = web_bot
		self.GUILDID = GUILDID
		self.CHANNELID = CHANNELID
		self.TIME = TIME
		self.tz = timezone(timedelta(hours=8))

		self.lock = asyncio.Lock()
		self.daily_briefing.add_exception_type(asyncpg.PostgresConnectionError)
		self.daily_briefing.start()

	@tasks.loop(hours=24.0, minutes = 0.0)
	async def daily_briefing(self):
		await self.db_channel.send("Your daily briefing up and coming!")
		async with self.lock:
			messages = await self.web_bot.view_links()
		for m in messages:
			await self.db_channel.send(embed = m)

	@daily_briefing.before_loop
	async def daily_briefing_before(self):
		print('Waiting for bot to connect...')
		await self.bot.wait_until_ready()
		print('Bot connected, cog now ready!')

		today = datetime.now(tz = self.tz)
		start = datetime(today.year, today.month, today.day, self.TIME, 0, 0, 0, tzinfo=self.tz)
		delta = int((start-today).total_seconds())
		if delta < 0: delta += 86400
		print(f'cog waiting for {delta} seconds')
		await asyncio.sleep(delta)
		self.db_channel = self.bot.get_guild(self.GUILDID).get_channel(self.CHANNELID)


	@daily_briefing.after_loop
	async def daily_briefing_cancel(self):
		if self.daily_briefing.is_being_cancelled():
			#do sth
			pass

	@daily_briefing.error
	async def error_handle(self,err0r):
		pass

	def cog_unload(self):
		self.daily_briefing.cancel()
