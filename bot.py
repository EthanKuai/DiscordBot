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


@bot.command()
async def helpp(ctx):
    message = "**^ represents an optional argument**\n\n"
    for i, (command, description) in enumerate(help_dict.items()):
        message += "```" + command + "``` >> " + description + "\n\n"
    await ctx.send(message)


@bot.command()
async def quote(ctx,*args):
    if args[0]=="today":
        response = requests.get("https://zenquotes.io/api/today")
        json_tmp = json.loads(response.text)
        quote = "**Quote of the day**: *" + json_tmp[0]['q'] + "* -" + json_tmp[0]['a']
    else:
        global QUOTES
        if len(QUOTES)==0:
            response = requests.get("https://zenquotes.io/api/quotes")
            QUOTES = json.loads(response.text)
        quote = "*" + QUOTES[-1]['q'] + "* -" + QUOTES[-1]['a']
        QUOTES.pop()
    await ctx.send(quote)


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
    await ctx.send(message)


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
    await ctx.send(message)


@bot.command()
@commands.is_owner()
async def error(ctx):
    raise discord.DiscordException


@bot.command()
async def hi(ctx):
    await ctx.send(DESC)


@bot.command()
async def daily(ctx):
    await quote(ctx,("today"))
    await ctx.send("there is supposed to be dailies.")


@bot.command()
async def news(ctx):
    await ctx.send("there is supposed to be news feeds")


@bot.command()
async def echo(ctx,*,response):
    response = response.split("\n")
    for line in response:
        if len(line) < MAX_LEN:
            ctx.send(response)
        else:
            i = 0
            while i < len(line):
                ctx.send(line[i: i + MAX_LEN])
                i += MAX_LEN


keep_alive()
bot.run(TOKEN)
