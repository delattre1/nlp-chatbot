import os
import json
import discord
import requests
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

if not DISCORD_TOKEN:
    raise Exception("DISCORD TOKEN is not defined. Please verify the file '/src/.env'")


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
    print('The bot is running!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!run'):
        msg = message.content 
        split = msg.split(' ')

        if (len(split) == 2) and (split[1] == 'zen'):
            quote = get_quote()
            await message.channel.send(f'Here is a zen message for you: \n"{quote}"')
            return

        await message.channel.send(f"Command '!run' expected argument 'zen'.\nSend '!run zen' to get a cool zen message!")

    elif message.content.startswith('!source'):
        await message.channel.send('Here is the source code: https://github.com/delattre1/nlp-chatbot')

    elif message.content.startswith('!author'):
        await message.channel.send('Here is the info about the author: Daniel Delattre, danielcd3@al.insper.edu.br')

    elif message.content.startswith('!help'):
        HELP_MESSAGE  =  "Use the command: '!source'  to get the link to the source code.\n"
        HELP_MESSAGE +=  "Use the command: '!author'  to get the information about the author.\n"
        HELP_MESSAGE +=  "Use the command: '!help'    to get the description of available commands\n"
        HELP_MESSAGE +=  "Use the command: '!run zen' to get a zen message, and make your day better. The data is originated from: 'https://zenquotes.io'\n"
        await message.channel.send(HELP_MESSAGE)

    else:
        #await message.channel.send(f"Intent not identified. Received: '{message.content}'")
        print(f"Intent not identified. Received: '{message.content}'")


if __name__ == '__main__':
    client.run(DISCORD_TOKEN)