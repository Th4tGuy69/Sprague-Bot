#---
#TODO: Auto-post announcements to #annuoncements channel daily
#TODO: Censorship warning system
#TODO: Connect to a student database to auto-assign roles and nick-names? Same system that does schedule changes with
#      student ID, first letter of last name, email, etc. (Doubt we would get access... unless..?)
#TODO: Try to make this ass professional as possible :) - IN PROGRESS
#---

import sys
import json
import discord
from discord.ext import commands


with open('info.json', 'r') as json_file:
    data = json.load(json_file)
    for j in data['info']:
        token = j['token']
        prefix = j['prefix']
    json_file.close()


client = commands.Bot(command_prefix=prefix)


@client.event
async def on_ready():
    print('\nLogged in as: ', client.user.name)
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


client.run(token)
