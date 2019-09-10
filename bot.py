#---
#TODO: Create a tool to read sprague classes from a file - IN PROGRESS
#TODO: Censorship warning system
#TODO: Connect to a student database to auto-assign roles and nick-names? Same system that does schedule changes with
#      student ID, first letter of last name, email, etc. (Doubt we would get access... unless..?)
#TODO: Try to make this ass professional as possible :) - IN PROGRESS
#---

import sys
import json
import discord
from discord.ext import commands


class Cat:
    catName = ''
    subCats = []

    def __init__(self, name, subs):
        self.catName = name
        self.subCats = subs

cats = []

with open('info.json', 'r') as json_file:
    data = json.load(json_file)
    for j in data['info']:
        token = j['token']
        prefix = j['prefix']
    json_file.close()

with open('classes.txt', 'r') as file:
    #lineCount = file.readlines()
    lineCount = 2
    lines = []
    for l in range(lineCount):
        lines.append(file.readline())
        if lines[l].endswith('I') or lines[l].endswith('V'):
            pass
        else:
            cats.append(Cat(lines[l].replace('\n', ''), None))

print('Cat 0 name: ', cats[0].catName, '. Cat 0 subs: ', cats[0].subCats)
print('Cat 1 name: ', cats[1].catName, '. Cat 1 subs: ', cats[1].subCats)
        


client = commands.Bot(command_prefix=prefix)


overwrite1 = discord.PermissionOverwrite(read_messages=False, send_messages=False, connect=False)
overwrite2 = discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True)

createdRoles = []
createdCategories = []
createdVoice = []
createdText = []


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
    elif message.content.startswith(prefix):
        if 'create' in message.content: #Creates a 'class' (category w/ roles, permissions, vc, and text chat)





            for i in range(3):
                global createdCategories
                global createdRoles
                global createdText
                global createdVoice
                category = await message.guild.create_category_channel(name='CLASS', reason='Automajically generated')
                role = await message.guild.create_role(name='TEST')
                await category.set_permissions(message.guild.default_role, overwrite=overwrite1, reason='bbbrole')
                await category.set_permissions(role, overwrite=overwrite2, reason='bbbrole')
                text = await category.create_text_channel(name='Text TEST', reason='m')
                voice = await category.create_voice_channel(name='Voice TEST', reason='Lebron Jamas')
                createdCategories.append(category)
                createdRoles.append(role)
                createdText.append(text)
                createdVoice.append(voice)
        if 'undo' in message.content: #Undoes any and all classes created by the previous function
            i = 0
            while i < len(createdRoles):
                await createdRoles[i].delete(reason='undo')
                i+=1
            i = 0
            while i < len(createdVoice):
                await createdVoice[i].delete(reason='undo')
                i+=1
            i = 0
            while i < len(createdText):
                await createdText[i].delete(reason='undo')
                i+=1
            i = 0
            while i < len(createdCategories):
                await createdCategories[i].delete(reason='undo')
                i+=1

            createdRoles = []
            createdCategories = []
            createdVoice = []
            createdText = []


client.run(token)
