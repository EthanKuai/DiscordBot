import discord
import json
import re

MAX_LEN = 1900 # discord message max length
MAX_PARA = 165 # paragraph max len
# .trim()
_TRIM = [("*",""),("`",""),(">>> ",""),("%20"," "),("_"," "),("   "," "),("  "," "),("&amp;",""),("&gt;","")]
_TRIM_LINK = [(" ","%20"),("amp;","")]
with open('bot/data/usages.json') as f: USAGES = json.load(f)
with open('bot/data/aliases.json') as f: ALIASES = json.load(f)


async def badarguments(ctx, cog: str, name: str):
	"""Helps format error messages when user keys in wrong arguments for a Discord command."""
	out = 'Wrong arguments!\n'
	out += f'**Arguments**: `.{name} {USAGES[cog][name]}`\n'
	if cog in ALIASES:
		if name in ALIASES[cog]:
			out += f'**Aliases**: {", ".join(ALIASES[cog][name])}\n'
	out += '\n**``<x>``**: *x* is a required arguments; **``[y=m]``**: *y* is an optional argument with default value *m*\n'
	out += 'Type `.help command` for more info on a command.\n'
	out += 'You can also type `.help category` for more info on a category.'
	await ctx.send(out)


async def p(ctx, messages, splitby: str = "\n"):
	"""Sends one/ list of normal & embed messages to Discord ctx, manages char limit."""
	if not isinstance(messages, list): messages = [messages]
	for m in messages:
		if isinstance(m, discord.Embed): # embed message
			await ctx.send(embed = m)
			continue
		for line in m.split(splitby):
			line = line.strip()
			if line == "": # empty line
				continue
			elif len(line) < MAX_LEN: # short line
				await ctx.send(line)
				continue
			for i in range(0, len(line)+MAX_LEN-1, MAX_LEN): # long line
				await ctx.send(line[i: i + MAX_LEN])


def closestMatch(s: str, lst_in: list, /, splitby: str = ' '):
	"""Finds closest item in list to string, uses splitby to split each phrase in list into words."""
	lst = []
	for i in lst_in: lst += [i.lower().split(splitby)]
	s = s.lower().strip()

	score = [0 for _ in lst]
	maxindex = 0 # index of maximum scorer

	for phrase in range(len(lst)):
		for word in lst[phrase]:
			if re.search(word, s):
				score[phrase] += 1
		if score[phrase] > score[maxindex]:
			maxindex = phrase
	return maxindex, splitby.join(lst[maxindex])


def trim(string: str, maxlen: int = MAX_PARA):
	"""Trims string to fit maxlen, removes special symbols, accounts for hyperlinks."""

	def process_nolinks(s: str):
		for i, j in _TRIM: s = s.replace(i, j)
		cleansed = ''

		for ss in re.split(';|\n', s.strip()):
			ss = re.sub("\s*#[\da-fA-F]{6}\s*", "", ss.strip()) # remove hex color str
			if ss != '': cleansed += ss + ' '

		return re.sub(" +", " ", cleansed)

	def process_links(s: str):
		if s.startswith('http'): # link
			return s
		else: # hyperlink
			arr = s.split('](')
			for i, j in _TRIM_LINK: arr[2] = arr[2].replace(i, j)
			return arr[0] + '](' + arr[2]

	LINK_RGX = '\[[\w ]*\]\(https*:\/\/[\w\.\/\?\& \-~:#\[\]@!\$\'\*\+,;%=]+\)|https*:\/\/[\w\.\/\?\&\-~:#\[\]@!\$\'\*\+,;%=\(\)]+' # retrieve hyperlinks & links
	lst_nolinks = re.split(LINK_RGX, string)
	lst_links = re.findall(LINK_RGX, string)
	out = ''

	for i in range(len(lst_nolinks)+len(lst_links)):
		if i%2==0: # nolinks
			out += process_nolinks(lst_nolinks[i//2]) + ' '
		else: # links
			out += process_links(lst_links[i//2]) + ' '

		# overflow
		if len(out) > maxlen:
			if i%2==0: out = out[:maxlen] # does not end w link
			return out + '...'

	return out

