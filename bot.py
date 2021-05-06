import discord
import logging
from discord.ext import commands
from keep_alive import keep_alive
import os

import requests
import json
import random

MAX_LEN = 1950
TOKEN = os.environ['TOKEN']
SERVER = os.environ['SERVER']
DESC = "Hi I am Pseudo, a personal discord bot. Currently in development."

bot = commands.Bot(command_prefix = '.', description = DESC)
help_dict = json.load(open('help.json',))


@bot.command()
async def help(ctx):
    message = "**^ represents an optional argument**\n\n"
    for i, (command, description) in enumerate(help_dict.items()):
        message += "```" + command + "``` >> " + description + "\n\n"
    await ctx.send(message)


QUOTES = []
@bot.command()
async def quote(ctx,args):
    if args=="today":
        response = requests.get("https://zenquotes.io/api/today")
        json_tmp = json.loads(response.text)
        quote = json_tmp[0]['q'] + " -" + json_tmp[0]['a']
    else:
        global QUOTES
        if len(QUOTES)==0:
            response = requests.get("https://zenquotes.io/api/quotes")
            QUOTES = json.loads(response.text)
        quote = QUOTES[-1]['q'] + " -" + QUOTES[-1]['a']
        QUOTES.pop()
    await ctx.send(quote)


@bot.command()
async def coin(ctx,args):
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
async def rng(ctx,args):
    message = ""
    total = 0

    if len(args) > 2:
        return "`.rng` accepts two arguments only! (**.rng <Max number> <Repeats>**)"
    elif len(args) == 0:
        return "`.rng` requires at least one argument, with a optional second argument! (**.rng <Max number> <Repeats>**)"
    else:
        args.append("1")
        if args[0].isnumeric() and args[1].isnumeric():
            maxn = max(0, int(args[0]))
            count = max(1, int(args[1]))
        else: return "Arguments must be a whole number! (**.rng <Max number> <Repeats>**)"

    for i in range(count):
        tmp = random.randint(0,maxn)
        message += str(tmp) + " "
        total += tmp
    
    if count > 1:
        message += "\nTotal sum: **" + str(total) + "**"
    await ctx.send(message)


@bot.command()
async def error(ctx):
    raise discord.DiscordException


@bot.command()
async def hi(ctx):
    await ctx.send(DESC)


@bot.command()
async def daily(ctx):
    quote(ctx,"today")
    await ctx.send("there is supposed to be dailies.")


@bot.command()
async def news(ctx):
    await ctx.send("there is supposed to be news feeds")


async def sendMessage(ctx,response):
    responses = []
    if len(response) < MAX_LEN:
        responses.append(response)
    else:
        i = 0
        while i < len(response):
            responses.append(response[i: i + MAX_LEN])
            i += MAX_LEN
    
    for i in responses:
        await ctx.send(i)


keep_alive()
bot.run(TOKEN)
