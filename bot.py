import discord
import logging
from discord.ext import commands
from keep_alive import keep_alive

from async_handlers import *
from converters import *
from database import db_accessor
import requests
import json
import random
import typing


MAX_LEN = 1950
DESC = "Hi I am Pseudo, a personal discord bot. Currently in development."
QUOTES = []
QUOTE_DAILY = ["today","daily","qotd"]

bot = commands.Bot(command_prefix = '.', description = DESC)
help_dict = json.load(open('help.json',))
db = db_accessor()
web_bot = web_crawler(db)
my_cog = MyCog(bot, web_bot, db)


# print command
async def p(ctx,out):
	response = out.split("\n")
	for line in response:
		if len(line) < MAX_LEN:
			await ctx.send(line)
		else:
			i = 0
			while i < len(line):
				await ctx.send(line[i: i + MAX_LEN])
				i += MAX_LEN


@bot.command()
async def echo(ctx,cnt: typing.Optional[int] = 1,*,response):
	for i in range(min(cnt,10)):
		await ctx.send(response)


@bot.command()
@commands.is_owner()
async def _embed(ctx,*,arg):
	try:
		await ctx.send(embed = eval(f'discord.Embed({arg})'))
	except:
		await ctx.send("failed.")


@bot.command()
async def helpp(ctx):
	message = "**^ represents an optional argument**\n\n"
	for i, (command, description) in enumerate(help_dict.items()):
		message += "```" + command + "``` >> " + description + "\n\n"
	#await ctx.send(message)
	await p(ctx,message)


@bot.command()
async def quote(ctx, cnt: text_or_int(-1, QUOTE_DAILY) = 1):
	if cnt==-1: # daily quote
		response = requests.get("https://zenquotes.io/api/today")
		json_tmp = json.loads(response.text)
		quote = "*\"" + json_tmp[0]['q'].strip() + "\"* - **" + json_tmp[0]['a'].strip() + "**"
		await ctx.send("**Quote of the day**: " + quote)
	else: # normal quote
		global QUOTES
		cnt = min(cnt,25)
		if len(QUOTES) < cnt:
			response = requests.get("https://zenquotes.io/api/quotes")
			QUOTES += json.loads(response.text)

		for i in range(cnt):
			quote = "*\"" + QUOTES[-1]['q'].strip() + "\"* - **" + QUOTES[-1]['a'].strip() + "**"
			QUOTES.pop()
			await ctx.send(quote)


@quote.error
async def quote_error(ctx, error):
	if isinstance(error, commands.BadArgument):
		await ctx.send('**.quote** Only accepts one argument: number of quotes, or "daily/qotd/today" for quote of the day')


@bot.command()
async def coin(ctx, cnt: typing.Optional[int] = 1):
	message = ""
	total = 0
	cnt = min(cnt,MAX_LEN)

	if cnt < 100:
		yes = "yes "
		no = "no "
	else:
		yes = "1 "
		no = "0 "

	for i in range(cnt):
		if random.randint(0,1):
			message += yes
			total += 1
		else: message += no

	if cnt > 1: message += "\nTotal sum: **" + str(total) + "**"
	await p(ctx,message)


@bot.command()
async def rng(ctx, maxn: int, cnt: typing.Optional[int] = 1):
	message = ""
	total = 0
	cnt = min(max(1, cnt),MAX_LEN)
	maxn = max(1, maxn)

	for i in range(cnt):
		tmp = random.randint(0,maxn)
		message += str(tmp) + " "
		total += tmp

	if cnt > 1:
		message += "\nTotal sum: **" + str(total) + "**"
	await p(ctx,message)


@bot.command()
@commands.is_owner()
async def _error(ctx, *description):
	await ctx.send("**<Admin>** Error raised.")
	raise discord.DiscordException(' '.join(description))


@bot.command()
@commands.is_owner()
async def _info(ctx):
	try:
		out = "**<Admin>** Channel information.\n"

		out += f'**guild:**{ctx.guild}, **guild id:**{ctx.guild.id}\n'

		out += f'**channel:**{ctx.channel}, **channel id:**{ctx.channel.id}\n'
		out += '**text channel list of guild:**\n'
		for channel in ctx.guild.channels:
			if channel.type == 'text': out += f'{channel} '
		out += '\n'

		out += f'**author:**{ctx.author}, **author id :**{ctx.author.id}\n'
		out += '**member list of guild:**\n'
		for m in ctx.guild.fetch_members(limit=100):
			out += f'({m}, {m.id}) '
		out += '\n'

		out += f'Functions of ctx: use command `dir(ctx)`'
		await p(ctx, out)
	except:
		await ctx.send("failed.")
		await _error(ctx, "_info failed")


@bot.command()
@commands.is_owner()
async def _eval(ctx, *, arg):
	try:
		await ctx.send(eval(arg))
	except:
		await ctx.send("failed.")


@bot.command()
async def hi(ctx):
	await p(ctx,DESC)


@bot.command()
async def daily(ctx):
	await quote(ctx,-1)
	await my_cog.daily_briefing(ctx.guild.id, ctx.channel.id)
	await ctx.send("There is supposed to be other dailies.")


@bot.command()
async def ping(ctx, precision: typing.Optional[int] = 3):
	await ctx.reply('Pong! Latency: {0}'.format(round(bot.latency, precision)))


@bot.command()
async def news(ctx):
	await ctx.send("there is supposed to be a news feeds")


keep_alive()
bot.run(db.TOKEN)
