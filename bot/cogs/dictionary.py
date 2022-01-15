import discord
from discord.ext import commands

from bot import *
from disputils import BotEmbedPaginator
from requests.utils import requote_uri


class DictionaryCog(commands.Cog):
	"""Searches word meanings & synonyms with Merriam Webster!"""

	def __init__(self, bot: commands.bot, db: db_accessor, web_bot: web_accessor):
		self.bot = bot
		self.db = db
		self.web_bot = web_bot
		self.webster_logo = "https://merriam-webster.com/assets/mw/static/social-media-share/mw-logo-245x245@1x.png"
		self.default_thes_list = [[{'wd':'N.A.'}]]


	@commands.command(usage=USAGES['dictionary']['dictionary'], aliases=ALIASES['dictionary']['dictionary'])
	async def dictionary(self, ctx, *, search: str):
		"""Meanings of words & phrases, via Merriam Webster."""

		# if not valid word, will output nearest search terms
		search_url = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/" + self.web_bot.clean_inputs_for_urls(search)
		search_params = {"key": self.db.DICTAPI_DICT}
		search_json = await self.web_bot.web_json(search_url, params = search_params)

		if len(search_json)==0:
			# input search string is super off, no suggested search term
			await p(ctx, "No search results for term: " + search)
			return None
		elif "meta" in search_json[0]:
			# previously was a dictionary request (ie. input search string is valid)
			dict_json = search_json
		else:
			# dictionary, previously was a search instead of a dictionary request (ie. input search string is invalid)
			dict_url = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/" + search_json[0] # new search term
			dict_params = {"key": self.db.DICTAPI_DICT}
			dict_json = await self.web_bot.web_json(dict_url, params = dict_params)

		embeds = [
			discord.Embed(
				title = "Dictionary: " + dct['meta']['id'],
				url = requote_uri("https://www.merriam-webster.com/dictionary/" + dct['meta']['id']),
				color = discord.Colour.red(),
				description = '*'+dct['fl'].replace('*','\*')+'*'
			)
			.add_field(name = "Pronunciation", value = f"\u200b*{dct['hwi']['hw']}*", inline = True)
			.add_field(name = "Stems", value = '\u200b'+', '.join(dct['meta']['stems'])[:MAX_FIELD], inline = True)
			.add_field(
				name = "Definition",
				value = '\u200b'+'\n'.join([
					f"**{i+1}**	{j}" for i,j in enumerate(dct['shortdef'])
				])[:MAX_FIELD],
				inline = False
			)
			.set_author(name = "Merriam Webster", icon_url = self.webster_logo)
			for dct in dict_json
		]
		paginator = BotEmbedPaginator(ctx, embeds)
		await paginator.run(timeout = PAGINATOR_TIMEOUT)


	@dictionary.error
	async def dictionary_error(self, ctx, error):
		await badarguments(ctx, 'dictionary', 'dictionary')


	# for thesaurus function
	def _fn(self, dct: dict, index: str):
		return ', '.join([
			', '.join([i['wd'] for i in row])
			for row in dct['def'][0]['sseq'][0][0][1].get(index, self.default_thes_list)
		])[:MAX_FIELD]


	@commands.command(usage=USAGES['dictionary']['thesaurus'], aliases=ALIASES['dictionary']['thesaurus'])
	async def thesaurus(self, ctx, *, search: str):
		"""Synonyms, via Merriam Webster."""

		# if not valid word, will output nearest search terms
		search_url = "https://www.dictionaryapi.com/api/v3/references/thesaurus/json/" + self.web_bot.clean_inputs_for_urls(search)
		search_params = {"key": self.db.DICTAPI_THES}
		search_json = await self.web_bot.web_json(search_url, params = search_params)

		if len(search_json)==0:
			# input search string is super off, no suggested search term
			await p(ctx, "No search results for term: " + search)
			return None
		elif "meta" in search_json[0]:
			# previously was a thesaurus request (ie. input search string is valid)
			thes_json = search_json
		else:
			# thesaurus, previously was a search instead of a thesaurus request (ie. input search string is invalid)
			thes_url = "https://www.dictionaryapi.com/api/v3/references/thesaurus/json/" + search_json[0] # new search term
			thes_params = {"key": self.db.DICTAPI_THES}
			thes_json = await self.web_bot.web_json(thes_url, params = thes_params)

		embeds = [
			discord.Embed(
				title = "Thesaurus: " + dct['meta']['id'],
				url = requote_uri("https://www.merriam-webster.com/thesaurus/" + dct['meta']['id']),
				color = discord.Colour.red(),
				description = '*'+dct['fl'].replace('*','\*')+'*'
			)
			.add_field(name = "Stems", value = '\u200b'+', '.join(dct['meta']['stems']), inline = True)
			.add_field(
				name = "Definition",
				value = '\u200b'+'\n'.join([
					f"**{i+1}**	{j}" for i,j in enumerate(dct['shortdef'])
				])[:MAX_FIELD],
				inline = True
			)
			.add_field(name = "Synonymous Phrases", value = self._fn(dct,'phrase_list'), inline = True)
			.add_field(name = "Synonyms", value = '\u200b'+', '.join(dct['meta']['syns'][0])[:MAX_FIELD], inline = True)
			.add_field(name = "Anonyms", value = self._fn(dct,'near_list'), inline = True)
			.add_field(name = "Related Words", value = self._fn(dct,'rel_list'), inline = True)
			.set_author(name = "Merriam Webster", icon_url = self.webster_logo)
			for dct in thes_json
		]
		paginator = BotEmbedPaginator(ctx, embeds)
		await paginator.run(timeout = PAGINATOR_TIMEOUT)


	@thesaurus.error
	async def thesaurus_error(self, ctx, error):
		await badarguments(ctx, 'dictionary', 'thesaurus')
