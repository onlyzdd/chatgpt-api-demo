import argparse
import os
import readline
from typing import List, Optional

import openai
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

OPENAI_MODEL = 'gpt-3.5-turbo'
OPTIONS = {
    'H': 'HELP',
    'HELP': 'HELP',
    'Q': 'QUIT',
    'QUIT': 'QUIT',
    'R': 'RESET',
    'RESET': 'RESET',
}

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.proxy = os.getenv('OPENAI_PROXY')
console = Console()


def get_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument('--disable-stream', action='store_false', default=False, help='disable stream-style output')
    return parser.parse_args()


def print_help():
    print('Usage: ')
    print('  H or HELP to show this message')
    print('  R or RESET to clear ChatGPT context')
    print('  Q or QUIT to exit ChatGPT')
    print('  [question] to get your answer')
    print('')


def complete(history: Optional[List] = None, stream: bool = True):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{'role': 'user', 'content': question} for question in history],
        stream=stream,
    )
    if stream:
        console.print('[bold green]Answer:[/] ')
        start_line = False
        for block in completion:
            content = block['choices'][0]['delta'].get('content', '')
            if not start_line:
                if len(content.strip()):
                    start_line = True
                    print(content.lstrip(), end='', flush=True)
            else:
                print(content, end='', flush=True)
    else:
        console.print('[bold green]Answer:[/] ')
        markdown = Markdown(completion['choices'][0]['message']['content'].strip())
        console.print(markdown)
    print('\n')


def main():
    opts = get_opts()
    if openai.api_key is None:
        print('OPENAI_API_KEY is not set, please check.')
        exit(1)
    print_help()
    history = []
    while True:
        question = console.input('[bold yellow]Question:[/]\n').strip()
        if not question:
            continue
        option = OPTIONS.get(question.upper(), '')
        if option == 'RESET':
            history.clear()
            print()
            continue
        if option == 'QUIT':
            print()
            break
        if option == 'HELP':
            print_help()
            continue
        history.append(question)
        complete(history, stream=not opts.disable_stream)


if __name__ == '__main__':
    main()
