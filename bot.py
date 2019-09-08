#---
#TODO: Read token and prefix from json file
#TODO: Create a tool to read sprague classes from a file, create categories and chats for them, and roles for each class
#TODO: Censorship warning system
#TODO: Connect to a student database to auto-assign roles and nick-names?
#      (Doubt we would get access to that if it does exist)
#TODO: Try to make this ass professional as possible :)
#---

import sys
import json
import discord
from discord.ext import commands


token = 'NjE5OTI3MzM5NzM1ODQyODI3.XXUyMA.4e5syQqzbXv2t2X6_m8-CraHNjU'
prefix = '!'


client = commands.Bot(command_prefix=prefix)

startsWith = '!'


@client.event
async def on_ready():
    print('Logged in as: ', client.user.name)
    print('ID: ', client.user.id)
    print('Using discord.py version: ', discord.__version__)
    print('Running on python version: ', sys.version.split(' ')[0])
    print('Ready to use\n')


@client.event
async def on_message(message):
    if message.content.startswith(startsWith):
        print('hey')

client.run(token)
