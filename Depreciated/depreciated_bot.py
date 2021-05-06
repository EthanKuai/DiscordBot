import discord
import os
import requests
import json
from keep_alive import keep_alive
import random


client = discord.Client()
TOKEN = os.environ['TOKEN']
SERVER = os.environ['SERVER']
key = 0 # command to be run
exact_keys = json.load(open('exact_keys.json',))
#start_keys = json.load(open('start_keys.json',))
help_dict = json.load(open('help.json',))
MAX_LEN = 1950


# validates if message intends to run command
def valid(message):
    tmpkey = message.split(' ', 1)[0].lower()
    if tmpkey in exact_keys:
        return exact_keys[tmpkey]
    #future start_keys method
    return False


# help command
def help():
    message = "**^ represents an optional argument**\n\n"
    for i, (command, description) in enumerate(help_dict.items()):
        message += "```" + command + "``` >> " + description + "\n\n"
    return message


# quote command
QUOTES = []
def get_quotes(type): # 'random', 'today'
    if type=="today":
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
    return quote


# coin command
def coin(txt):
    message = ""
    count = 1
    total = 0

    if len(txt) > 1:
        return "`.coin` accepts one argument only! (**.coin <Repeats>**)"
    elif len(txt) == 1:
        if txt[0].isnumeric():
            count = max(1, int(txt[0]))
        else: return "Argument must be a whole number! (**.coin <Repeats>**)"

    for i in range(count):
        if random.randint(0,1):
            message += "yes "
            total += 1
        else: message += "no "
    
    if count > 1:
        message += "\nTotal sum: **" + str(total) + "**"
    return message


# rng command
def rng(txt):
    message = ""
    total = 0

    if len(txt) > 2:
        return "`.rng` accepts two arguments only! (**.rng <Max number> <Repeats>**)"
    elif len(txt) == 0:
        return "`.rng` requires at least one argument, with a optional second argument! (**.rng <Max number> <Repeats>**)"
    else:
        txt.append("1")
        if txt[0].isnumeric() and txt[1].isnumeric():
            maxn = max(0, int(txt[0]))
            count = max(1, int(txt[1]))
        else: return "Arguments must be a whole number! (**.rng <Max number> <Repeats>**)"

    for i in range(count):
        tmp = random.randint(0,maxn)
        message += str(tmp) + " "
        total += tmp
    
    if count > 1:
        message += "\nTotal sum: **" + str(total) + "**"
    return message


# startup
@client.event
async def on_ready():
    """for guild in client.guilds:
        if guild.name != SERVER: continue
        print(f'{client.user} is connected to {guild.name} (ID: {guild.ID}).')"""
    print(f'{client.user} has connected!')


#handling errors
@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else: raise


# main chunk
@client.event
async def on_message(message):
    if message.author == client.user:
        return # bot is not a psycho
    
    # validates its a valid command
    if message.content[0] == ".":   
        txt = message.content[1:] # message
        key = valid(txt)
        if not key:
            message.channel.send("Invalid command! Use `.help` to get a list of available commands.")
            return
        else:
            txt = txt.strip().split(' ')[1:]
            response = ""
    else: return
    
    # update with future switch feature
    if key == -2: # error
        raise discord.DiscordException
    elif key == -1: # help
        response = help()
    elif key == 1: # hi
        response = "Hello! I am Pseudo, a personal discord bot"
    elif key == 2: # quote
        response = get_quotes("random")
    elif key == 3: # daily
        response = get_quotes("today") + "\n there is supposed to be dailies"
    elif key == 4: # news
        response = "there is supposed to be news feeds"
    elif key == 5: # coin
        response = coin(txt)
    elif key == 6: #rng
        response = rng(txt)
    
    else:
        print("how did error 2048 happen?")
        raise discord.DiscordException
    
    responses = []
    if len(response) < MAX_LEN:
        responses.append(response)
    else:
        i = 0
        while i < len(response):
            responses.append(response[i: i + MAX_LEN])
            i += MAX_LEN
    
    for i in responses:
        await message.channel.send(i)


keep_alive()
client.run(TOKEN)
