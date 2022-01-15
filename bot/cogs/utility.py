import discord
from discord.ext import commands

from bot import *
import sys
import typing
import random
from numpy.random import normal
from math import sqrt
from datetime import datetime as dt


class UtilityCog(commands.Cog):
	"""Utility"""

	def __init__(self, bot: commands.bot, db: db_accessor):
		self.bot = bot
		self.db = db


	@commands.command(usage=USAGES['utility']['echo'])
	async def echo(self, ctx, cnt: typing.Optional[int] = 1, *, response: str):
		"""Sends messages with content given."""
		for i in range(min(cnt,5)):
			await ctx.send(response)


	@commands.command(usage=USAGES['utility']['coin'], aliases=ALIASES['utility']['coin'])
	async def coin(self, ctx, cnt: typing.Optional[int] = 1):
		"""Flips a coin x times!"""
		if cnt < MAX_LEN:
			message = ""
			total = 0
			if cnt < 128:
				yes = "yes "; no = "no "
			else:
				yes = "1"; no = "0"

			for i in range(cnt):
				if random.randint(0,1):
					message += yes
					total += 1
				else: message += no

			if cnt > 1: message += "\nTotal sum: **``" + str(total) + "``**"

		else:
			total = int(normal(cnt*0.5, 0.5/sqrt(cnt), 1))
			message = "Total sum: **``" + str(total) + "``**"

		await p(ctx,message)


	@coin.error
	async def coin_error(self, ctx, error):
		await badarguments(ctx, 'utility', 'coin')


	@commands.command(usage=USAGES['utility']['rng'], aliases=ALIASES['utility']['rng'])
	async def rng(self, ctx, maxn: int, cnt: typing.Optional[int] = 1):
		"""Random Number Generator. Rolls x-sided dice y times."""
		if cnt < MAX_LEN:
			message = ""
			total = 0

			for i in range(cnt):
				tmp = random.randint(0,maxn)
				message += str(tmp) + " "
				total += tmp

			if cnt > 1: message += "\nTotal sum: **``" + str(total) + "``**"

		else:
			total = int(maxn * normal(cnt*0.5, 0.5/sqrt(cnt), 1))
			message = "Total sum: **``" + str(total) + "``**"

		await p(ctx,message)


	@rng.error
	async def rng_error(self, ctx, error):
		await badarguments(ctx, 'utility', 'rng')


	@commands.command(usage=USAGES['utility']['ping'])
	async def ping(self, ctx, precision: typing.Optional[int] = 3):
		"""Bot latency test."""
		await ctx.reply('Pong! Latency: {0}'.format(round(self.bot.latency, max(precision, 10))))


	@commands.command()
	async def timezones(self, ctx):
		"""Lists all timezones."""
		desc = ""
		for name, offset in TZ_DICT.items():
			if offset > 0: desc += f"**{name}** (UTC+{offset}), "
			elif offset == 0: desc += f"**{name}** (UTC), "
			else: desc += f"**{name}** (UTC{offset}), "
		out = discord.Embed(
			title = "Timezones",
			description = desc[:-2],
			colour = discord.Colour.gold()
		)
		await p(ctx, out)


	@commands.command(aliases=ALIASES['utility']['day'])
	async def day(self, ctx):
		"""Day of the year."""
		now = dt.now(tz=self.db.tz)
		s = now.strftime("%A, %d %B %Y, at %H:%M:%S") # Saturday, 1 January 2022, at 20:12:13

		day = now.timetuple().tm_yday # day of year

		year = now.year
		_ = (year % 400 == 0 and year % 100 == 0) or (year % 4 == 0 and year % 100 != 0) # leapyear
		pcg = ( 1- day/(364+_) ) * 100 # % left of year

		out = f"It is currently {s} (Timezone {self.db.tz})\n It is **Day {day}** of the year, with **{pcg:.2f}%** of the year left to go. 💪💪"
		await p(ctx, out)
