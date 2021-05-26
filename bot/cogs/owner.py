import discord
from discord.ext import commands

from bot import *
import sys


def setup(bot):
	print(sys.argv[0] + ' being loaded!')
	bot.add_cog(OwnerCog(bot))

def teardown(bot):
	print(sys.argv[0] + ' being unloaded!')

class OwnerCog(commands.Cog):
	def __init__(self, bot: commands.bot):
		self.bot = bot

	# Won't show up on the default help.
	@commands.command(name='_load', hidden=True)
	@commands.is_owner()
	async def cog_load(self, ctx, cog):
		try:
			self.bot.load_extension(cog)
		except Exception as e:
			await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
		else:
			await ctx.send('**`SUCCESS`**')


	@commands.command(name='_unload', hidden=True)
	@commands.is_owner()
	async def cog_unload(self, ctx, cog):
		try:
			self.bot.unload_extension(cog)
		except Exception as e:
			await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
		else:
			await ctx.send('**`SUCCESS`**')


	@commands.command(name='_reload', hidden=True)
	@commands.is_owner()
	async def cog_reload(self, ctx, cog):
		await self.cog_load(ctx, cog)
		await self.cog_unload(ctx, cog)


	@commands.command(name='_embed', hidden=True)
	@commands.is_owner()
	async def send_embed(self, ctx,*,arg):
		try:
			await ctx.send(embed = eval(f'discord.Embed({arg})'))
		except:
			await ctx.send("failed.")


	@commands.command(name='_error', hidden=True)
	@commands.is_owner()
	async def debug_error(self, ctx, *description):
		await ctx.send("**<Admin>** Error raised.")
		raise discord.DiscordException(' '.join(description))


	@commands.command(name='_info', hidden=True)
	@commands.is_owner()
	async def debug_info(self, ctx):
		try:
			out = "**<Admin>** Channel information.\n"

			out += f'**guild:**{ctx.guild}, **guild id:**{ctx.guild.id}\n'

			out += f'**channel:**{ctx.channel}, **channel id:**{ctx.channel.id}\n'
			out += '**text channel list of guild:**\n'
			for channel in ctx.guild.channels:
				out += f'{channel} '
			out += '\n'

			out += f'**author:**{ctx.author}, **author id :**{ctx.author.id}\n'
			out += '**member list of guild:**\n'
			for m in ctx.guild.members:
				out += f'({m}, {m.id}) '
			out += '\n'

			out += f'Functions of ctx: use command `dir(ctx)`'
			await p(ctx, out)
		except:
			await ctx.send("failed.")
			await self.debug_error(ctx, "_info failed")


	@commands.command(name='_eval', hidden=True)
	@commands.is_owner()
	async def debug_eval(self, ctx, *, arg):
		try:
			await ctx.send(eval(arg))
		except:
			await ctx.send("failed.")


	@commands.command(name='_exec', hidden=True)
	@commands.is_owner()
	async def debug_exec(self, ctx, *, arg):
		try:
			await ctx.send(exec(arg))
		except:
			await ctx.send("failed.")
