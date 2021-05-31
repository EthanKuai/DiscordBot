import discord
from discord.ext import commands

from bot import *
import sys
import typing
import random


class UtilityCog(commands.Cog):
	def __init__(self, bot: commands.bot):
		self.bot = bot
		print(sys.argv[0] + ' being loaded!')

	# repeat command
	@commands.command()
	async def echo(self, ctx, cnt: typing.Optional[int] = 1,*,response):
		for i in range(min(cnt,5)):
			await ctx.send(response)

	# flips a coin cnt times
	@commands.command(aliases=['coin','2'])
	async def coin(self, ctx, cnt: typing.Optional[int] = 1):
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

		if cnt > 1: message += "\nTotal sum: **" + str(total) + "**"
		await p(ctx,message)

	# rolls a maxn sided nice cnt times
	@commands.command(aliases=['rng','random','dice'])
	async def rng(self, ctx, maxn: int, cnt: typing.Optional[int] = 1):
		message = ""
		total = 0

		for i in range(cnt):
			tmp = random.randint(0,maxn)
			message += str(tmp) + " "
			total += tmp

		if cnt > 1:
			message += "\nTotal sum: **" + str(total) + "**"
		await p(ctx,message)

	# latency test
	@commands.command()
	async def ping(self, ctx, precision: typing.Optional[int] = 3):
		await ctx.reply('Pong! Latency: {0}'.format(round(self.bot.latency, precision)))
