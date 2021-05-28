import discord
from discord.ext import commands

from bot import *
import sys


class WikiCog(commands.Cog):
	def __init__(self, bot: commands.bot, web_bot: web_accessor):
		self.bot = bot
		self.web_bot = web_bot
		print(sys.argv[0] + ' being loaded!')

	@commands.command()
	async def wiki(self, ctx, *, search):
		search = search.split(' ')
		if search[0] == 'search':
			out = await self.web_wiki_search(' '.join(search[1:]))
		elif search[-1] == 'search':
			out = await self.web_wiki_search(' '.join(search[:-1]))
		elif search[0] == 'full':
			out = await self.web_wiki(' '.join(search[1:]), True)
		elif search[-1] == 'full':
			out = await self.web_wiki(' '.join(search[:-1]), True)
		else:
			out = await self.web_wiki(' '.join(search))
		await p(ctx, out)

	# wiki search results
	async def web_wiki_search(self, search: str, is_embed: bool = True, /, lang: str = 'en'):
		api_url = f'https://{lang}.wikipedia.org/w/api.php'
		# search closest wiki page
		search = search.replace("%20", " ").replace("_", " ")
		search_params = {
			"action": "opensearch",
			"format": "json",
			"search": search
		}
		search_json = await self.web_bot.web_json(api_url, search_params)
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
	async def web_wiki(self, search: str, full: bool = False, /, lang: str = 'en'):
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
		info_json = await self.web_bot.web_json(api_url, info_params)
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
		icon_json = await self.web_bot.web_json(api_url, icon_params)
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
		one_json = await self.web_bot.web_json(api_url, one_params)
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
