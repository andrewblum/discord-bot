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


def make_chains(message_list):
    """Take list of strings; return dictionary of Markov chains."""

    chains = {}
    for message in message_list:
        message = message.split()
        if len(message) < 3:
            continue
        for i in range(len(message) - 2):
            key = (message[i], message[i + 1])
            value = message[i + 2]
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


def get_all_channels():
    channels = []
    for channel in client.get_all_channels():
        if channel.type == discord.ChannelType.text:
            channels.append(channel)
    return channels

async def get_all_users_messages(username, limit=None, channels=None):
    """ Get all of username's messages, up to LIMIT number of messages, from list of channels. 
        If limit not provided, will get all. 
        If channels not provided, will search all channels.
    """

    if not channels:
        channels = get_all_channels()

    counter = 0
    messages = []
    for channel in channels:
        async for message in channel.history(limit=limit):
            if message.author.name == username:
                messages.append(message)
                counter += 1
    print(f"Completed retriving {username}'s messages, {counter} in total")
    return messages


def clean_messages(messages):
    cleaned_messages = []
    for message in messages: 
        cleaned_message = message.clean_content
        cleaned_message = discord.utils.escape_markdown(cleaned_message)
        cleaned_messages.append(cleaned_message)
    return cleaned_messages


def username_from_command(message):
    message_as_list = message.clean_content.split()
    if len(message_as_list) < 2: 
        return None
    return message_as_list[1]

# Get the filenames from the user through a command line prompt, ex:
# python markov.py green-eggs.txt shakespeare.txt
# filenames = sys.argv[1:]
# Open the files and turn them into one long string
# text = open_and_read_file(filenames)
# Get a Markov chain
# chains = make_chains(text)

client = discord.Client()
user_chains = {}
prefix = "$"

@client.event
async def on_ready():
    print(f'Successfully connected! Logged in as {client.user}.')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(prefix):
        if message.content.startswith(prefix + "hello"):
            await message.channel.send("Hello!")

        elif message.content.startswith(prefix + "clone"):
            username = username_from_command(message)
            if not username:
                await message.channel.send(f"Include a valid username, like $clone vodka")
            else:
                await message.channel.send(f"Building a fake {username}")
                all_users_messages = await get_all_users_messages(username)
                cleaned_messages = clean_messages(all_users_messages)
                user_chains[username] = make_chains(cleaned_messages)

        elif message.content.startswith(prefix + "speak"):
            username = username_from_command(message)
            if not username: 
                await message.channel.send(f"Include a valid username, like $speak vodka")
            elif username not in user_chains:
                await message.channel.send(f"Clone them first")
            else:
                await message.channel.send(make_text(user_chains[username]))


client.run(os.environ['DISCORD_TOKEN'])