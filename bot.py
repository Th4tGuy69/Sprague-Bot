#---
#TODO: Scrape announcenments using BeautifulSoup and post into #announcements 
#TODO: Censorship warning system
#TODO: Connect to a student database to auto-assign roles and nick-names? Same system that does schedule changes with
#      student ID, first letter of last name, email, etc. (Doubt we would get access... unless..?)
#TODO: Try to make this ass professional as possible :) - IN PROGRESS
#---

import re
import sys
import json
import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands


announcements = []
page = requests.get('http://spragueannouncements.blogspot.com/')


soup = BeautifulSoup(page.content, 'lxml')
whole = soup.find(class_='post-body entry-content')
class_ = whole.find_all('div')
class_.pop(0)
for div in class_:
    if len(div.text) > 3:
        text = div.text
        if '/' in text:
            text = text[:-4]
        text = re.sub(r'\s+',' ',text)

        announcements.append(text)


with open('info.json', 'r') as json_file:
    data = json.load(json_file)
    for j in data['info']:
        token = j['token']
        prefix = j['prefix']
    json_file.close()


client = commands.Bot(command_prefix=prefix)


embed = discord.Embed(title='Today\'s Announcements', type='rich', url='http://spragueannouncements.blogspot.com/', color=0xf04923)
embed.set_author(name='Sprague Bot', url='https://github.com/Th4tGuy69/Sprague-Bot', icon_url='http://spraguehs.com/images/oly-logos/victory-o-orange.svg')
for announcement in announcements:
    try:
        embed.add_field(name='———', value=announcement, inline=False)
    finally:
        pass
embed.set_footer(text=dayType + ' | Make it a great day!')


@client.event
async def on_ready():
    print('\nLogged in as: ', client.user.name)
    print('ID: ', client.user.id)
    print('Using discord.py version: ', discord.__version__)
    print('Running on python version: ', sys.version.split(' ')[0])
    print('Ready to use\n')


@client.event #Sends new users a message on joining the guild, TODO:Test and replace embed with something more professional
async def on_member_join(member):
    embed = discord.Embed(title='*beep boop*', type='rich', description='Bot text')
    await member.send(embed=embed)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif message.content.startswith(prefix):
        if 'ann' in message.content:
            await message.channel.send(embed=embed)


client.run(token)
