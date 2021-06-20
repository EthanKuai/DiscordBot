import discord
from discord.ext import commands

from bot import *
import sys

QUOTE_DAILY = {"today":-1, "daily":-1, "qotd":-1, "day":-1}

class QuoteCog(commands.Cog):
	"""Quotes"""

	def __init__(self, bot: commands.bot, web_bot: web_accessor):
		self.bot = bot
		self.web_bot = web_bot
		print(sys.argv[0] + ' being loaded!')
		self.QUOTES = []


	@commands.command(aliases=aliases['quote']['quote'], usage=usages['quote']['quote'])
	async def quote(self, ctx, cnt: text_or_int(QUOTE_DAILY) = 1):
		"""QOTD & random quotes to help you stay motivated! Powered by Zenquote."""
		out = await self.web_quote(cnt)
		if cnt == -1: out = "**Quote of the day**: " + out
		await p(ctx, out)


	@quote.error
	async def quote_error(self, ctx, error):
		await badarguments(ctx, 'quote', 'quote')


	# zenquotes API, returns str of quotes: https://premium.zenquotes.io/zenquotes-documentation/
	async def web_quote(self, cnt: int):
		out = ""; cnt = min(cnt,15)
		if cnt==-1: # daily quote
			response = await self.web_bot.web_json("https://zenquotes.io/api/today")
			self.QUOTES += response
		elif len(self.QUOTES) < cnt:
			response = await self.web_bot.web_json("https://zenquotes.io/api/quotes")
			self.QUOTES += response

		for i in range(abs(cnt)):
			tmp = self.QUOTES.pop()
			out += '*"' + trim(tmp['q']) + '"* - **' + trim(tmp['a']) + '**\n'
		return out
