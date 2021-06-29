import discord
from discord.ext import commands, tasks

from bot import *
from .reddit import RedditCog
from .quote import QuoteCog
from datetime import datetime
import sys
import asyncpg
import asyncio


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
			out += await self.view_links()
			out += [await self.quote.web_quote(-1)] # quote of the day
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
		usr = ctx.message.author.id
		for (userid, contents) in self.db.TIMETABLES:
			if userid == usr:
				await p(ctx, contents)
				return
		await p(ctx, "No timetable set! Use `.timetableset`")


	@commands.command(aliases=ALIASES['daily']['timetableset'])
	async def timetableset(self, ctx, *, contents: str = ""):
		"""Sets timetable contents which bot will send upon command. Unique to each user."""
		out = self.db.add_timetable(int(ctx.message.author.id), contents)
		if out: ctx.reply("Timetable set!")
		else: ctx.reply("Timetable set failed!")


	def cog_unload(self):
		self.daily_briefing.cancel()
