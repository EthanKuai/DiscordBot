import discord
from discord.ext import commands

from bot import *
import re
from disputils import BotEmbedPaginator


class WikiCog(commands.Cog):
	"""Wikipedia"""

	def __init__(self, bot: commands.bot, web_bot: web_accessor):
		self.bot = bot
		self.web_bot = web_bot
		self.wiki_logo = "https://upload.wikimedia.org/wikipedia/commons/6/63/Wikipedia-logo.png"
		self.default_lang = 'en'
		self.summary_length = 500
		self.pages = 9


	def _lang(self, s: str):
		"""If accepted language, else uses default"""
		if re.search('^[A-Z][A-Z\-]*[A-Z]$', s):
			return s.lower() # accepted language
		else:
			return self.default_lang


	@commands.command(usage=USAGES['wiki']['wiki'], aliases=ALIASES['wiki']['wiki'])
	async def wiki(self, ctx, *, search: str):
		"""Summary of Wikipedia page"""
		search = search.replace('_', ' ')
		lang = self._lang(search.split(' ')[-1])

		# search closest wiki page
		results = await self.web_wiki_search(search, lang, False)
		page_title = results[0][0]
		page_url = results[0][1]

		embeds = await self.web_wiki(page_title, page_url, lang)
		paginator = BotEmbedPaginator(ctx, embeds)
		await paginator.run()


	@commands.command(usage=USAGES['wiki']['wikisearch'], aliases=ALIASES['wiki']['wikisearch'])
	async def wikisearch(self, ctx, *, search: str):
		"""Top Wikipedia search results"""
		search = search.replace('_', ' ')
		lang = self._lang(search.split(' ')[-1])

		out = await self.web_wiki_search(search, lang)
		await p(ctx, out)


	# https://stackoverflow.com/questions/27193619/get-all-sections-separately-with-wikimedia-api
	# allow searching specific sections + listing out all sections.
	# 1-line abstract when searching, create function for that


	# wiki search results
	async def web_wiki_search(self, search: str, lang: str, is_embed: bool = True):
		api_url = f'https://{lang}.wikipedia.org/w/api.php'
		# get closest wiki page
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
	async def web_wiki(self, page_title: str, page_url: str, lang: str):
		api_url = f'https://{lang}.wikipedia.org/w/api.php'

		# retrieving page info
		info_params = {
			"action": "query",
			"format": "json",
			"titles": page_title, # "titles": "Category:Foo|Category:Infobox templates",
			"prop": "extracts", # "prop": "categoryinfo",
			"explaintext": "", # no html formatting
			"redirects": 1
		}
		info_json = await self.web_bot.web_json(api_url, info_params)
		info_json = info_json['query']['pages']
		# info_json.keys() has 1 item, being the pageid
		for i in info_json.keys(): info_json = info_json[i]
		abstract = trim(info_json['extract'], self.summary_length) # summary
		page_info = trim(info_json['extract'], MAX_LEN * self.pages) # 'full' article

		# retrieving page icon
		icon_params = {
			"action": "query",
			"format": "json",
			"titles": page_title,
			"prop": "pageimages",
			"pithumbsize": "500"
		}
		try:
			icon_json = await self.web_bot.web_json(api_url, icon_params)
			icon_json = icon_json['query']['pages']
			# icon_json.keys() has 1 item, being the pageid
			for i in icon_json.keys(): icon_json = icon_json[i]
			icon_url = icon_json['thumbnail']['source']
		except: icon_url = ""

		# retrieving 1-liner description
		one_params = {
			"action": "query",
			"format": "json",
			"titles": page_title,
			"prop": "pageprops"
		}
		try:
			one_json = await self.web_bot.web_json(api_url, one_params)
			one_json = one_json['query']['pages']
			# one_json.keys() has 1 item, being the pageid
			for i in one_json.keys(): one_json = one_json[i]['pageprops']
			one_liner = "*" + one_json['wikibase-shortdesc'] + "*\n"
		except: one_liner = ""

		# formatting first embed (abstract)
		embeds = [
			discord.Embed(
				title = page_title,
				url = page_url,
				description = one_liner + re.sub(" *=+ *","**\n", abstract),
				color = discord.Colour.light_grey()
			)
			.set_thumbnail(url = icon_url)
			.set_author(name = "Wikipedia", icon_url = self.wiki_logo)
		]

		# split full page into multiple embeds
		paras = re.split(' *=+[A-z ]+=+ *', page_info)
		sects = [""] + re.findall(' *=+[A-z ]+=+ *', page_info)
		lst = [""]
		for para, sect in zip(paras, sects):
			end = MAX_LEN - len(lst[-1])
			lst[-1] += re.sub(" *=+ *","**\n", sect)
			lst[-1] += para[:end]
			if end <= len(para):
				lst += [para[i:MAX_LEN+i] for i in range(end, len(para), MAX_LEN)]

		# add other embeds (full wiki page)
		embeds += [
			discord.Embed(description = x, color = discord.Colour.light_grey())
			.set_author(name = "Wikipedia: " + page_title, icon_url = self.wiki_logo, url = page_url)
			.set_image(url=icon_url)
			for x in lst
		]
		return embeds
