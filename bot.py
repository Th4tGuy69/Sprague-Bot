# ---
# TODO: Censorship warning system, download image to check for adult content, read text, and keep track of who has recieved warnings and why
# TODO: Connect to a student database to auto-assign roles and nick-names? Same system that does schedule changes with
#      student ID, first letter of last name, email, etc. (Doubt we would get access... unless..?)
# TODO: Try to make this ass professional as possible :) - IN PROGRESS
# ---

#region Imports
import re
import sys
import json
import discord
import requests
import pytesseract
import datetime as dt
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from discord.ext import commands
from sightengine.client import SightengineClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler
#endregion 


emojiA = 'https://i.imgur.com/dmTKeTi.png'
emojiB = 'https://i.imgur.com/oLJnbDL.png'
emojiAB = 'https://i.imgur.com/dVOtgZq.png'
announcements = []
date = ''
dayType = ''
global embed


# Grab bot token and prefix from file, TODO: If we have any actual user commands, make the prefix changable
with open('info.json', 'r') as json_file:
    data = json.load(json_file)
    for j in data['info']:
        token = j['token']
        prefix = j['prefix']
    json_file.close()


client = commands.Bot(command_prefix=prefix)
sight = SightengineClient('1428354798', 'HbyKWBXNC2T96rYbaeGD')


#https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v5.0.0-alpha.20190708.exe
#https://stackoverflow.com/questions/42831662/python-install-tesseract-for-windows-7
#output = pytesseract.image_to_string(Image.open('images/test_image.png').convert("RGB"), lang='eng')
#print(output)


@client.event
async def on_ready():
    print('\nLogged in as: ', client.user.name)
    print('ID: ', client.user.id)
    print('Using discord.py version: ', discord.__version__)
    print('Running on python version: ', sys.version.split(' ')[0])
    print('Ready to use\n')


# Sends new users a message on joining the guild, TODO:Test and replace embed with something more professional
@client.event
async def on_member_join(member):
    embed = discord.Embed(title='*beep boop*',
                          type='rich', description='Bot text')
    await member.send(embed=embed)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif message.attachments != None:
        for a in message.attachments:
            output = sight.check('nudity','wad','offensive','text').set_url(a.proxy_url)
            if output['status'] == 'success':
                #check nudity
                NotImplemented
                #check weapons, alcohol, & drugs
                NotImplemented
                #check offensive
                NotImplemented
                #check text
                if output['text']['has_artificial'] or output['text']['has_natural'] > 0.5:
                    text = pytesseract.image_to_string(Image.open(BytesIO(requests.get(a.proxy_url).content)).convert("RGB"), lang='eng')
                    print(text) #TODO: Check this against a list of 'bad words'
                
                with open('test.json', 'w') as outfile:
                    json.dump(output, outfile, indent=4)


# Web crawler grabs announcements, modifys, then posts to id=619772443116175370
async def postAnnouncements():
    announcements.clear()

    date = str(dt.date.today()).split('-')

    if dt.date.today().weekday() is 1 or 3:
        dayType = 'an **A** day'
    elif dt.date.today().weekday() is 2 or 4:
        dayType = 'a **B** day'
    elif dt.date.today().weekday() is 0:
        dayType = 'an **A/B** day'

    # Web crawler
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
            text = re.sub(r'\s+', ' ', text)

            announcements.append(text)

    # Embed setup
    embed = discord.Embed(title='Announcements for **{}/{}/{}**, {}.'.format(date[1].replace(
        '0', ''), date[2], date[0][2:], dayType), type='rich', url='http://spragueannouncements.blogspot.com/', color=0xf04923)
    embed.set_author(name='Sprague Bot', url='https://github.com/Th4tGuy69/Sprague-Bot',
                     icon_url='http://spraguehs.com/images/oly-logos/Victory%20O%20Orange.png')
    embed.set_footer(text='Remember to make it a great day, everybody!')
    if dt.date.today().weekday() is 1 or 3:
        embed.set_thumbnail(url=emojiA)
    elif dt.date.today().weekday() is 2 or 4:
        embed.set_thumbnail(url=emojiB)
    elif dt.date.today().weekday() is 0:
        embed.set_thumbnail(url=emojiAB)
    for announcement in announcements:
        try:
            embed.add_field(name='⸻\t\t\t⸻\t\t\t⸻\t\t\t⸻\t\t\t⸻',
                            value=announcement, inline=False)
        finally:
            pass

    await client.get_channel(619772443116175370).send(embed=embed)


# Scheduled posting of announcements
scheduler = AsyncIOScheduler()
scheduler.add_job(postAnnouncements, trigger='cron',
                  day_of_week='mon-fri', hour=7)
scheduler.start()


client.run(token)
