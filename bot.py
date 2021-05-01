import discord
client = discord.Client()

import os
TOKEN = os.environ['TOKEN']

@client.event
async def on_ready():
    print(f'{client.user} has connected!')
    print('Alternatively, {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return # bot is not a psycho

    if message.content.startswith('.'):
        await message.channel.send('Hello!')

client.run(TOKEN)
