import discord
import logging
from discord.ext import commands

from bot import *
from .cogs import *
import json


DESC = "Hi I am Pseudo, a personal discord bot. Currently in development."
HELP_COMMAND = commands.DefaultHelpCommand(no_category = 'Others')

# bot
intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.typing = False
intents.presences = False
bot = commands.Bot(
	command_prefix = commands.when_mentioned_or('.'),
	description = DESC,
	intents = intents,
	case_insensitive = True,
	help_command = HELP_COMMAND
)

# utilities
with open('bot/usage.json') as f: usages = json.load(f)
with open('bot/aliases.json') as f: aliases = json.load(f)
db = db_accessor()
web_bot = web_accessor()

# cogs
bot_cogs = {'owner':OwnerCog(bot),
			'utility':UtilityCog(bot),
			'reddit':RedditCog(bot, web_bot),
			'wiki':WikiCog(bot, web_bot),
			'quote':QuoteCog(bot, web_bot),
			'singapore':SingaporeCog(bot)
}
bot_cogs['daily'] = DailyCog(bot, db, bot_cogs['reddit'], bot_cogs['quote'])
if __name__ == '__main__':
	for i in bot_cogs.values():
		bot.add_cog(i)

# https://docs.python.org/3/library/logging.html#module-logging
# https://docs.python.org/3/howto/logging.html#logging-basic-tutorial
logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR) #INFO, DEBUG, ERROR, WARNING, CRITICAL
handler = logging.FileHandler(filename='err.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# help format error messages when user keys in wrong arguments for a command
async def badarguments(ctx, cog: str, name: str):
	out = 'Wrong arguments!\n'
	out += f'**Arguments**: `.{name} {usages[cog][name]}`\n'
	if cog in aliases:
		if name in aliases[cog]:
			out += f'**Aliases**: {", ".join(aliases[cog][name])}\n'
	out += '\n**``<x>``**: *x* is a required arguments; **``[y=m]``**: *y* is an optional argument with default value *m*\n'
	out += 'Type `.help command` for more info on a command.\n'
	out += 'You can also type `.help category` for more info on a category.'
	await ctx.send(out)

# When bot is ready
@bot.event
async def on_ready():
	global bot
	# discord.Game(name="", type=1, url="")
	# discord.Streaming(name="", url="")
	# discord.Activity(type=discord.ActivityType.listening/watching, name="")
	await bot.change_presence(activity=discord.Game(name='Type .help for help!', type=1))
	print(f'{bot.user.name=}; {bot.user.id=}; {discord.__version__=}')

@bot.command(aliases=['hello','bonjour','ohayou','halo','nihao'])
async def hi(ctx):
	"""Help Pseudo remain happy!"""
	await p(ctx,DESC)

alive()
bot.run(db.TOKEN, bot=True, reconnect=True)
