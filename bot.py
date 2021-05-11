import discord
import logging
from discord.ext import commands
from keep_alive import keep_alive
import os

from async_handlers import *
from converters import *
import asyncio
import requests
import json
import random
import typing


MAX_LEN = 1950
TOKEN = os.environ['TOKEN']
SERVER = os.environ['SERVER']
DESC = "Hi I am Pseudo, a personal discord bot. Currently in development."
QUOTES = []
QUOTE_DAILY = ["today","daily","qotd"]

bot = commands.Bot(command_prefix = '.', description = DESC)
help_dict = json.load(open('help.json',))
web_bot = web_crawler()
my_cog = MyCog(bot, web_bot)


# print command
async def p(ctx,out):
    response = out.split("\n")
    for line in response:
        if len(line) < MAX_LEN:
            await ctx.send(line)
        else:
            i = 0
            while i < len(line):
                await ctx.send(line[i: i + MAX_LEN])
                i += MAX_LEN


@bot.command()
async def echo(ctx,cnt: typing.Optional[int] = 1,*,response):
    for i in range(max(cnt,10)):
        await ctx.send(response)


@bot.command()
async def helpp(ctx):
    message = "**^ represents an optional argument**\n\n"
    for i, (command, description) in enumerate(help_dict.items()):
        message += "```" + command + "``` >> " + description + "\n\n"
    #await ctx.send(message)
    await p(ctx,message)


@bot.command()
async def quote(ctx, cnt: text_or_int(-1, QUOTE_DAILY) = 1):
    if cnt==-1: # daily quote
        response = requests.get("https://zenquotes.io/api/today")
        json_tmp = json.loads(response.text)
        quote = "*\"" + json_tmp[0]['q'].strip() + "\"* - **" + json_tmp[0]['a'].strip() + "**"
        await ctx.send("**Quote of the day**: " + quote)
    else: # normal quote
        global QUOTES
        cnt = min(cnt,25)
        if len(QUOTES) < cnt:
            response = requests.get("https://zenquotes.io/api/quotes")
            QUOTES += json.loads(response.text)

        for i in range(cnt):
            quote = "*\"" + QUOTES[-1]['q'].strip() + "\"* - **" + QUOTES[-1]['a'].strip() + "**"
            QUOTES.pop()
            await ctx.send(quote)


@quote.error
async def quote_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send('**.quote** Only accepts one argument: number of quotes, or "daily/qotd/today" for quote of the day')


@bot.command()
async def coin(ctx, cnt: typing.Optional[int] = 1):
    message = ""
    total = 0
    cnt = min(cnt,MAX_LEN)

    if cnt < 100:
        yes = "yes "
        no = "no "
    else:
        yes = "1 "
        no = "0 "

    for i in range(cnt):
        if random.randint(0,1):
            message += yes
            total += 1
        else: message += no

    if cnt > 1: message += "\nTotal sum: **" + str(total) + "**"
    await p(ctx,message)


@bot.command()
async def rng(ctx, maxn: int, cnt: typing.Optional[int] = 1):
    message = ""
    total = 0
    cnt = min(max(1, cnt),MAX_LEN)
    maxn = max(1, maxn)

    for i in range(cnt):
        tmp = random.randint(0,maxn)
        message += str(tmp) + " "
        total += tmp

    if cnt > 1:
        message += "\nTotal sum: **" + str(total) + "**"
    await p(ctx,message)


@bot.command()
@commands.is_owner()
async def _error(ctx):
    await ctx.send("**<Admin>** Error raised.")
    raise discord.DiscordException


@bot.command()
@commands.is_owner()
async def _info(ctx):
    try:
        await ctx.send("**<Admin>** Channel information.")
        await ctx.send(f'guild:{ctx.guild}, channel:{ctx.channel}')
        await ctx.send(ctx)
    except:
        error(ctx)


@bot.command()
@commands.is_owner()
async def _eval(ctx, *, arg):
    await ctx.send(eval(arg))


@bot.command()
async def hi(ctx):
    await p(ctx,DESC)


@bot.command()
async def daily(ctx):
    await quote(ctx,("today"))
    await ctx.send("There is supposed to be other dailies.")


@bot.command()
async def ping(ctx, precision: typing.Optional[int] = 3):
    await ctx.send('Pong! Latency: {0}'.format(round(bot.latency, precision)))


@bot.command()
async def news(ctx):
    await ctx.send("there is supposed to be a news feeds")
    embed = discord.Embed(title="List of webpages you can open",
                      description="eg: some descriton",
                      colour=discord.Colour(0x3e038c))
    embed.add_field(name="yt", value="[link](https://www.youtube.com/)", inline=False)
    await ctx.send(embed=embed)


keep_alive()
bot.run(TOKEN)
