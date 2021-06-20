import discord
from discord import colour
from discord.ext import commands

from bot import *
import sys
import re


class SingaporeCog(commands.Cog):
	"""Singapore"""

	def __init__(self, bot: commands.bot):
		self.bot = bot
		print(sys.argv[0] + ' being loaded!')
		self.mrt_initialise()


	@commands.group()
	async def mrt(self, ctx):
		pass


	@mrt.command()
	async def map(self, ctx):
		"""Singapore MRT Map."""
		await p(ctx, self.mrt_map)


	@mrt.command()
	async def line(self, ctx, *, inn: str):
		"""Search for Singapore MRT line."""
		i, line = closestMatch(inn, self.mrt_lines)
		embed = discord.Embed(title = line, color = self.mrt_colors[i])
		embed.description = '\n'.join(self.mrt_stations[i])
		await p(ctx, embed)


	@mrt.command()
	async def station(self, ctx, *, inn: str):
		"""Search for Singapore MRT station."""
		stations = []
		for x in self.mrt_stations:
			for i in x:
				stations += [i.replace('*','')]
		i, station = closestMatch(inn, stations)
		embed = discord.Embed(title = station)
		await p(ctx, embed)


	@mrt.command()
	async def stations(self, ctx, *, inn: str):
		"""List of Singapore MRT stations."""
		stations = []
		for x in self.mrt_stations:
			stations += x
		i, station = closestMatch(inn, stations)
		embed = discord.Embed(title = station)
		await p(ctx, embed)


	def mrt_initialise(self):
		self.mrt_map = "https://www.sgtrains.com/img/network/systemmap_2020.png"
		self.mrt_lines = ["North South Line NSL", "East West Line EWL", "North East Line NEL", "Circle Line CCL", "Downtown Line DTL", "Thomson-East Coast Line TEL"]
		self.mrt_colors = [discord.Color.from_rgb(211,26,0), discord.Color.from_rgb(0,149,58), discord.Color.from_rgb(151,42,181), discord.Color.from_rgb(254,158,19), discord.Color.from_rgb(0,87,184), discord.Color.from_rgb(163,87,16)]
		self.mrt_stations = []

		with open('bot/data/singapore_mrt.txt') as f:
			for line in f.readlines():
				line = line.strip()
				codes = re.findall("[A-Z]+\d+", line)
				names = re.split("[A-Z]+\d+", line)[1:]
				fullnames = ""
				for i in range(len(codes)):
					fullnames += f'**``{codes[i]}``** {names[i]}'
					if names[i] != "": fullnames += '\n'
				self.mrt_stations += [fullnames.split('\n')[:-1]]
