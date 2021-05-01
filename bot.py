import discord
client = discord.Client()
import os
import requests
import json
from keep_alive import keep_alive

TOKEN = os.environ['TOKEN']
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
def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    if quote.startswith("Too many requests."): return "On cooldown."
    return quote

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name != SERVER: continue
        print(f'{client.user} is connected to {guild.name} (ID: {guild.ID}).')
        members = '\n - '.join([member.name for member in guild.members])
        print(f'Guild Members:\n - {members}')
    print(f'{client.user} has connected!')

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
    
    if key == 0:
        await message.channel.send('no help for you haha')

    elif key == 1:
        await message.channel.send('Hello!')

    elif key == 2:
        await message.channel.send(get_quote())
    
    elif key == 3:
        await message.channel.send("there is supposed to be dailies")

    elif key == 4:
        await message.channel.send("there is supposed to be news feeds")

keep_alive()
client.run(TOKEN)
