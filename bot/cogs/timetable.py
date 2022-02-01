import discord
from discord.ext import commands
import asyncio
import typing

from bot import *


class TimetableCog(commands.Cog):
	"""Timetable message u can use to check your reminders, custom for each user"""

	def __init__(self, bot: commands.bot, db: db_accessor):
		self.bot = bot
		self.db = db
		self.tt_reminder = "To reset your timetable, use `.ttset`. Afterwards, you can also append your existing timetable with `.ttadd` for easy updating, and remove lines with `.ttremove`!"
		self.tt_unset = "No timetable set!" + self.tt_reminder
		self.raw_emoji = '<:raw:923554453938896936>'


	@commands.command(aliases=ALIASES['daily']['timetable'])
	async def timetable(self, ctx, others: typing.Optional[str] = None):
		"""Sends timetable message uniquely set by each user."""
		userid = ctx.message.author.id
		if userid in self.db.TIMETABLES:
			embed = (
				discord.Embed(
					title = "Timetable",
					description = self.db.TIMETABLES[userid]
				)
				.set_image(url = self.db.TIMETABLEIMGS[userid])
				.set_footer(
					text = str(ctx.author),
					icon_url = ctx.author.avatar_url
				)
			)

			# send embed, add :raw: emoji reaction
			if others is None: msg = await ctx.reply(embed = embed)
			else: msg = await ctx.reply(self.tt_reminder, embed = embed)
			await msg.add_reaction(self.raw_emoji)

			# detect for user's reaction
			def check(reaction, user):
				return str(reaction)==self.raw_emoji and user.id==userid
			try:
				reaction = None
				#reaction = await self.bot.wait_for_reaction([self.raw_emoji], msg)
				reaction, _ = await self.bot.wait_for('reaction_add', timeout=REACTION_TIMEOUT, check=check)
			except asyncio.TimeoutError: # timeout
				await msg.add_reaction(self.raw_emoji)
			finally:
				await msg.clear_reaction(self.raw_emoji)
				if reaction is not None:
					# user reacted with :raw:, send new embed of raw .tt content
					embed.description = "```md\n" + embed.description.replace("`","\u200b`\u200b")[:MAX_DESCRIPTION] + "```"
					embed.title = "Timetable [Raw]"
					await msg.edit(embed=embed)
		else:
			await ctx.reply(self.tt_unset)


	@commands.command(aliases=ALIASES['daily']['timetableset'])
	async def timetableset(self, ctx, *, contents: str = ""):
		"""Re-sets timetable (uniquely user-set), which bot will send upon command."""
		img = get_img(ctx, default = "")

		# save into database
		userid = ctx.message.author.id
		out = self.db.add_timetable(userid, contents, updated_img = img)
		if out: await ctx.message.add_reaction("✅")
		else: await ctx.message.add_reaction("❎")


	@commands.command(aliases=ALIASES['daily']['timetableadd'])
	async def timetableadd(self, ctx, *, contents: str = ""):
		"""Appends timetable (uniquely user-set), which bot will send upon command."""
		userid = ctx.message.author.id
		if userid in self.db.TIMETABLES:
			img = get_img(ctx)
			new_contents = self.db.TIMETABLES[userid] + '\n' + contents
			if len(new_contents) > MAX_DESCRIPTION:
				await ctx.message.add_reaction("❎")
				await ctx.reply(f"Maximum character count of `.tt` cannot exceed {MAX_DESCRIPTION}! Delete existing lines with `.ttremove`, or reset entire message with `.ttset`")
				return None

			out = self.db.add_timetable(userid, new_contents, updated_img = img)
			if out: await ctx.message.add_reaction("✅")
			else: await ctx.message.add_reaction("❎")
		else:
			await ctx.reply(self.tt_unset)


	@commands.command(aliases=ALIASES['daily']['timetableremove'])
	async def timetableremove(self, ctx, *, contents: str = ""):
		"""Removes existing lines from timetable (uniquely user-set), which bot will send upon command."""
		lines_to_remove = contents.split("\n")
		rejected_lines = [] # lines which are not contained in existing timetable
		userid = ctx.message.author.id

		if userid in self.db.TIMETABLES:
			lines = self.db.TIMETABLES[userid].split("\n")
			for line in lines_to_remove:
				if line in lines: lines.remove(line)
				else: rejected_lines.append(line)

			if len(rejected_lines) == len(lines_to_remove): # all lines rejected
				await ctx.message.add_reaction("❎")
				await ctx.reply("No lines in your message were found in your set timetable!")
			else:
				out = self.db.add_timetable(userid, "\n".join(lines))
				if out:
					await ctx.message.add_reaction("✅")
					if len(rejected_lines): # some lines rejected
						msg = "Some lines were not found in your set timetable:\n" + "\n".join(rejected_lines)
						await ctx.reply(msg)
				else: await ctx.message.add_reaction("❎")
		else:
			await ctx.reply(self.tt_unset)
