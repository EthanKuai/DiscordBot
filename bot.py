import discord
import logging
from discord.ext import commands, tasks
from keep_alive import keep_alive
import os
import asyncio

from async_handlers import *
import asyncpg
import requests
import json
import random
import typing


MAX_LEN = 1950
TOKEN = os.environ['TOKEN']
SERVER = os.environ['SERVER']
DESC = "Hi I am Pseudo, a personal discord bot. Currently in development."
QUOTES = []

bot = commands.Bot(command_prefix = '.', description = DESC)
help_dict = json.load(open('help.json',))
async_handler = handler()


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
async def echo(ctx,*,response):
    await ctx.send(response)


@bot.command()
async def helpp(ctx):
    message = "**^ represents an optional argument**\n\n"
    for i, (command, description) in enumerate(help_dict.items()):
        message += "```" + command + "``` >> " + description + "\n\n"
    #await ctx.send(message)
    await p(ctx,message)


async def quote_rng(ctx,cnt):
    global QUOTES
    cnt = min(cnt,25)
    if len(QUOTES) < cnt:
        response = requests.get("https://zenquotes.io/api/quotes")
        QUOTES += json.loads(response.text)

    for i in range(cnt):
        quote = "*\"" + QUOTES[-1]['q'].strip() + "\"* - **" + QUOTES[-1]['a'].strip() + "**"
        QUOTES.pop()
        await ctx.send(quote)


@bot.command()
async def quote(ctx,*args):
    if len(args)==0:
        await quote_rng(ctx,1)

    elif args[0].isnumeric():
        await quote_rng(ctx,int(args[0]))

    elif args[0].lower() in ["today","daily","qotd"]:
        response = requests.get("https://zenquotes.io/api/today")
        json_tmp = json.loads(response.text)
        quote = "*\"" + json_tmp[0]['q'].strip() + "\"* - **" + json_tmp[0]['a'].strip() + "**"
        await ctx.send("**Quote of the day**: " + quote)

    else:
        await ctx.send("`.quote` Wrong arguments.")
        #WIP


@bot.command()
async def coin(ctx, cnt: typing.Optional[int] = 1):
    message = ""
    total = 0

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
    cnt = min(1, cnt)
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
async def error(ctx):
    raise discord.DiscordException
    await ctx.send("**<Admin>** Error raised.")


@bot.command()
async def hi(ctx):
    await p(ctx,DESC)


@bot.command()
async def daily(ctx):
    await quote(ctx,("today"))
    await ctx.send("There is supposed to be other dailies.")


@bot.command()
async def ping(ctx):
    await ctx.send('Pong! Latency: {0}'.format(round(bot.latency, 2)))


@bot.command()
async def news(ctx):
    await ctx.send("there is supposed to be a news feeds")
    embed = discord.Embed(title="List of webpages you can open",
                      description="eg: some descriton",
                      colour=discord.Colour(0x3e038c))
    embed.add_field(name="yt", value="[link](https://www.youtube.com/)", inline=False)
    await ctx.send(embed=embed)


print("test")

keep_alive()
bot.run(TOKEN)
