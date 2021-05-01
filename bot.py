import discord
client = discord.Client()
import os
import requests
import json

key = "" # command to be run


# shortcut
def s(txt):
    return txt==key

# validates if message intends to run command
def valid(message):
    tmpkey = message.split(' ', 1)[0]
    return tmpkey

# quote feature
QUOTE_MAX_STR = "Too many requests. Obtain an auth key for unlimited access. -zenquotes.io"
def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    if quote == QUOTE_MAX_STR: return "On cooldown."
    return quote

@client.event
async def on_ready():
    print(f'{client.user} has connected!')

# main chunk
@client.event
async def on_message(message):
    if message.author == client.user:
        return # bot is not a psycho
    
    # validates its a valid command
    if message.content.startswith('.'):
        txt = message.content[1:] # message
        key = valid(txt)
        if not key: return "Invalid command! Use `.help` to get list of available commands."
    else: return
    
    if s('hello') or s('hi') or s('ohayou') or s('bonjour'):
        await message.channel.send('Hello!')
    
    elif s('inspire') or s('quote') or s('inspiration'):
        quote = get_quote()
        await message.channel.send(quote)

client.run(os.environ['TOKEN'])
