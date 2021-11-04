import discord
from discord.ext import commands

from bot import *
import sys


class GnewsCog(commands.Cog):
	"""Google News"""

	def __init__(self, bot: commands.bot):
		self.bot = bot

	@commands.command(aliases=['gnews','googlenews'])
	async def gnews(self, ctx, *args):
		"""Fetch top news today."""
		await p(ctx, "there is supposed to be a news feeds")
