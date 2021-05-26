import discord
from discord.ext import commands, tasks


from bot.database import *
from bot.send import *
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
		lst = [discord.Embed(title=f"Reddit's top: {sr}",\
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

	# wiki search results
	async def web_wiki_search(self, search: str, is_embed: bool = True, lang: str = 'en'):
		api_url = f'https://{lang}.wikipedia.org/w/api.php'
		# search closest wiki page
		search = search.replace("%20", " ").replace("_", " ")
		search_params = {
			"action": "opensearch",
			"format": "json",
			"search": search
		}
		search_json = await self.web_json(api_url, search_params)
		lst = [(search_json[1][i],search_json[3][i]) for i in range(len(search_json[1]))]
		#[1][...] contains all related article title results
		#[3][...] contains all related article url results
		if is_embed:
			desc = ""
			for i in range(min(len(lst),10)):
				desc += f'[**{trim(lst[i][0])}**]({lst[i][1]})\n'
			embed = discord.Embed(description = desc, color = discord.Colour.light_grey())
			embed.title = f'Wiki search results for: {search}'
			return embed
		else: return lst

	# mediawiki API: https://github.com/mudroljub/wikipedia-api-docs
	async def web_wiki(self, search: str, full: bool = False, lang: str = 'en'):
		embed = discord.Embed(color = discord.Colour.light_grey())
		api_url = f'https://{lang}.wikipedia.org/w/api.php'

		# search closest wiki page
		results = await self.web_wiki_search(search, False, lang)
		page_title = results[0][0]
		page_url = results[0][1]

		# retrieving page info
		info_params = {
			"action": "query",
			"format": "json",
			"titles": page_title, # "titles": "Category:Foo|Category:Infobox templates",
			"prop": "extracts", # "prop": "categoryinfo",
			"explaintext": "", # no html formatting
			"redirects": 1
		}
		if not full: info_params["exintro"] = "1" # display summary
		info_json = await self.web_json(api_url, info_params)
		info_json = info_json['query']['pages']
		# info_json.keys() has 1 item, being the pageid
		for i in info_json.keys(): info_json = info_json[i]
		if not full: extract = trim(info_json['extract'],450) # summary article
		else: extract = trim(info_json['extract'], MAX_LEN) # 'full' article

		# retrieving page icon
		icon_params = {
			"action": "query",
			"format": "json",
			"titles": page_title,
			"prop": "pageimages",
			"pithumbsize": "500"
		}
		icon_json = await self.web_json(api_url, icon_params)
		icon_json = icon_json['query']['pages']
		try:
			# icon_json.keys() has 1 item, being the pageid
			for i in icon_json.keys(): icon_json = icon_json[i]
			icon_url = icon_json['thumbnail']['source']
			if full: embed.set_image(url=icon_url)
			else: embed.set_thumbnail(url=icon_url)
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
