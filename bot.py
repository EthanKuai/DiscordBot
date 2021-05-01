import discord
client = discord.Client()
import os
import requests
import json

def s(message, key):
    return message.startswith(key)

QUOTE_MAX_STR = "Too many requests. Obtain an auth key for unlimited access. -zenquotes.io"
def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    if quote == QUOTE_MAX_STR:
        return "On cooldown."
    return quote

@client.event
async def on_ready():
    print(f'{client.user} has connected!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return # bot is not a psycho
    
    if message.content.startswith('.'):
        txt = message.content[1:]
    else:
        return # not a command
    
    if s(txt,'hello') or txt.startswith('hi') or txt.startswith('ohayou') or txt.startswith('bonjour'):
        await message.channel.send('Hello!')
    
    if txt.startswith('inspire'):
        quote = get_quote()
        await message.channel.send(quote)

client.run(os.environ['TOKEN'])
