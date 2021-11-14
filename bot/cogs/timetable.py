import discord
from discord.ext import commands

from bot import *


class TimetableCog(commands.Cog):
	"""Timetable message u can use to check your reminders, custom for each user"""

	def __init__(self, bot: commands.bot, db: db_accessor):
		self.bot = bot
		self.db = db
		self.tt_message = "No timetable set! Use `.ttset`. Afterwards, you can also append your set-timetable with `.ttadd` for easy updating, and remove lines with `.ttremove`"


	@commands.command(aliases=ALIASES['daily']['timetable'])
	async def timetable(self, ctx):
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
			await ctx.reply(embed = embed)
		else:
			await ctx.reply(self.tt_message)


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

			out = self.db.add_timetable(userid, new_contents, updated_img = img)
			if out: await ctx.message.add_reaction("✅")
			else: await ctx.message.add_reaction("❎")
		else:
			await ctx.reply(self.tt_message)


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
			await ctx.reply(self.tt_message)
