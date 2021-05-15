from discord import Embed, Color
from discord.ext import commands, tasks
from database import db_accessor


from datetime import datetime
import wikipediaapi as wikiapi
import asyncpg
import asyncio
import aiohttp
import requests
import json
import re


class web_crawler:
	def __init__(self, db: db_accessor):
		self.db = db
		self.loop = asyncio.get_event_loop()
		self.client = aiohttp.ClientSession(loop=self.loop)
		self.wiki = wikiapi.Wikipedia('en')
		self.MAX_CHAR = 170
		self.TRIM = [("*",""),("`",""),(">>> ",""),("  "," "),(" _"," "),("_ "," ")]
		self.QUOTES = []

	# trims string to fit maxlen, removes special symbols, accounts for hyperlinks
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

	# scans through links in database, if known API reads & outputs message
	async def view_links(self):
		messages = []
		for link in self.db.LINKS:
			if link.startswith("https://www.reddit.com"): out = await self.web_reddit(link)
			else: print(f'handler.read_link: link "{link}" does not match any known APIs!')
			for m in out: messages.append(m)
		return messages

	# reads & returns json of url
	async def web_json(self, url: str):
		async with self.client.get(url) as response:
			assert response.status == 200
			data = await response.read()
			return json.loads(data.decode('utf-8'))

	# reddit API, returns embed messages
	async def web_reddit(self, link: str):
		data = await self.web_json(link)['data']['children']
		sr = data[0]['data']['subreddit_name_prefixed']
		lst = [Embed(title=f"Reddit's top today: {sr}",\
			description = "", colour=Colour.orange())]

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
				lst.append(Embed(colour=Colour.orange(), description = tmp))
			else:
				lst[-1].description += tmp
		return lst

	# zenquotes API, returns str of quotes: https://premium.zenquotes.io/zenquotes-documentation/
	async def web_quote(self, cnt: int):
		print(self.web_json("https://zenquotes.io/api/quotes"))
		out = ""; cnt = min(cnt,15)
		if cnt==-1: # daily quote
			response = requests.get("https://zenquotes.io/api/today")
			self.QUOTES += json.loads(response.text)
		elif len(self.QUOTES) < cnt:
			response = requests.get("https://zenquotes.io/api/quotes")
			self.QUOTES += json.loads(response.text)

		for i in range(abs(cnt)):
			tmp = self.QUOTES.pop()
			out += '*"' + self.trim(tmp['q']) + '"* - **' + self.trim(tmp['a']) + '**\n'
		return out

	# wikipedia API: https://wikipedia-api.readthedocs.io/en/latest/README.html
	async def web_wiki(self, search: str, full: bool = False):
		search = search.replace(" ", "_")
		page = self.wiki.page(search, extract_format=wikiapi.ExtractFormat.WIKI)
		if not page.exists():
			return f'Wikipedia page "{search}" does not exist!'
		if full: desc = page.text
		else: desc = f'{page.summary[:200]}\n\n[More information]({page.fullurl})'
		out = Embed(title=page.title, description = self.trim(desc, 1900), colour=Colour.light_grey())
		return out


class MyCog(commands.Cog):
	def __init__(self, bot: commands.bot, web_bot: web_crawler, db: db_accessor):
		self.bot = bot
		self.web_bot = web_bot
		self.db = db
		self.lock = asyncio.Lock()
		self.daily_briefing.add_exception_type(asyncpg.PostgresConnectionError)
		self.daily_briefing.start()

	# daily briefing every 24h at set time
	@tasks.loop(hours=24.0, minutes = 0.0)
	async def daily_briefing(self, ctx = None):
		async with self.lock:
			if ctx == None:
				ctx = self.bot.get_guild(self.db.GUILD_ID).get_channel(self.db.DAILY_CHANNEL)
			await ctx.send("Your daily briefing up and coming!")
			messages = await self.web_bot.view_links()
			for m in messages:
				if isinstance(m, Embed): await ctx.send(embed = m)
				else: await ctx.send(m)

	# reads set-time for daily briefing, waits for that time
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
