import discord
from discord.ext import commands

from bot import *
import sys


class RedditCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		print(sys.argv[0] + ' being loaded!')

	@commands.command()
	async def command(self, ctx):
		await p(ctx, "hello world")
