import discord
from discord.ext import commands

from bot import *
import sys
import typing
import random


class UtilityCog(commands.Cog):
	"""Utility"""

	def __init__(self, bot: commands.bot):
		self.bot = bot
		print(sys.argv[0] + ' being loaded!')


	@commands.command(usage=USAGES['utility']['echo'])
	async def echo(self, ctx, cnt: typing.Optional[int] = 1,*,response):
		"""Sends messages with content given."""
		for i in range(min(cnt,5)):
			await ctx.send(response)


	@commands.command(usage=USAGES['utility']['coin'], aliases=ALIASES['utility']['coin'])
	async def coin(self, ctx, cnt: typing.Optional[int] = 1):
		"""Flips a coin x times!"""
		message = ""
		total = 0

		if cnt < 100:
			yes = "yes "; no = "no "
		elif cnt < MAX_LEN:
			yes = "1 "; no = "0 "
		else:
			yes = ""; no = ""

		for i in range(cnt):
			if random.randint(0,1):
				message += yes
				total += 1
			else: message += no

		if cnt > 1: message += "\nTotal sum: **``" + str(total) + "``**"
		await p(ctx,message)


	@coin.error
	async def coin_error(self, ctx, error):
		await badarguments(ctx, 'utility', 'coin')


	@commands.command(usage=USAGES['utility']['rng'], aliases=ALIASES['utility']['rng'])
	async def rng(self, ctx, maxn: int, cnt: typing.Optional[int] = 1):
		"""Random Number Generator. Rolls x-sided dice y times."""
		message = ""
		total = 0

		for i in range(cnt):
			tmp = random.randint(0,maxn)
			message += str(tmp) + " "
			total += tmp

		if cnt > 1:
			message += "\nTotal sum: **``" + str(total) + "``**"
		await p(ctx,message)


	@rng.error
	async def rng_error(self, ctx, error):
		await badarguments(ctx, 'utility', 'rng')


	@commands.command(usage=USAGES['utility']['ping'])
	async def ping(self, ctx, precision: typing.Optional[int] = 3):
		"""Bot latency test."""
		await ctx.reply('Pong! Latency: {0}'.format(round(self.bot.latency, precision)))
