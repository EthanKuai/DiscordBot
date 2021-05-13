import discord
from discord.ext import commands, tasks
from database import db_accessor


from datetime import datetime, timezone, timedelta
import asyncpg
import asyncio
import aiohttp
import json
import re


class web_crawler:
	def __init__(self, db: db_accessor):
		self.MAX_CHAR = 170
		self.db = db
		self.loop = asyncio.get_event_loop()
		self.client = aiohttp.ClientSession(loop=self.loop)
		self.TRIM = [("*",""),("`",""),(">>> ",""),("  "," "),(" _"," "),("_ "," ")]

	def trim(self, s: str, maxlen: int = -1):
		if maxlen == -1: maxlen = self.MAX_CHAR # not allowed in header :(
		out = ''
		for i in self.TRIM: s = s.replace(i[0],i[1])
		s = re.split(';|\n', s.strip())
		for ss in s:
			if maxlen < 0:
				print('theres something wrong!!!')
				exit()
			ss = ss.strip()
			if ss == '' or ss == '&gt' or ss == '&amp': continue # reddit formatting
			if ss[0] == '#' and len(ss) == 6: continue # color code
			maxlen -= len(ss) + 1
			if maxlen >= -1:
				out += ss + ' '
			elif maxlen > -7:
				out += ss[:maxlen]
				break
			else:
				index = ss[:max(-1,maxlen+6)].find("](http")
				if index != -1:
					out += ss[:index + 1 + ss[index:].find(")")]
					maxlen = 0
				else: out += ss[:maxlen]
				break
		if maxlen < -1: out = out[:-3] + "..."
		return out.strip().replace("  "," ")

	async def view_links(self):
		messages = []
		for link in self.db.LINKS:
			if link.startswith("https://www.reddit.com"): out = await self.web_reddit(link)
			else: print(f'handler.read_link: link "{link}" does not match any known APIs!')
			for m in out: messages.append(m)
		return messages

	async def web_json(self, url: str):
		async with self.client.get(url) as response:
			assert response.status == 200
			return await response.read()

	async def web_reddit(self, link: str):
		data = await self.web_json(link)
		data = json.loads(data.decode('utf-8'))['data']['children']
		sr = data[0]['data']['subreddit_name_prefixed']
		lst = [discord.Embed(title=f"Reddit's top today: {sr}",\
			description = "", colour=discord.Colour.orange())]

		for i in data:
			link = "https://reddit.com" + i['data']['permalink'].strip()
			score = i['data']['score']
			comments = i['data']['num_comments']
			author = self.trim(i['data']['author'], 27)
			title = "**"+self.trim(i['data']['title'])+"**"
			desc = self.trim(i['data']['selftext'])

			tmp = f'[{title}]({link})\n'
			if desc != '': tmp += f'{desc}\n'
			tmp += f'Score: {score} Comments: {comments} Author: {author}\n\n'
			if len(lst[-1].description) + len(tmp) > 1900:
				lst[-1].description = lst[-1].description.strip()
				lst.append(discord.Embed(colour=discord.Colour.orange(), description = tmp))
			else:
				lst[-1].description += tmp
		return lst


class MyCog(commands.Cog):
	def __init__(self, bot: commands.bot, web_bot: web_crawler, db: db_accessor):
		self.bot = bot
		self.web_bot = web_bot
		self.db = db
		self.lock = asyncio.Lock()
		self.daily_briefing.add_exception_type(asyncpg.PostgresConnectionError)
		self.daily_briefing.start()

	@tasks.loop(hours=24.0, minutes = 0.0)
	async def daily_briefing(self, ctx = None):
		async with self.lock:
			if ctx == None:
				ctx = self.bot.get_guild(self.db.GUILD_ID).get_channel(self.db.DAILY_CHANNEL)
			await ctx.send("Your daily briefing up and coming!")
			messages = await self.web_bot.view_links()
			for m in messages:
				await ctx.send(embed = m)

	@daily_briefing.before_loop
	async def daily_briefing_before(self):
		print('Waiting for bot to connect...')
		await self.bot.wait_until_ready()
		print('Bot connected, cog now ready!')

		today = datetime.now(tz = self.db.tz)
		start = datetime(today.year, today.month, today.day, self.db.DAILY_TIME, 0, 0, 0, tzinfo=self.db.tz)
		delta = int((start-today).total_seconds())
		if delta < 0: delta += 86400
		print(f'cog waiting for {delta} seconds')
		await asyncio.sleep(delta)
		print('cog done waiting!')


	@daily_briefing.after_loop
	async def daily_briefing_cancel(self):
		if self.daily_briefing.is_being_cancelled():
			pass

	@daily_briefing.error
	async def error_handle(self,error):
		print(f'MyCog: error {error}')
		pass

	def cog_unload(self):
		self.daily_briefing.cancel()
