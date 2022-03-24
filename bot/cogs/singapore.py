import discord
from discord import colour
from discord.ext import commands

from bot import *
import re
from disputils import BotEmbedPaginator


class SingaporeCog(commands.Cog):
	"""Singapore"""

	def __init__(self, bot: commands.bot):
		self.bot = bot
		self.mrt_initialise()


	@commands.group()
	async def mrt(self, ctx):
		pass


	@mrt.command()
	async def map(self, ctx):
		"""Singapore MRT Map."""
		embed = discord.Embed(title = "MRT Map")
		embed.add_field(name="MRT Lines",value='\n'.join(self.mrt_lines))
		embed.set_image(url=self.mrt_map)
		embed.set_footer(text="Use .mrt stations to list all stations")
		await p(ctx, embed)


	@mrt.command()
	async def line(self, ctx, *, inn: str):
		"""Search for Singapore MRT line."""
		indexes = closestMatchesIndexes(inn, self.mrt_lines)
		paginator = BotEmbedPaginator(ctx, [self.mrt_line_embeds[i] for i in indexes])
		await paginator.run(timeout = PAGINATOR_TIMEOUT)


	@mrt.command()
	async def station(self, ctx, *, inn: str):
		"""Search for Singapore MRT station."""
		stations = closestMatches(inn, self.mrt_stations, tol=0.8)[:50]
		embed = discord.Embed(title="Search results for: "+inn, description='\n'.join(stations))
		embed.set_footer(text="Use .mrt map to view MRT map")
		await p(ctx, embed)


	@mrt.command()
	async def stations(self, ctx):
		"""List of Singapore MRT stations."""
		paginator = BotEmbedPaginator(ctx, self.mrt_line_embeds)
		await paginator.run(timeout = PAGINATOR_TIMEOUT)


	def mrt_initialise(self):
		self.mrt_map = "https://www.sgtrains.com/img/network/systemmap_2020.png"
		self.mrt_lines = ["North South Line NSL", "East West Line EWL", "North East Line NEL", "Circle Line CCL", "Downtown Line DTL", "Thomson-East Coast Line TEL"]
		self.mrt_colors = [discord.Color.from_rgb(211,26,0), discord.Color.from_rgb(0,149,58), discord.Color.from_rgb(151,42,181), discord.Color.from_rgb(254,158,19), discord.Color.from_rgb(0,87,184), discord.Color.from_rgb(163,87,16)]
		self.mrt_stations = [] # for .mrt station
		self.mrt_line_embeds = [] # for .mrt stations

		with open('bot/data/singapore_mrt.txt') as f:
			for i, line in enumerate(f.readlines()):
				line = line.strip()
				codes = re.findall("[A-Z]+\d+", line)
				names = re.split("[A-Z]+\d+", line)[1:]
				fullnames = ""
				for j in range(len(codes)):
					fullnames += f'**``{codes[j]}``** {names[j]}'
					if names[j] != "": fullnames += '\n'

				self.mrt_stations += fullnames.split('\n')[:-1]
				embed = discord.Embed(
					title = self.mrt_lines[i],
					color = self.mrt_colors[i],
					description = fullnames
				).set_footer(text="Use .mrt station to a find specific station")
				self.mrt_line_embeds.append(embed)
