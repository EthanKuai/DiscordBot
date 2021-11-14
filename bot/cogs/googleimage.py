import discord
from discord.ext import commands

from bot import *


class GImageCog(commands.Cog):
	"""Google Image Search"""

	def __init__(self, bot: commands.bot, db: db_accessor):
		self.bot = bot
		self.db = db

	@commands.command()
	async def command(self, ctx):
		await p(ctx, "hello world")
