import discord
import logging
from discord.ext import commands
from .keep_alive import keep_alive

from bot import *
from .cogs import * # !!! does this work
import typing
import json
import random


DESC = "Hi I am Pseudo, a personal discord bot. Currently in development."
HELP_COMMAND = commands.DefaultHelpCommand(no_category = 'Others')

# bot
intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.typing = False
intents.presences = False
bot = commands.Bot(command_prefix='.', description=DESC, intents=intents,
					case_insensitive=True, help_command = HELP_COMMAND)
#bot.remove_command('help')

# utilities
with open('help.json',) as f: help_dict = json.load(f)
db = db_accessor()
web_bot2 = web_accessor()

# cogs
bot_cogs = {'owner':OwnerCog(bot),
			'utility':UtilityCog(bot),
			'reddit':RedditCog(bot, web_bot2),
			'wiki':WikiCog(bot, web_bot2),
			'quote':QuoteCog(bot, web_bot2)
}
bot_cogs['daily'] = DailyCog(bot, db, bot_cogs['reddit'], bot_cogs['quote'])
if __name__ == '__main__':
	for cog_name in bot_cogs.keys():
		bot.load_extension(bot_cogs[cog_name]) # !!! does this work

# https://docs.python.org/3/library/logging.html#module-logging
# https://docs.python.org/3/howto/logging.html#logging-basic-tutorial
logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR) #INFO, DEBUG, ERROR, WARNING, CRITICAL
handler = logging.FileHandler(filename='err.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# When bot is ready
@bot.event
async def on_ready():
	global bot
	print('connected!')
	await bot.change_presence(game=discord.Game(name='Type .help for help!', type=1, url=''))
	print(f'name: {bot.user.name}, id: {bot.user.id}, version: {discord.__version__}')

@bot.command()
async def helpp(ctx):
	message = "**^ represents an optional argument**\n\n"
	for i, (command, description) in enumerate(help_dict.items()):
		message += "```" + command + "``` >> " + description + "\n\n"
	#await ctx.send(message)
	await p(ctx,message)

@bot.command()
async def hi(ctx):
	await p(ctx,DESC)

keep_alive()
bot.run(db.TOKEN, bot=True, reconnect=True)
