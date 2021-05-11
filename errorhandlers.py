import discord
from discord.ext import commands

@quote.error
async def quote_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send('**.quote** Only accepts one argument: number of quotes, or "daily/qotd/today" for quote of the day')

