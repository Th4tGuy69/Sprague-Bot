import sys
import json
import discord
from discord.ext import commands

token = 'NjE5OTI3MzM5NzM1ODQyODI3.XXPraQ.ZlrOW7eFbTrbbi6Xh2aYuo9bkck'
prefix = '!' #read token and prefix from json file


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
