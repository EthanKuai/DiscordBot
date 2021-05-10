import discord
from discord.ext import commands

class text_or_int(commands.Converter):
	def __init__(self, textout, lst_text):
		self.text = textout # returned when an accepted text
		self.lst_text = lst_text # list of accepted text

    async def convert(self, ctx, arg):
		if arg=="": return 1
		elif arg.isnumeric(): return int(arg)
		elif arg in lst_text: return self.textout
		else: raise CommandError("Not integer nor recognised text")
