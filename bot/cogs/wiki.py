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
		self.section_regex = ' *=+[\dA-z, \(\)\-\+]+=+ *'
		self.DEFAULT_LANG = 'en'
		self.SUMMARY_LEN = 500
		self.PAGES = 9
		self.SEARCH_MAX = 36
		self.SEARCH_PER_PAGE = 6


	def _lang(self, s: str):
		"""If accepted language, else uses default"""
		if re.search('^[A-Z][A-Z\-]*[A-Z]$', s):
			return s.lower() # accepted language
		else:
			return self.DEFAULT_LANG


	@commands.command(usage=USAGES['wiki']['wiki'], aliases=ALIASES['wiki']['wiki'])
	async def wiki(self, ctx, *, search: str):
		"""Summary of Wikipedia page"""
		search = search.replace('_', ' ')
		lang = self._lang(search.split(' ')[-1])

		# search closest wiki page
		results = await self.web_wiki_search(search, lang)
		page_title = results[0][0]
		page_url = results[0][1]

		embeds = await self.web_wiki(page_url, page_title = page_title, lang = lang)
		paginator = BotEmbedPaginator(ctx, embeds)
		await paginator.run(timeout = 400)


	@wiki.error
	async def wiki_error(self, ctx, error):
		await badarguments(ctx, 'wiki', 'wiki')


	@commands.command(usage=USAGES['wiki']['wikisearch'], aliases=ALIASES['wiki']['wikisearch'])
	async def wikisearch(self, ctx, *, search: str):
		"""Top Wikipedia search results"""
		search = search.replace('_', ' ')
		lang = self._lang(search.split(' ')[-1])

		results = await self.web_wiki_search(search, lang)
		results = results[:self.SEARCH_MAX]
		embeds = []

		for page in range(0, len(results), self.SEARCH_PER_PAGE):
			# description of each embed
			desc = ""
			for title, url in results[page:page + self.SEARCH_PER_PAGE]:
				one_liner = await self.web_wiki_abstract(title, lang)
				desc += process_links(f'[**{trim(title)}**]({url} )') + '\n' + one_liner + '\n'

			embeds.append(
				discord.Embed(
					title = f"Search results for \"{search}\"",
					description = desc,
					color = discord.Colour.light_grey()
				)
				.set_author(name = "Wikipedia", icon_url = self.wiki_logo)
			)
		paginator = BotEmbedPaginator(ctx, embeds)
		await paginator.run(timeout = 400)


	@wikisearch.error
	async def wikisearch_error(self, ctx, error):
		await badarguments(ctx, 'wiki', 'wikisearch')


	# https://stackoverflow.com/questions/27193619/get-all-sections-separately-with-wikimedia-api
	# allow searching specific sections + listing out all sections.


	# retrieve 1-liner description of page
	async def web_wiki_abstract(self, page_title: str, lang: str):
		api_url = f'https://{lang}.wikipedia.org/w/api.php'
		params = {
			"action": "query",
			"format": "json",
			"titles": page_title,
			"prop": "pageprops"
		}
		try:
			json = await self.web_bot.web_json(api_url, params)
			json = json['query']['pages']
			# one_json.keys() has 1 item, being the pageid
			for i in json.keys(): json = json[i]['pageprops']
			one_liner = "*" + json['wikibase-shortdesc'] + "*\n"
		except:
			one_liner = ""
		return one_liner


	# wiki search results
	async def web_wiki_search(self, search: str, lang: str):
		api_url = f'https://{lang}.wikipedia.org/w/api.php'
		# get closest wiki page
		search = search.replace("_", "%20").replace("&", "%20")
		search_params = {
			"action": "opensearch",
			"format": "json",
			"search": search
		}
		search_json = await self.web_bot.web_json(api_url, params = search_params)
		# (title, url)
		results = [(search_json[1][i],search_json[3][i]) for i in range(len(search_json[1]))]
		return results


	# mediawiki API: https://github.com/mudroljub/wikipedia-api-docs
	async def web_wiki(self, page_url: str, page_title: str = None, lang: str = None, indiv_posts: bool = True):
		if lang == None:
			lang = page_url.split(".wikipedia.org/")[0][8:]
		if page_title == None:
			page_title = ' '.join([s.capitalize() for s in page_url.split(".wikipedia.org/wiki/")[1].split("_")])
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
		info_json = await self.web_bot.web_json(api_url, params = info_params)
		info_json = info_json['query']['pages']
		# info_json.keys() has 1 item, being the pageid
		for i in info_json.keys(): info_json = info_json[i]
		summary = trim(info_json['extract'], self.SUMMARY_LEN) # article summary
		if indiv_posts: page_info = trim(info_json['extract'], MAX_LEN * self.PAGES) # 'full' article

		# retrieving main image
		icon_params = {
			"action": "query",
			"format": "json",
			"titles": page_title,
			"prop": "pageimages",
			"pithumbsize": "500"
		}
		try:
			icon_json = await self.web_bot.web_json(api_url, params = icon_params)
			icon_json = icon_json['query']['pages']
			# icon_json.keys() has 1 item, being the pageid
			for i in icon_json.keys(): icon_json = icon_json[i]
			icon_url = icon_json['thumbnail']['source']
		except: icon_url = ""

		# retrieving 1-liner description
		one_liner = await self.web_wiki_abstract(page_title, lang)

		# formatting first embed (summary)
		embeds = [
			discord.Embed(
				title = page_title,
				url = page_url,
				description = one_liner + re.sub(" *=+ *","**\n", summary),
				color = discord.Colour.light_grey()
			)
			.set_thumbnail(url = icon_url)
			.set_author(name = "Wikipedia", icon_url = self.wiki_logo)
		]

		if indiv_posts:
			# split full page into multiple embeds
			paras = re.split(self.section_regex, page_info)
			sects = [""] + re.findall(self.section_regex, page_info)
			lst = [""]
			for para, sect in zip(paras, sects):
				end = min(MAX_LEN - len(lst[-1]), 0) # solve edge-case problem where char change from renaming section headers cause -ve end values and thus blank pages
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
