import os
import json
import asyncio
import discord
import traceback
import requests
from dotenv import load_dotenv
from classes.crawler import Crawler
from classes.reverse_index import ReverseIndex
from classes.openai import chatgpt_generate
from structlog import get_logger
from concurrent.futures import ThreadPoolExecutor
from utils import create_s3_connection
from utils import load_dict

log = get_logger()
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CACHE_DIR = 'cache'

if not DISCORD_TOKEN:
    raise Exception("DISCORD TOKEN is not defined. Please verify the file '/src/.env'")

S3 = create_s3_connection()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)

def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return(quote)


def crawl(url: str):
    try:
        crawler = Crawler(s3_connection=S3)
        crawler.crawl(url=url)
        return True
    except Exception as err:
        print(f"Failed to crawl url '{url}'.\nError: {err}")
        traceback.print_exc()
        return False

def build_reverse_index():
    try:
        rev_idx = ReverseIndex()
        rev_idx.build_reverse_index(s3_connection=S3)
        return True
    except Exception as err:
        log.error("Failed to create rev_index.", error=str(err))
        traceback.print_exc()
        return False

def search(words: list[str], threshold: float = None) -> list[str]:
    try:
        rev_idx = ReverseIndex()
        res = rev_idx.search_words(words)
        if res is None:
            return False, 'Term not found'

        sorted_res, not_found = res
        log.info('Finished search', sorted_res=sorted_res, not_found=not_found)
        related_websites = [k for k,v in sorted_res.items()]
        if threshold:
            dic_texts = load_dict(f'{CACHE_DIR}/dic_texts.json')
            related_websites = [url for url in related_websites if dic_texts.get(url) and dic_texts.get(url)['sentiment'] > threshold]
        return True, related_websites

    except:
        traceback.print_exc()
        return False, []

def wn_search(word: str, threshold: int = None) -> list[str]:
    try:
        rev_idx = ReverseIndex()
        res = rev_idx.wn_search_word(word)
        if res is None:
            return False, 'Term not found'

        sorted_res, not_found = res
        log.info('Finished search', sorted_res=sorted_res, not_found=not_found)
        related_websites = [k for k,v in sorted_res.items()]

        if threshold:
            dic_texts = load_dict(f'{CACHE_DIR}/dic_texts.json')
            related_websites = [url for url in related_websites if dic_texts.get(url) and dic_texts.get(url)['sentiment'] > threshold]

        return True, related_websites
    except:
        traceback.print_exc()
        return False, []

def generate(words: list[str]):
    try:
        rev_idx = ReverseIndex()
        res = rev_idx.search_words(words)
        if res is None:
            return False, 'Term not found'

        sorted_res, not_found = res
        log.info('Finished search (generate)', sorted_res=sorted_res, not_found=not_found)
        dic_texts = load_dict(f'{CACHE_DIR}/dic_texts.json')
        N = 5
        content = [dic_texts[k]['content'] for k in sorted_res.keys()][:N]
        content = ' '.join([i[:15] for i in content])
        content = chatgpt_generate(text=content)
        return True, content

    except:
        traceback.print_exc()
        return False, []

@client.event
async def on_ready():
    print('The bot is running!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Threshold handler
    content = message.content.strip()
    threshold = None

    try:
        split = content.split('th=')
        if len(split) > 2:
            await message.channel.send(f'Wrong usage. Please send "!search [term-1, term-2, ..., term-n] th=0.X".\nE.g "!search smashed potatoes th=0.3"\nE.g "!search cars th=0.4"')

        if len(split) == 2:
            content, threshold = split   
            threshold = float(threshold)
    except:
        await message.channel.send(f'Wrong usage. Please send "!search [term-1, term-2, ..., term-n] th=0.X".\nE.g "!search smashed potatoes th=0.3"\nE.g "!search cars th=0.4"')
        return


    if content.startswith('!run'):
        msg = message.content 
        split = msg.split(' ')

        if (len(split) == 2) and (split[1] == 'zen'):
            quote = get_quote()
            await message.channel.send(f'Here is a zen message for you: \n"{quote}"')
            return
        await message.channel.send(f"Command '!run' expected argument 'zen'.\nSend '!run zen' to get a cool zen message!")


    elif content.startswith('!crawl'):
        split = content.split(' ')
        if len(split) != 2:
            await message.channel.send(f'Wrong usage. Please send "!crawl [url_link]".\nE.g "!crawl https://google.com"')
            return

        url = split[1]
        await message.channel.send(f"Started crawling process for url")#": '{url}'")
        is_success = crawl(url)
        if is_success:
            await message.channel.send(f"Success crawling url\nStarted creating the reverse_index")

            loop = asyncio.get_event_loop()
            is_success_build_rev_idx = await loop.run_in_executor(ThreadPoolExecutor(), build_reverse_index)
            if is_success_build_rev_idx:
                await message.channel.send(f"Success creating the reverse index")
            else:
                await message.channel.send(f"Failed to create reverse index due to internal server error!")
        else:
            await message.channel.send(f"Crawling failed due to internal server error!")


    elif content.startswith('!search'):
        split = content.split(' ')
        if len(split) < 2:
            await message.channel.send(f'Wrong usage. Please send "!search [term-1, term-2, ..., term-n]".\nE.g "!search smashed potatoes"\nE.g "!search cars"')
            return

        words = split[1:]
        print("started sorted_res 1")
        log.info('Started search', words=words)
        await message.channel.send(f"Started search process for words: '{', '.join(words)}'")
        is_success, related_websites = search(words, threshold)
        if not is_success:
            if related_websites:
                error_message = related_websites
                await message.channel.send(f"Search failed due to: '{error_message}'")
            else:
                await message.channel.send(f"Search failed due to internal server error!")
            return

        N = 5
        top_n = '- https://'+'\n- https://'.join(related_websites[:N])
        content = f"Top {N} websites related to your search:\n{top_n}"
        await message.channel.send(content)


    elif content.startswith('!wn_search'):
        split = content.split(' ')
        if len(split) != 2:
            await message.channel.send(f'Wrong usage. Please send "!wn_search [term (in portuguese)]".\nE.g "!wn_search batatas"\nE.g "!wn_search carros"')
            return

        word = split[1]
        print("started sorted_res 1")
        log.info('Started search', word=word)
        await message.channel.send(f"Started search process for word: '{word}'")
        is_success, related_websites = wn_search(word, threshold)
        if not is_success:
            if related_websites:
                error_message = related_websites
                await message.channel.send(f"WN Search failed due to: '{error_message}'")
            else:
                await message.channel.send(f"WN Search failed due to internal server error!")
            #await message.channel.send(f"wn_search failed due to internal server error!")
            await message.channel.send(f'Please send "!wn_search [term (in portuguese)]".\nE.g "!wn_search batatas"\nE.g "!wn_search carros"')
            return

        N = 5
        top_n = '- https://'+'\n- https://'.join(related_websites[:N])
        content = f"Top {N} websites related to your search:\n{top_n}"
        await message.channel.send(content)

    elif content.startswith('!generate'):
        split = content.split(' ')
        if len(split) < 2:
            await message.channel.send(f'Wrong usage. Please send "!generate [term-1, term-2, ..., term-n]".\nE.g "!generate smashed potatoes"\nE.g "!generate cars"')
            return

        words = split[1:]
        print("started sorted_res 1")
        log.info('Started generate', words=words)
        await message.channel.send(f"Started generate process for words: '{', '.join(words)}'")
        is_success, website_content = generate(words)

        if not is_success:
            if website_content:
                error_message = website_content
                await message.channel.send(f"generate failed due to: '{error_message}'")
            else:
                await message.channel.send(f"generate failed due to internal server error!")
            return

        content = f"Random generated phrase from websites related to your terms:\n{website_content}"
        await message.channel.send(content)        

    elif content.startswith('!source'):
        await message.channel.send('Here is the source code: https://github.com/delattre1/nlp-chatbot')


    elif content.startswith('!author'):
        await message.channel.send('Here is the info about the author: Daniel Delattre, danielcd3@al.insper.edu.br')


    elif content.startswith('!help'):
        HELP_MESSAGE  =  "Use the command: '!source'  to get the link to the source code.\n"
        HELP_MESSAGE +=  "Use the command: '!author'  to get the information about the author.\n"
        HELP_MESSAGE +=  "Use the command: '!help'    to get the description of available commands\n"
        HELP_MESSAGE +=  "Use the command: '!run zen' to get a zen message, and make your day better. The data is originated from: 'https://zenquotes.io'\n"
        HELP_MESSAGE +=  'Use the command: \'!crawl [url]\' to crawl webpages. E.g "!crawl https://google.com"\n'
        HELP_MESSAGE += f"\nUse the command: '!search [term-1, term-2, ..., term-n]'.\n- E.g '!search smashed potatoes'\n- E.g '!search cars'\n"
        HELP_MESSAGE += f"\nUse the command: '!wn_search [term (in portuguese)]'.\n- E.g '!wn_search batatas'\n- E.g '!wn_search carros'\n"
        HELP_MESSAGE += f"\nObs: you can add 'th' parameter to filter only positive results from 'search' and 'wn_search'.\n- E.g '!search cars th=0.3'\n"
        HELP_MESSAGE += f"\nUse the command: '!generate [term-1, term-2, ..., term-n]'.\n- E.g '!generate smashed potatoes'\n- E.g '!generate cars'\n"
        await message.channel.send(HELP_MESSAGE)


    else:
        #await message.channel.send(f"Intent not identified. Received: '{message.content}'")
        print(f"Intent not identified. Received: '{message.content}'")


if __name__ == '__main__':
    client.run(DISCORD_TOKEN)