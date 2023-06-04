import os
import openai
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
# Carregar a chave de API da OpenAI dos ambientes
openai.api_key = os.getenv('OPENAI_API_KEY')

def chatgpt_generate(text: str) -> str:
    prompt = 'Usuário: A partir dos seguintes trechos aletórios extraidos de um site, gere um parágrafo de texto sobre o tema: """' + text + '""""\nChatbot: '
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.7
    )
    return response.choices[0].text.strip()