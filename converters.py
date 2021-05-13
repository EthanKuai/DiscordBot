from discord.ext import commands
import re

class text_or_int(commands.Converter):
	def __init__(self, textout, lst_text):
		self.textout = textout # returned when an accepted text
		self.lst_text = lst_text # list of accepted text

	async def convert(self, ctx, arg):
		arg = arg.lower()
		if arg.isnumeric(): return int(arg)
		elif arg in self.lst_text: return self.textout
		else: raise commands.BadArgument(f'Neither integer nor recognised text: <{arg}>')


class text(commands.Converter):
	def __init__(self, dict):
		self.dict = dict # dict of accepted text

	async def convert(self, ctx, arg):
		arg = arg.lower()
		if arg in self.dict:
			return self.dict[arg]
		else: raise commands.BadArgument(f'Unrecognised text: <{arg}>')


class regex(commands.Converter):
	def __init__(self, antireg: str = "", reg: str = "", maxlen: int = 2000):
		self.reg = reg
		self.antireg = antireg
		self.maxlen = maxlen

	async def convert(self, ctx, arg):
		arg = arg.lower()
		if len(arg) > self.maxlen: pass
		elif self.antireg != "" and re.search(self.antireg, arg) == None: pass
		elif self.reg != "" and re.search(self.reg, arg) != None: pass
		else: return arg
		raise commands.BadArgument(f'Unrecognised text: <{arg}>')
