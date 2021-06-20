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
		await p(ctx, self.mrt_map)


	@mrt.command()
	async def lines(self, ctx):
		i, line = closestMatch(ctx, self.mrt_lines)
		embed = discord.Embed(title = line, color = self.mrt_colors[i])
		embed.description = '\n'.join(self.mrt_stations[i])
		await p(ctx, embed)


	@mrt.command()
	async def stations(self, ctx):
		stations = []
		for x in self.mrt_stations: stations += x
		i, station = closestMatch(ctx, stations)
		embed = discord.Embed(title = station)
		await p(ctx, embed)


	def mrt_initialise(self):
		self.mrt_map = "https://www.sgtrains.com/img/network/systemmap_2020.png"
		self.mrt_lines = ["North South Line NSL", "East West Line EWL", "North East Line NEL", "Circle Line CCL", "Downtown Line DTL", "Thomson-East Coast Line TEL"]
		self.mrt_colors = [discord.Color.from_rgb(211,26,0), discord.Color.from_rgb(0,149,58), discord.Color.from_rgb(151,42,181), discord.Color.from_rgb(254,158,19), discord.Color.from_rgb(0,87,184), discord.Color.from_rgb(163,87,16)]
		nsl = "W24NS1Jurong EastNS2Bukit BatokNS3Bukit GombakBP1JS1NS4Choa Chu KangNS5Yew TeeNS7KranjiNS8MarsilingTE2NS9WoodlandsNS10AdmiraltyNS11SembawangNS12CanberraNS13YishunNS14KhatibNS15Yio Chu KangCR11NS16Ang Mo KioCC15NS17BishanNS18BraddellNS19Toa PayohNS20NovenaDT11NS21NewtonTE14NS22OrchardNS23SomersetCC1NE6NS24Dhoby GhautEW13NS25City HallEW14NS26Raffles PlaceTE20CE2NS27Marina BayNS28Marina South Pier"
		ewl = "EW33Tuas LinkEW32Tuas West RoadEW31Tuas CrescentEW30Gul CircleEW29Joo KoonEW28PioneerJS8EW27Boon LayEW26LakesideEW25Chinese GardenJE5NS1EW24Jurong EastEW23ClementiEW22DoverCC22EW21Buona VistaEW20CommonwealthEW19QueenstownEW18RedhillEW17Tiong BahruTE17NE3EW16Outram ParkEW15Tanjong PagarNS26EW14Raffles PlaceNS25EW13City HallDT14EW12BugisEW11LavenderEW10KallangEW9AljuniedCC9EW8Paya LebarEW7EunosEW6KembanganEW5BedokCGEW4Tanah MerahEW3SimeiDT32EW2TampinesCP1CR5EW1Pasir RisDT35CG1ExpoCG2Changi Airport"
		nel = "NE1HarbourFrontTE17EW16NE3Outram ParkDT19NE4ChinatownNE5Clarke QuayCC1NS24NE6Dhoby GhautDT12NE7Little IndiaNE8Farrer ParkNE9Boon KengNE10Potong PasirNE11WoodleighCC13NE12SerangoonNE13KovanCR8NE14HougangNE15BuangkokSTCNE16SengkangPTCCP4NE17PunggolNE18Punggol Coast"
		ccl = "CC1Dhoby GhautCC2Bras BasahCC3EsplanadeDT15CC4PromenadeCC5Nicoll HighwayCC6StadiumCC7MountbattenCC8DakotaEW8CC9Paya LebarDT26CC10MacPhersonCC11Tai SengCC12BartleyNE12CC13SerangoonCC14Lorong ChuanNS17CC15BishanCC16MarymountTE9CC17CaldecottDT9CC19Botanic GardensCC20Farrer RoadCC21Holland VillageEW21CC22Buona VistaCC23one-northCC24Kent RidgeCC25Haw Par VillaCC26Pasir PanjangCC27Labrador ParkCC28Telok BlangahNE1CC29HarbourFrontCC30KeppelCC31CantonmentCC32Prince Edward RoadTE20NS27CE2Marina BayDT16CE1Bayfront"
		dtl = "6DT1Bukit PanjangDT2CashewDT3HillviewDT4HumeDT5Beauty WorldDT6King Albert ParkDT7Sixth AvenueDT8Tan Kah KeeCC19DT9Botanic GardensTE11DT10StevensNS21DT11NewtonNE7DT12Little IndiaDT13RochorEW12DT14BugisCC4DT15PromenadeCE1DT16BayfrontDT17DowntownDT18Telok AyerNE4DT19ChinatownDT20Fort CanningDT21BencoolenDT22Jalan BesarDT23BendemeerDT24Geylang BahruDT25MattarCC10DT26MacPhersonDT27UbiDT28Kaki BukitDT29Bedok NorthDT30Bedok ReservoirDT31Tampines WestEW2DT32TampinesDT33Tampines EastDT34Upper ChangiCG1DT35ExpoDT36XilinTE31DT37Sungei Bedok"
		tel = "TE1Woodlands NorthNS9TE2WoodlandsTE3Woodlands SouthTE4SpringleafTE5LentorTE6MayﬂowerCR13TE7Bright HillTE8Upper ThomsonCC17TE9CaldecottTE10Mount PleasantDT10TE11StevensTE12NapierTE13Orchard BoulevardNS22TE14OrchardTE15Great WorldTE16HavelockNE3EW16TE17Outram ParkTE18MaxwellTE19Shenton WayCE2NS27TE20Marina BayTE21Marina SouthTE22Gardens by the BayTE22AFounders' MemorialTE23Tanjong RhuTE24Katong ParkTE25Tanjong KatongTE26Marine ParadeTE27Marine TerraceTE28SiglapTE29BayshoreTE30Bedok SouthDT37TE31Sungei Bedok"
		self.mrt_stations = []
		for line in [nsl, ewl, nel, ccl, dtl, tel]:
			codes = re.findall("[A-Z]+\d+", line)
			names = re.split("[A-Z]+\d+", line)[1:]
			fullnames = ""
			for i in range(len(codes)):
				fullnames += f'**``{codes[i]}``** {names[i]}'
				if names[i] != "": fullnames += '\n'
			self.mrt_stations += [fullnames.split('\n')[:-1]]
