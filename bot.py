import discord
client = discord.Client()
import os
import requests
import json
from keep_alive import keep_alive


SERVER = os.environ['SERVER']
key = 0 # command to be run
exact_keys = json.load(open('exact_keys.json',))
#start_keys = json.load(open('start_keys.json',))


# validates if message intends to run command
def valid(message):
    tmpkey = message.split(' ', 1)[0].lower()
    if tmpkey in exact_keys:
        return exact_keys[tmpkey]
    #future start_keys method
    return False


# quote feature
QUOTES = []
def get_quotes(type): # 'random', 'today'
    if type=="today":
        response = requests.get("https://zenquotes.io/api/quotes")
        json_tmp = json.loads(response.text)
        return json_tmp[0]['q'] + " -" + json_tmp[0]['a']
    else:
        global QUOTES
        if len(QUOTES)==0:
            response = requests.get("https://zenquotes.io/api/quotes")
            QUOTES = json.loads(response.text)
        return QUOTES[0]['q'] + " -" + QUOTES[0]['a']


@client.event
async def on_ready():
    """for guild in client.guilds:
        if guild.name != SERVER: continue
        print(f'{client.user} is connected to {guild.name} (ID: {guild.ID}).')"""
    print(f'{client.user} has connected!')


"""#handling errors
@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise"""


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
            txt = txt.strip().split(' ')
    else: return
    
    # update with future switch feature
    if key == -2:
        raise discord.DiscordException

    elif key == -1:
        await message.channel.send('no help for you haha')

    elif key == 1:
        await message.channel.send('Hello!')

    elif key == 2:
        await message.channel.send(get_quotes("random"))
    
    elif key == 3:
        await message.channel.send(get_quotes("today"))
        await message.channel.send("there is supposed to be dailies")

    elif key == 4:
        await message.channel.send("there is supposed to be news feeds")


keep_alive()
client.run(os.environ['TOKEN'])
