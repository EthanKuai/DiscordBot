import discord
from discord.ext import commands, tasks

from bot import *
from .reddit import RedditCog
from .quote import QuoteCog
from .wiki import WikiCog
from datetime import datetime
import asyncpg
import asyncio
from urllib.parse import urlparse
import re
from disputils import BotEmbedPaginator


class DailyCog(commands.Cog):
	"""Daily Briefing"""

	def __init__(self, bot: commands.bot, db: db_accessor, reddit: RedditCog, quote: QuoteCog, wiki: WikiCog):
		self.bot = bot
		self.db = db
		self.reddit = reddit
		self.quote = quote
		self.wiki = wiki
		self.lock = asyncio.Lock()
		self.daily_loop.add_exception_type(asyncpg.PostgresConnectionError)
		self.daily_loop.start()


	async def _database_get_links(self, indiv_posts: bool = False):
		"""scans through links in database, if has known API, reads & outputs message"""
		messages = []
		for link in self.db.LINKS:
			if link.startswith("https://www.reddit.com"):
				out = await self.reddit.web_reddit(link, indiv_posts = indiv_posts)
			elif re.search('https://[a-z]+.wikipedia.org/wiki/', link):
				out = await self.wiki.web_wiki(link, indiv_posts = indiv_posts)
			else:
				print(f'handler.read_link: {link=} does not match any known APIs!')
			for m in out: messages.append(m)
		return messages


	# also a standard command
	@commands.group(name='daily', aliases=ALIASES['daily']['daily_command'], invoke_without_command=True)
	async def daily_CG(self, ctx, *args):
		"""Your daily quotes and links, does not interrupt usual 24h daily briefing loop."""
		if len(args) == 0: pass # happens when no args given to children commands
		await self.daily_loop(ctx)


	"""-------------------------------- daily loop --------------------------------"""


	@tasks.loop(hours=24.0, minutes = 0.0)
	async def daily_loop(self, ctx = None, *args):
		"""daily briefing every 24h at set time"""
		try:
			async with self.lock:
				out = ["Your daily briefing up and coming!"]
				out += [await self.quote.web_quote(-1)] # quote of the day
				if ctx == None:
					# time-triggered
					ctx = self.bot.get_guild(self.db.GUILD_ID).get_channel(self.db.DAILY_CHANNEL)
					out += await self._database_get_links()
					await p(ctx, out)
				else:
					# message-triggered
					out += await self._database_get_links(indiv_posts = True)
					await p(ctx, out[:2])
					paginator = BotEmbedPaginator(ctx, out[2:])
					await paginator.run(timeout = 400)
		except Exception as error:
			if ctx != None: await p(ctx, "Daily briefing has run into an error!")
			owner = await self.bot.application_info().owner
			if owner != None:
				await owner.send('Daily briefing has run into an error')
				await owner.send(f'{error=}')


	@daily_loop.before_loop
	async def daily_loop_before(self):
		"""reads set-time for daily briefing, waits for that time"""
		await self.bot.wait_until_ready()

		now = datetime.now(tz = self.db.tz)
		start = datetime(now.year, now.month, now.day, self.db.DAILY_TIME, 0, 0, 0, tzinfo=self.db.tz)
		delta = int((start-now).total_seconds()) % 86400
		# waiting seconds > 0, 86400 = days in seconds
		print(f'Bot connected\nTime of daily briefing: {self.db.DAILY_TIME:02}:00, {self.db.tz}\nDailyCog time left: {delta=}')
		await asyncio.sleep(delta)
		print('DailyCog done waiting!')


	def cog_unload(self):
		self.daily_loop.cancel()


	"""-------------------------------- daily links --------------------------------"""


	@daily_CG.group(name='links', invoke_without_command=True)
	async def dl_CG(self, ctx, *args):
		"""List of links used in daily briefing."""
		if len(args) == 0: pass # no args given to children commands
		embed = discord.Embed(
			colour=discord.Colour.blurple(),
			title = 'Daily Briefing Links',
			description = '\n'.join(self.db.LINKS)
		)
		await p(ctx, embed)


	@dl_CG.command(name='add', usage=USAGES['daily']['dl_add'])
	async def dl_add(self, ctx, new_link: str):
		"""Adds a new non-existing link for daily briefing. Daily briefing will only display messages for recognised domains."""
		# Validate url
		o = urlparse(new_link)
		if o.scheme not in ['http','https']: raise commands.BadArgument("Non-http link")
		# ensure non-duplicate url
		if new_link in self.db.LINKS: raise commands.BadArgument("Existing link!")

		# save url
		if self.db.add_link(new_link):
			await ctx.message.add_reaction("✅")
		else:
			await ctx.message.add_reaction("❎")
			raise commands.BadArgument("Database save failed")


	@dl_add.error
	async def dl_add_error(self, ctx, error):
		await p(ctx, error)
		await badarguments(ctx, 'daily', 'dl_add')


	@dl_CG.command(name='remove', usage=USAGES['daily']['dl_remove'])
	async def dl_remove(self, ctx, link: str):
		"""Removes one of existing links for daily briefing."""
		if self.db.remove_link(link):
			await ctx.message.add_reaction("✅")
		else:
			await ctx.message.add_reaction("❎")
			raise commands.BadArgument("Database save failed")


	@dl_remove.error
	async def dl_remove_error(self, ctx, error):
		await badarguments(ctx, 'daily', 'dl_remove')


	"""-------------------------------- daily time --------------------------------"""


	@daily_CG.group(name='time', invoke_without_command=True)
	async def dt_CG(self, ctx, *args):
		"""Timing of daily briefing"""
		if len(args) != 0: pass # no args given to children commands
		await p(ctx, f'Daily at {self.db.DAILY_TIME:02}:00, {self.db.tz}.')


	@dt_CG.command(name="shift", usage=USAGES['daily']['dt_shift'])
	async def dt_shift(self, ctx, shift: int):
		"""Shift time for daily briefing by offset (-ve means earlier)."""
		self.db.DAILY_TIME = ( self.db.DAILY_TIME + shift ) % 24
		self.db.update_data()
		await p(ctx, f"Shifted by {shift} hours! New time: {self.db.DAILY_TIME:02}:00, {self.db.tz}")


	@dt_shift.error
	async def dt_shift_error(self, ctx, error):
		await badarguments(ctx, 'daily', 'dt_shift')


	@dt_CG.command(name="timezone", aliases=ALIASES['daily']['dt_timezone'], usage=USAGES['daily']['dt_timezone'])
	async def dt_timezone(self, ctx, tz: text_or_int(TZ_DICT)):
		"""Set time to new timezone."""
		if tz > 12 or tz < -11:
			raise commands.BadArgument("Invalid timezone")
		self.db.TZ_OFFSET = tz
		self.db.update_data()
		await p(ctx, f"Changed timezone! New time: {self.db.DAILY_TIME:02}:00, {self.db.tz}")


	@dt_timezone.error
	async def dt_timezone_error(self, ctx, error):
		await badarguments(ctx, 'daily', 'dt_timezone')
