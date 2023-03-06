import discord
import os
import requests
import json
from dotenv import load_dotenv


load_dotenv()
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)

def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return(quote)


@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name='A Cidade dos Robôs')
    channel = discord.utils.get(guild.text_channels, name='teste-daniel')
    await channel.send('The bot is running!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!run'):
        quote = get_quote()
        await message.channel.send(f'Here is a zen message for you: \n"{quote}"')

    elif message.content.startswith('!source'):
        await message.channel.send('Here is the source code: https://github.com/delattre1/nlp-chatbot')

    elif message.content.startswith('!author'):
        await message.channel.send('Here is the info about the author: Daniel Delattre, danielcd3@al.insper.edu.br')

    else:
        #await message.channel.send(f"Intent not identified. Received: '{message.content}'")
        print(f"Intent not identified. Received: '{message.content}'")

client.run(os.getenv('DISCORD_TOKEN'))