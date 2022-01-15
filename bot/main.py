import discord
import logging
from discord.ext import commands

from bot import *
from .cogs import *
from .keep_alive import alive


# bot
DESC = "Hi I am Pseudo, a personal discord bot. Currently in development."
help_command = commands.DefaultHelpCommand(no_category = 'Others')

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
	help_command = help_command
)


# bot commands
@bot.event
async def on_ready():
	"""When bot is ready and connected to Discord"""
	# discord.Game discord.Streaming discord.Activity(type=discord.ActivityType.listening/watching)
	await bot.change_presence(activity=discord.Game(name='Type .help for help!', type=1))
	print(f'{bot.user.name=}; {bot.user.id=}; {discord.__version__=}')

@bot.command(aliases=ALIASES['hi'])
async def hi(ctx):
	"""Help Pseudo remain happy!"""
	await p(ctx,DESC)


# cogs
db = db_accessor()
web_bot = web_accessor()

bot_cogs = {
	'owner':OwnerCog(bot, db),
	'utility':UtilityCog(bot, db),
	'reddit':RedditCog(bot, web_bot),
	'wiki':WikiCog(bot, web_bot),
	'quote':QuoteCog(bot, web_bot),
	'singapore':SingaporeCog(bot),
	'twitter':TwitterCog(bot),
	'timetable':TimetableCog(bot, db, web_bot),
	'google':GoogleCog(bot, db, web_bot),
	'dictionary':DictionaryCog(bot, db, web_bot)
}
bot_cogs['daily'] = DailyCog(bot, db, bot_cogs['reddit'], bot_cogs['quote'], bot_cogs['wiki'])


# logger
# https://docs.python.org/3/library/logging.html#module-logging
# https://docs.python.org/3/howto/logging.html#logging-basic-tutorial
logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR) #INFO, DEBUG, ERROR, WARNING, CRITICAL
handler = logging.FileHandler(filename='err.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


# main script
def main():
	global bot
	for bot_cog in bot_cogs.values(): bot.add_cog(bot_cog)
	alive()
	bot.run(db.TOKEN, bot=True, reconnect=True)

if __name__ == '__main__':
	main()
