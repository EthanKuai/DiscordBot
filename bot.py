import discord
import logging
from discord.ext import commands, tasks
from keep_alive import keep_alive
import os

import asyncpg
import requests
import json
import random


MAX_LEN = 1950
TOKEN = os.environ['TOKEN']
SERVER = os.environ['SERVER']
DESC = "Hi I am Pseudo, a personal discord bot. Currently in development."
QUOTES = []

bot = commands.Bot(command_prefix = '.', description = DESC)
help_dict = json.load(open('help.json',))


# print command
async def p(ctx,out):
    response = out.split("\n")
    for line in response:
        if len(line) < MAX_LEN:
            await ctx.send(response)
        else:
            i = 0
            while i < len(line):
                await ctx.send(line[i: i + MAX_LEN])
                i += MAX_LEN


@bot.command()
async def echo(ctx,*,response):
    ctx.send(response)


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

    elif args[0] in ["today","daily"]:
        response = requests.get("https://zenquotes.io/api/today")
        json_tmp = json.loads(response.text)
        quote = "*\"" + json_tmp[0]['q'].strip() + "\"* - **" + json_tmp[0]['a'].strip() + "**"
        await ctx.send("**Quote of the day**: " + quote)

    else:
        await ctx.send("`.quote` Wrong arguments.")
        #WIP


@bot.command()
async def coin(ctx,*args):
    message = ""
    count = 1
    total = 0

    if len(args) > 1:
        return "`.coin` accepts one argument only! (**.coin <Repeats>**)"
    elif len(args) == 1:
        if args[0].isnumeric():
            count = max(1, int(args[0]))
        else: return "Argument must be a whole number! (**.coin <Repeats>**)"

    for i in range(count):
        if random.randint(0,1):
            message += "yes "
            total += 1
        else: message += "no "

    if count > 1:
        message += "\nTotal sum: **" + str(total) + "**"
    #await ctx.send(message)
    await p(ctx,message)


@bot.command()
async def rng(ctx,*args):
    message = ""
    total = 0

    if len(args) > 2:
        await ctx.send("`.rng` accepts two arguments only! (**.rng <Max number> <Repeats>**)")
    elif len(args) == 0:
        await ctx.send("`.rng` requires at least one argument, with a optional second argument! (**.rng <Max number> <Repeats>**)")
        return
    else:
        args = list(args) + ["1"]
        if args[0].isnumeric() and args[1].isnumeric():
            maxn = max(0, int(args[0]))
            count = max(1, int(args[1]))
        else:
            await ctx.send("Arguments must be a whole number! (**.rng <Max number> <Repeats>**)")
            return

    for i in range(count):
        tmp = random.randint(0,maxn)
        message += str(tmp) + " "
        total += tmp

    if count > 1:
        message += "\nTotal sum: **" + str(total) + "**"
    #await ctx.send(message)
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
async def news(ctx):
    await ctx.send("there is supposed to be a news feeds")


print("test")

keep_alive()
bot.run(TOKEN)
