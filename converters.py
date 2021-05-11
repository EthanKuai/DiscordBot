from discord.ext import commands

class text_or_int(commands.Converter):
	def __init__(self, textout, lst_text):
		self.textout = textout # returned when an accepted text
		self.lst_text = lst_text # list of accepted text

	async def convert(self, ctx, arg):
		arg = arg.lower()
		if arg.isnumeric(): return int(arg)
		elif arg in self.lst_text: return self.textout
		else: raise commands.BadArgument(f'Neither integer nor recognised text: <{arg}>')