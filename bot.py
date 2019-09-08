#---
#TODO: Read token and prefix from json file
#TODO: Create a tool to read sprague classes from a file, create categories and chats for them, and roles for each class
#TODO: Censorship warning system
#TODO: Connect to a student database to auto-assign roles and nick-names? Same system that does schedule changes with
#      student ID, first letter of last name, email, etc. (Doubt we would get access... unless..?)
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


@client.event #Sends new users a message on joining the guild, TODO:Test
async def on_member_join(member):
    embed = discord.Embed(title='*beep boop*', type='rich', description='Bot text')
    await member.send(embed=embed)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif message.content.startswith(startsWith):
        if 'join' in message.content:
            embed = discord.Embed(title='*beep boop*', type='rich', description='Bot text')
            await message.author.send(embed=embed)


client.run(token)
