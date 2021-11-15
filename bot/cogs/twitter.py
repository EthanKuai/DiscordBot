import discord
from discord.ext import commands

from bot import *
import sys
import twint


class TwitterCog(commands.Cog):
	"""Twitter API"""

	def __init__(self, bot: commands.bot, web_bot: web_accessor):
		self.bot = bot
		self.web_bot = web_bot
		self.c = twint.Config()

	@commands.command()
	async def twitter(self, ctx, *, username: str):
		out = await self.web_twitter(username)
		await p(ctx, out)

	async def web_twitter(self, user: str, limit: int = 5, search: str = None):
		self.c.Username = user
		self.c.Limit = limit
		self.c.Store_csv = False
		#self.c.Output = "none.csv"
		self.c.Lang = "en"
		#self.c.Translate = True
		#self.c.TranslateDest = "it"
		#self.c.Custom["tweet"] = ["id"]
		#self.c.Custom["user"] = ["bio"]
		if search != None: self.c.Search = search

		out = twint.run.Search(self.c)
		print(out)
