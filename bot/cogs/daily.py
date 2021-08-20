import discord
from discord.ext import commands, tasks

from bot import *
from .reddit import RedditCog
from .quote import QuoteCog
from datetime import datetime
import sys
import asyncpg
import asyncio
from urllib.parse import urlparse


class DailyCog(commands.Cog):
	"""Daily Briefing"""

	def __init__(self, bot: commands.bot, db: db_accessor, reddit: RedditCog, quote: QuoteCog):
		self.bot = bot
		self.db = db
		self.reddit = reddit
		self.quote = quote
		print(sys.argv[0] + ' being loaded!')
		self.lock = asyncio.Lock()
		self.daily_briefing.add_exception_type(asyncpg.PostgresConnectionError)
		self.daily_briefing.start()


	# scans through links in database, if known API reads & outputs message
	async def view_links(self):
		messages = []
		for link in self.db.LINKS:
			if link.startswith("https://www.reddit.com"): out = await self.reddit.web_reddit(link)
			else: print(f'handler.read_link: {link=} does not match any known APIs!')
			for m in out: messages.append(m)
		return messages


	@commands.group()
	async def dailylinks(self, ctx):
		pass


	@dailylinks.command(usage=USAGES['daily']['add'])
	async def add(self, ctx, new_link: str):
		"""Adds a new non-existing link for daily briefing. Daily briefing will only display messages for recognised domains."""
		# Validate url
		o = urlparse(new_link)
		if o.scheme not in ['http','https']: raise commands.BadArgument("Non-http link")

		# ensure non-duplicate url
		if new_link in self.db.LINKS: raise commands.BadArgument("Existing link!")

		# save url
		if self.db.add_link(new_link):
			# successfully saved!
			await ctx.reply("New link successfully added!")
		else:
			raise commands.BadArgument("Database save failed")


	@add.error
	async def add_error(self, ctx, error):
		await p(ctx, error)
		await badarguments(ctx, 'daily', 'add')


	@dailylinks.command(usage=USAGES['daily']['remove'])
	async def remove(self, ctx, link: str):
		"""Removes one of existing links for daily briefing."""
		if self.db.remove_link(link):
			# successfully removed
			await ctx.reply("Link successfully removed!")
		else:
			raise commands.BadArgument("Database save failed")


	@remove.error
	async def remove_error(self, ctx, error):
		await badarguments(ctx, 'daily', 'remove')


	@dailylinks.command(name="list", aliases=ALIASES['daily']['list'])
	async def command_list(self, ctx):
		"""Sends list of links used in daily briefing."""
		embed = discord.Embed(
			colour=discord.Colour.blurple(),
			title = 'Daily Briefing Links',
			description = '\n'.join(self.db.LINKS)
		)
		await p(ctx, embed)


	@commands.command(aliases=ALIASES['daily']['daily'])
	async def daily(self, ctx):
		"""Your daily quotes and links, does not interrupt usual 24h daily briefing loop."""
		await self.daily_briefing(ctx)


	# daily briefing every 24h at set time
	@tasks.loop(hours=24.0, minutes = 0.0)
	async def daily_briefing(self, ctx = None):
		async with self.lock:
			if ctx == None:
				ctx = self.bot.get_guild(self.db.GUILD_ID).get_channel(self.db.DAILY_CHANNEL)
			out = ["Your daily briefing up and coming!"]
			out += [await self.quote.web_quote(-1)] # quote of the day
			out += await self.view_links()
			await p(ctx, out)


	# reads set-time for daily briefing, waits for that time
	@daily_briefing.before_loop
	async def daily_briefing_before(self):
		await self.bot.wait_until_ready()

		now = datetime.now(tz = self.db.tz)
		start = datetime(now.year, now.month, now.day, self.db.DAILY_TIME, 0, 0, 0, tzinfo=self.db.tz)
		delta = int((start-now).total_seconds()) % 86400
		# waiting seconds > 0, 86400 = days in seconds
		print(f'Bot connected\nDailyCog time left: {delta=}')
		await asyncio.sleep(delta)
		print('DailyCog done waiting!')


	@daily_briefing.error
	async def error_handle(self, error):
		print(f'DailyCog: {error=}')
		pass


	@commands.command(aliases=ALIASES['daily']['timetable'])
	async def timetable(self, ctx):
		"""Sends timetable message set by each user."""
		userid = ctx.message.author.id
		if userid in self.db.TIMETABLES:
			await ctx.reply(self.db.TIMETABLES[userid])
		else:
			await ctx.reply("No timetable set! Use `.timetableset`")


	@commands.command(aliases=ALIASES['daily']['timetableset'])
	async def timetableset(self, ctx, *, contents: str = ""):
		"""Sets timetable contents which bot will send upon command. Unique to each user."""
		out = self.db.add_timetable(int(ctx.message.author.id), contents)
		if out: await ctx.reply("Timetable set!")
		else: await ctx.reply("Timetable set failed!")


	def cog_unload(self):
		self.daily_briefing.cancel()
