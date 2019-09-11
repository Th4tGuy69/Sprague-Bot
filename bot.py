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
import itertools
from discord.ext import commands


class Cat:
    def __init__(self, name, list subs):
        self.catName = name
        self.subCats = []
        self.subCats += subs


cats = []

with open('info.json', 'r') as json_file:
    data = json.load(json_file)
    for j in data['info']:
        token = j['token']
        prefix = j['prefix']
    json_file.close()

with open('classes.txt', 'r') as file:
    lineCount = 25
    lines = []
    for l in range(lineCount):
        lines.append(file.readline())
    for l in range(lineCount):
        subs = []
        category = ''
        if lines[l].endswith(' I\n'):
            category = lines[l].replace(' I\n', '')
            subs.append(lines[l].replace('\n', ''))
            try:
                if category and ' II\n' in lines[l+1]:
                    subs.append(lines[l+1].replace('\n', ''))
                if category and ' III\n' in lines[l+2]:
                    subs.append(lines[l+2].replace('\n', ''))
                if category and ' IV\n' in lines[l+3]:
                    subs.append(lines[l+3].replace('\n', ''))
                
                cats.append(Cat(category, subs))
            except:
                pass
        elif lines[l].endswith(' II\n'):
            pass
        elif lines[l].endswith(' III\n'):
            pass
        elif lines[l].endswith(' IV\n'):
            pass
        else:
            cats.append(Cat(lines[l].replace('\n', ''), None))
    file.close()

with open('catClasses.txt', 'w') as file:
    for c in cats:
        file.write('Cat Name: {} | Sub Cats : {}\n'.format(c.catName, c.subCats))
    file.close()

for c in cats:
    print(c.subCats)


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
            await message.channel.send(content='Creating...')

            for c in cats: 
                global createdCategories
                global createdRoles
                global createdText
                global createdVoice
                category = await message.guild.create_category_channel(name=c.catName, reason='Automajically generated')
                createdCategories.append(category)
                await category.set_permissions(message.guild.default_role, overwrite=overwrite1, reason='bbbrole')
                if len(c.subCats) > 1: 
                    genText = await category.create_text_channel(name='General Chat', topic='Chat for students of ' + c.catName, reason='m')
                    createdText.append(genText)
                    genVoice = await category.create_voice_channel(name='Voice Chat', reason='Lebron Jamas')
                    createdVoice.append(genVoice)
                    await genText.set_permissions(message.guild.default_role, overwrite=overwrite1, reason='bbbrole')
                    await genVoice.set_permissions(message.guild.default_role, overwrite=overwrite1, reason='bbbrole')
                    for r in c.subCats:
                        role = await message.guild.create_role(name=r, reason='bbbrole')
                        createdRoles.append(role)
                        text = await category.create_text_channel(name=r, topic='Chat for students in ' + r, reason='m')
                        createdText.append(text)
                        await text.set_permissions(message.guild.default_role, overwrite=overwrite1, reason='bbbrole')
                        await text.set_permissions(role, overwrite=overwrite2, reason='bbbrole')
                        await genText.set_permissions(role, overwrite=overwrite2, reason='bbbrole')
                        await genVoice.set_permissions(role, overwrite=overwrite2, reason='bbbrole')
                else:
                    role = await message.guild.create_role(name=c.catName, reason='bbbrole')
                    await category.set_permissions(role, overwrite=overwrite2, reason='bbbrole')
                    text = await category.create_text_channel(name=c.catName, topic='Chat for students in ' + c.catName, reason='m')
                    voice = await category.create_voice_channel(name='Voice Chat', reason='Lebron Jamas')
                    createdRoles.append(role)
                    createdText.append(text)
                    createdVoice.append(voice)

            await message.channel.send(content='Done! Use `!undo` to undo that mess I just made')


        if 'undo' in message.content: #Undoes any and all classes created by the previous function
            await message.channel.send(content='Undoing...')

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

            await message.channel.send(content='Done!')

            createdRoles = []
            createdCategories = []
            createdVoice = []
            createdText = []


client.run(token)
