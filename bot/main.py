import discord
import logging
from discord.ext import commands
from .keep_alive import keep_alive

from bot import *
import typing
import json
import random


DESC = "Hi I am Pseudo, a personal discord bot. Currently in development."
QUOTE_DAILY = {"today":-1, "daily":-1, "qotd":-1, "day":-1}
REDDIT = {"now":"now", "hour":"hour", "day":"day", "daily":"day", "today":"day", "week":"week", "month":"month", "year":"year", "all":"all", "alltime":"all", "overall":"all"}
HELP_COMMAND = commands.DefaultHelpCommand(no_category = 'Utility')

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='.', description=DESC, intents=intents,\
	 case_insensitive=True, help_command = HELP_COMMAND)
bot_cogs = [owner(bot)]
if __name__ == '__main__':
	for cog in bot_cogs: bot.load_extension(cog)
#bot.remove_command('help')
help_dict = json.load(open('help.json',))
db = db_accessor()
web_bot = web_crawler(db)
my_cog = MyCog(bot, web_bot, db)

# https://docs.python.org/3/library/logging.html#module-logging
# https://docs.python.org/3/howto/logging.html#logging-basic-tutorial
logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR) #INFO, DEBUG, ERROR, WARNING, CRITICAL
handler = logging.FileHandler(filename='err.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


@bot.event
# When bot is ready
async def on_ready():
	global bot
	print('connected!')
	await bot.change_presence(game=discord.Game(name='Type .help for help!', type=1, url=''))
	print(f'name: {bot.user.name}, id: {bot.user.id}, version: {discord.__version__}')


@bot.command()
async def echo(ctx,cnt: typing.Optional[int] = 1,*,response):
	for i in range(min(cnt,10)):
		await ctx.send(response)


@bot.command()
async def helpp(ctx):
	message = "**^ represents an optional argument**\n\n"
	for i, (command, description) in enumerate(help_dict.items()):
		message += "```" + command + "``` >> " + description + "\n\n"
	#await ctx.send(message)
	await p(ctx,message)


@bot.command()
async def quote(ctx, cnt: text_or_int(QUOTE_DAILY) = 1):
	out = await web_bot.web_quote(cnt)
	if cnt == -1: out = "**Quote of the day**: " + out
	await p(ctx, out)


@quote.error
async def quote_error(ctx, error):
	if isinstance(error, commands.BadArgument):
		await ctx.send('**.quote** Only accepts one argument (opt): *number of quotes*, or *"daily/qotd/today"* for quote of the day')


@bot.command()
async def coin(ctx, cnt: typing.Optional[int] = 1):
	message = ""
	total = 0

	if cnt < 100:
		yes = "yes "; no = "no "
	elif cnt < MAX_LEN:
		yes = "1 "; no = "0 "
	else:
		yes = ""; no = ""

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

	for i in range(cnt):
		tmp = random.randint(0,maxn)
		message += str(tmp) + " "
		total += tmp

	if cnt > 1:
		message += "\nTotal sum: **" + str(total) + "**"
	await p(ctx,message)


@bot.command()
async def hi(ctx):
	await p(ctx,DESC)


@bot.command()
async def daily(ctx):
	await quote(ctx,-1)
	await my_cog.daily_briefing(ctx)
	await ctx.send("There is supposed to be other dailies.")


@bot.command()
async def ping(ctx, precision: typing.Optional[int] = 3):
	await ctx.reply('Pong! Latency: {0}'.format(round(bot.latency, precision)))


@bot.command()
async def gnews(ctx, *args):
	await ctx.send("there is supposed to be a news feeds")


@bot.command()
async def reddit(ctx, sr: regex(antireg="\d|\s",maxlen=21), cnt: text_or_int(REDDIT) = 5, sortby: text_or_int(REDDIT, 0) = "day"):
	if isinstance(cnt, str):
		sortby = cnt; cnt = 5
	cnt = min(max(1, cnt),20)
	if sr != "top": sr = 'r/' + sr
	link = f'https://reddit.com/{sr}/top.json?sort=top&t={sortby}&limit={cnt}'
	messages = await web_bot.web_reddit(link)
	await p(ctx, messages)


@reddit.error
async def reddit_error(ctx, error):
	if isinstance(error, commands.BadArgument):
		await ctx.send('**.reddit** Accepts 3 arguments: *subreddit*, *number of posts* (opt) and *sort by "hour/day/week/month/year/all"* (opt)\nSpecial argument: "top" as subreddit for overall top posts.')


@bot.command()
async def wiki(ctx, *, search):
	search = search.split(' ')
	if search[0] == 'search':
		out = await web_bot.web_wiki_search(' '.join(search[1:]))
	elif search[-1] == 'search':
		out = await web_bot.web_wiki_search(' '.join(search[:-1]))
	elif search[-1] == 'full':
		out = await web_bot.web_wiki(' '.join(search[:-1]), True)
	else:
		out = await web_bot.web_wiki(' '.join(search))
	await p(ctx, out)


keep_alive()
bot.run(db.TOKEN, bot=True, reconnect=True)
