from discord.ext import commands
import re

class text_or_int(commands.Converter):
	"""Accepts some words, and can accept integers as well."""

	def __init__(self, text: dict, accept_int: bool = True):
		self.text = text # dict of accepted text
		self.accept_int = accept_int

	async def convert(self, ctx, arg):
		arg = arg.lower()
		if self.accept_int and arg.isnumeric():
			return int(arg)
		if arg in self.text:
			return self.text[arg]
		else: raise commands.BadArgument(f'Neither integer nor recognised text: <{arg}>')


class regex(commands.Converter):
	"""Accepts arguments within a max length, passing regex and failing antiregex"""

	def __init__(self, antireg: str = "", reg: str = "", maxlen: int = 2000):
		self.reg = reg
		self.antireg = antireg
		self.maxlen = maxlen

	async def convert(self, ctx, arg):
		arg = arg.lower()
		if len(arg) > self.maxlen: pass
		elif len(arg) == 0: pass
		elif self.antireg != "" and re.search(self.antireg, arg) != None: pass
		elif self.reg != "" and re.search(self.reg, arg) == None: pass
		else: return arg
		raise commands.BadArgument(f'Unrecognised text: <{arg}>')
