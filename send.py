from discord import Embed
import re

MAX_LEN = 1950 # discord message length
MAX_PARA = 170 # paragraph max len
TRIM = [("*",""),("`",""),(">>> ",""),("  "," "),(" _"," "),("_ "," ")] # .replace() in trim()

# sends list of message to ctx (context)
async def p(ctx, messages, keyword: str = "\n"):
	if isinstance(messages, str): messages = [messages]
	for m in messages:
		if isinstance(m, Embed): # embed message
			await ctx.send(embed = m)
			continue
		for line in m.split(keyword): # split by keyword
			line = line.strip()
			if line == "": # empty line
				continue
			elif len(line) < MAX_LEN: # short line
				await ctx.send(line)
				continue
			for i in range(0, len(line)+MAX_LEN-1, MAX_LEN): # long line
				await ctx.send(line[i: i + MAX_LEN])

# trims string to fit maxlen, removes special symbols, accounts for hyperlinks
def trim(s: str, maxlen: int = MAX_PARA):
	out = ''
	for i in TRIM: s = s.replace(i[0],i[1])
	s = re.split(';|\n', s.strip())
	for ss in s:
		if maxlen < 0:
			print('theres something wrong!!!')
			exit()
		ss = ss.strip()
		if ss == '' or ss == '&gt' or ss == '&amp': continue # reddit formatting
		if ss[0] == '#' and len(ss) == 6 and ss[1:].isnumeric(): continue # color coding
		maxlen -= len(ss) + 1
		if maxlen >= -1:
			out += ss + ' '
		elif maxlen > -7:
			out += ss[:maxlen]
			break
		else:
			index = ss[:max(-1,maxlen+6)].find("](http")
			if index != -1:
				out += ss[:index + 1 + ss[index:].find(")")]
				maxlen = 0
			else: out += ss[:maxlen]
			break
	if maxlen < -1: out = out[:-3] + "..."
	return out.strip().replace("  "," ")
