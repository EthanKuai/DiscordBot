import discord
from discord.ext import commands

from bot import *
import sys


class TemplateCog(commands.Cog):
	def __init__(self, bot: commands.bot):
		self.bot = bot

	@commands.command()
	async def command(self, ctx):
		await p(ctx, "hello world")
