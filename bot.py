import os
import sys
import discord
from random import choice


def open_and_read_file(filenames):
    """Take list of files. Open them, read them, and return one long string."""

    body = ''
    for filename in filenames:
        text_file = open(filename)
        body = body + text_file.read()
        text_file.close()
    return body


def make_chains(text_string):
    """Take input text as string; return dictionary of Markov chains."""

    chains = {}
    words = text_string.split()
    for i in range(len(words) - 2):
        key = (words[i], words[i + 1])
        value = words[i + 2]
        if key not in chains:
            chains[key] = []
        chains[key].append(value)
    return chains


def make_text(chains, char_limit=None):
    """Take dictionary of Markov chains; return random text."""

    keys = list(chains.keys())
    key = choice(keys)
    words = [key[0], key[1]]
    while key in chains:
        if char_limit and len(' '.join(words)) > char_limit:
            break
        # Note that for long texts (like a full book), this might mean
        # it would run for a very long time.
        word = choice(chains[key])
        words.append(word)
        key = (key[1], word)
    return ' '.join(words)

def get_all_users_messages(username, limit=None):
    counter = 0
    messages = []
    async for message in channel.history(limit=limit):
        if message.author.name == username:
            messages.append(message)
            counter += 1
    print(f"Completed retriving {username}'s messages, {counter} in total")
    return messages

# Get the filenames from the user through a command line prompt, ex:
# python markov.py green-eggs.txt shakespeare.txt
filenames = sys.argv[1:]

# Open the files and turn them into one long string
text = open_and_read_file(filenames)

# Get a Markov chain
chains = make_chains(text)
client = discord.Client()


@client.event
async def on_ready():
    print(f'Successfully connected! Logged in as {client.user}.')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
        await message.channel.send(make_text(chains))


client.run(os.environ['DISCORD_TOKEN'])