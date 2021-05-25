import discord
from discord.ext import commands, tasks
from database import db_accessor


from send import *
from datetime import datetime
import asyncpg
import asyncio
import aiohttp
import requests
import json


class web_crawler:
	def __init__(self, db: db_accessor):
		self.db = db
		self.loop = asyncio.get_event_loop()
		self.client = aiohttp.ClientSession(loop=self.loop)
		self.session = requests.Session()
		self.QUOTES = []

	# scans through links in database, if known API reads & outputs message
	async def view_links(self):
		messages = []
		for link in self.db.LINKS:
			if link.startswith("https://www.reddit.com"): out = await self.web_reddit(link)
			else: print(f'handler.read_link: link "{link}" does not match any known APIs!')
			for m in out: messages.append(m)
		return messages

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

	# reddit API, returns embed messages
	async def web_reddit(self, link: str):
		data = await self.web_json(link)
		data = data['data']['children']
		sr = data[0]['data']['subreddit_name_prefixed']
		lst = [discord.Embed(title=f"Reddit's top today: {sr}",\
			description = "", colour=discord.Colour.orange())]

		for i in data:
			link = "https://reddit.com" + i['data']['permalink'].strip()
			score = i['data']['score']
			comments = i['data']['num_comments']
			author = trim(i['data']['author'], 27)
			title = "**"+trim(i['data']['title'])+"**"
			desc = trim(i['data']['selftext'])

			tmp = f'[{title}]({link})\n'
			if desc != '': tmp += f'{desc}\n'
			tmp += f'Score: {score} Comments: {comments} Author: {author}\n\n'
			if len(lst[-1].description) + len(tmp) > 1900:
				lst[-1].description = lst[-1].description.strip()
				lst.append(discord.Embed(colour=discord.Colour.orange(), description = tmp))
			else:
				lst[-1].description += tmp
		return lst

	# zenquotes API, returns str of quotes: https://premium.zenquotes.io/zenquotes-documentation/
	async def web_quote(self, cnt: int):
		out = ""; cnt = min(cnt,15)
		if cnt==-1: # daily quote
			response = await self.web_json("https://zenquotes.io/api/today")
			self.QUOTES += response
		elif len(self.QUOTES) < cnt:
			response = await self.web_json("https://zenquotes.io/api/quotes")
			self.QUOTES += response

		for i in range(abs(cnt)):
			tmp = self.QUOTES.pop()
			out += '*"' + trim(tmp['q']) + '"* - **' + trim(tmp['a']) + '**\n'
		return out

	# formats url to find the REAL one; eg. Google_2015_logo.svg ->
	# https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Google_2015_logo.svg/2560px-Google_2015_logo.svg.png
	def wiki_icon_url(self, url: str, width: int = 0):
		if url.endswith('.svg'):
			lst = url.split('/')[-3:] # 3,32,Googleplex_HQ_%28cropped%29.jpg
			x = f'http://upload.wikimedia.org/wikipedia/commons/thumb/{lst[0]}/{lst[1]}/{lst[2]}/{width}px-{lst[2]}.png'
		else: x = url
		return x.replace(' ', '%20')

	# mediawiki API: https://www.mediawiki.org/wiki/API:Properties
	async def web_wiki(self, search: str, full: bool = False, lang: str = 'en'):
		embed = discord.Embed(color = discord.Colour.light_grey())
		api_url = f'https://{lang}.wikipedia.org/w/api.php'
		# search closest wiki page
		search = search.replace("_", " ")
		search_params = {
			"action": "opensearch",
			"format": "json",
			"search": search
		}
		search_json = await self.web_json(api_url, search_params)
		page_title = search_json[1][0] #[1][...] contains all related article title results
		page_url = search_json[3][0] #[3][...] contains all related article url results

		# retrieving page info
		info_params = {
			"action": "query",
			"format": "json",
			"titles": page_title, # "titles": "Category:Foo|Category:Infobox templates",
			"prop": "extracts", # "prop": "categoryinfo",
			"explaintext": "", # no html formatting
			"redirects": 1
		}
		if not full: info_params["exintro"] = "" # display summary
		info_json = await self.web_json(api_url, info_params)
		info_json = info_json['query']['pages']
		# info_json.keys() has 1 item, being the pageid
		for i in info_json.keys(): info_json = info_json[i]
		if not full: extract = trim(info_json['extract']) # summary article
		else: extract = trim(info_json['extract'], MAX_LEN) # 'full' article

		# retrieving page icon
		icon_params = {
			"action": "query",
			"format": "json",
			"titles": page_title,
			"prop": "pageimages",
			"piprop": "original"
		}
		icon_json = await self.web_json(api_url, icon_params)
		icon_json = icon_json['query']['pages']
		try:
			# icon_json.keys() has 1 item, being the pageid
			for i in icon_json.keys(): icon_json = icon_json[i]['original']
			icon_url = self.wiki_icon_url(icon_json['source'],icon_json['width'])
			embed.set_thumbnail(url=icon_url)
		except: icon_url = ""

		# retrieving 1-liner description
		one_params = {
			"action": "query",
			"format": "json",
			"titles": page_title,
			"prop": "pageprops"
		}
		one_json = await self.web_json(api_url, one_params)
		one_json = one_json['query']['pages']
		try:
			# one_json.keys() has 1 item, being the pageid
			for i in one_json.keys(): one_json = one_json[i]['pageprops']
			one_liner = one_json['wikibase-shortdesc']
		except: one_liner = ""

		# formatting to message
		if one_liner == "": desc = f'[**{page_title}**]({page_url})\n{extract}'
		else: desc = f'[**{page_title}**]({page_url})\n*{one_liner}*\n{extract}'
		embed.description = desc
		return embed


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
			out = ["Your daily briefing up and coming!"]
			out += await self.web_bot.view_links()
			await p(ctx, out)

	# reads set-time for daily briefing, waits for that time
	@daily_briefing.before_loop
	async def daily_briefing_before(self):
		print('Waiting for bot to connect...')
		await self.bot.wait_until_ready()
		print('Bot connected, cog now ready!')

		now = datetime.now(tz = self.db.tz)
		start = datetime(now.year, now.month, now.day, self.db.DAILY_TIME, 0, 0, 0, tzinfo=self.db.tz)
		delta = int((start-now).total_seconds()) % 86400
		# waiting seconds > 0, 86400 = days in seconds
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
