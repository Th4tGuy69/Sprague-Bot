# ---
# TODO: Censorship warning system, download image to check for adult content, read text, and keep track of who has recieved warnings and why
# TODO: Connect to a student database to auto-assign roles and nick-names? Same system that does schedule changes with
#      student ID, first letter of last name, email, etc. (Doubt we would get access... unless..?)
# TODO: Try to make this ass professional as possible :) - IN PROGRESS
# ---

# region Imports
import re
import sys
import json
import sqlite3
import discord
import requests
import pytesseract
import datetime as dt
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from discord.ext import commands
from sightengine.client import SightengineClient
from profanity_check import predict, predict_prob
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# endregion


emojiA = 'https://i.imgur.com/dmTKeTi.png'
emojiB = 'https://i.imgur.com/oLJnbDL.png'
emojiAB = 'https://i.imgur.com/dVOtgZq.png'
emojiAnnouncements = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/228/public-address-loudspeaker_1f4e2.png'
emojiExclamation = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/228/double-exclamation-mark_203c.png'
emojiWave = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/228/waving-hand-sign_1f44b.png'
announcements = []
date = ''
dayType = ''

#await openDB()

#sq.execute('''CREATE TABLE warned (first_last text, user_id integer, warnings integer, banned integer)''')
'''
values = [
    ('Caden Garrett', 147926148616159233, 0, False),
    ('Jordan Millett', 271357265913577475, 0, False),
    ('Ethan Hardey', 215663731672088576, 0, False),
    ('Joseph Byers', 242482798986788864, 0, False),
    ('Kyle Rudisil', 193065926206160896, 0, False)
    ]

sq.executemany('INSERT INTO warned VALUES (?,?,?,?)', values)
#sq.execute('SELECT * FROM warned WHERE symbol=?', '')

await closeDB()
'''

async def openDB():
    global db
    global sq
    db = sqlite3.connect('warned.db')
    sq = db.cursor()


async def closeDB():
    db.commit()
    db.close()


# Grab bot token and prefix from file, TODO: If we have any actual user commands, make the prefix changable
with open('info.json', 'r') as json_file:
    data = json.load(json_file)
    for j in data['info']:
        token = j['token']
        prefix = j['prefix']
    json_file.close()


client = commands.Bot(command_prefix=prefix)
sight = SightengineClient('1428354798', 'HbyKWBXNC2T96rYbaeGD')
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'

# https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v5.0.0-alpha.20190708.exe
# https://stackoverflow.com/questions/50951955/pytesseract-tesseractnotfound-error-tesseract-is-not-installed-or-its-not-i

@client.event
async def on_ready():
    print('\nLogged in as: ', client.user.name)
    print('ID: ', client.user.id)
    print('Using discord.py version: ', discord.__version__)
    print('Running on python version: ', sys.version.split(' ')[0])
    print('Ready to use\n')


# Sends new users a message on joining the guild
# TODO: Test
# TODO: Check username for profanity
# TODO: Add new users to SQLite Database
@client.event
async def on_member_join(member):
    '''
    temp = predict([member.name])
    print(temp[0])

    embed = discord.Embed(title='Hello `{}`!'.format(
        member.name), type='rich', color=0xf04923)
    embed.set_author(name='Sprague Bot',
                     url='https://github.com/Th4tGuy69/Sprague-Bot', icon_url=emojiWave)
    embed.set_footer(text='Remember to make it a great day')

    embed.add_field(name='w', value='w')

    await member.send(embed=embed)

    await openDB()
    sq.execute('INSERT INTO warned VALUES (?,?,?,?)',
               (name, member.id, 0, False,))
    await closeDB()
    '''


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif message.attachments != None:
        for a in message.attachments:  # TODO: Doesn't detect image if sent by url
            # a.read(use_cached=True))
            #if a.url != None:
                #NotImplemented
            if True == True:
                responce = requests.get(a.proxy_url)
                img = Image.open(BytesIO(responce.content))
                text = pytesseract.image_to_string(Image.open(BytesIO(requests.get(a.proxy_url).content))) #ughhhhh
                prob = predict_prob([text])
                print(text, ': ', prob, '%: ', a.proxy_url)

                return 0

                output = sight.check('nudity', 'wad', 'offensive',
                                     'text').set_url(a.proxy_url)
                if output['status'] == 'success':
                    offenses = []

                    # check nudity
                    if output['nudity']['raw'] > 0.35:
                        offenses.append('RAW NUDITY')
                    if output['nudity']['partial'] > 0.35:
                        offenses.append('PARTIAL NUDITY')

                    # check weapons, alcohol, & drugs
                    if output['weapon'] > 0.4:
                        offenses.append('WEAPON')
                    if output['alcohol'] > 0.5:
                        offenses.append('ALCOHOL')
                    if output['drugs'] > 0.5:
                        offenses.append('DRUGS')

                    # check offensive
                    if output['offensive']['prob'] > 0.5:
                        offenses.append('OFFENSIVE')

                    # check text
                    '''if output['text']['has_artificial'] or output['text']['has_natural'] > 0.5:
                        text = pytesseract.image_to_string(Image.open(BytesIO(requests.get(a.proxy_url).content)).convert("RGB"), lang='eng')
                        prob = predict_prob([text])
                        print(prob) #TODO: Check this against a list of 'bad words'''

                    if len(offenses) > 0:
                        await message.delete()
                        await Warn(offenses, message, a.proxy_url)

                    with open('test.json', 'w') as outfile:
                        json.dump(output, outfile, indent=4)
                    outfile.close()
                else:
                    NotImplemented  # TODO: Have admins manually review


async def Warn(offences, message, img_url):
    # add to user's warnings, if > 3 then ban
    await openDB()
    sq.execute('SELECT warnings FROM warned WHERE user_id=?',
               (message.author.id,))
    temp = sq.fetchone()
    warnings = temp[0] + 1
    banned = False

    embed = discord.Embed(title='WARNING', type='rich', color=0xf04923)
    embed.set_author(name='Sprague Bot', url='https://github.com/Th4tGuy69/Sprague-Bot',
                     icon_url=emojiExclamation)

    text = 'YOU POSTED AN IMAGE CONTAINING: `{}`'.format(', '.join(offences))

    if warnings == 1:
        embed.add_field(
            name=text, value=':x::heavy_multiplication_x::heavy_multiplication_x:')
    elif warnings == 2:
        embed.add_field(
            name=text, value=':x::x::heavy_multiplication_x:')
    elif warnings >= 3:
        banned = True  # TODO: Ban them fools
        embed.add_field(name=text, value=':x::x::x:')

    embed.set_image(url=img_url)
    embed.set_footer(text='Remember to make it a great day!')

    # TODO: Send to list of admins as documentation
    await message.author.send(embed=embed)

    sq.execute('UPDATE warned SET warnings = ?, banned = ? WHERE user_id=?',
               (warnings, banned, message.author.id,))

    await closeDB()


# Web crawler grabs announcements, modifys, then posts to id=619772443116175370
async def postAnnouncements():
    announcements.clear()

    today = dt.date.today()
    date = str(today).split('-')

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
                     icon_url=emojiAnnouncements)
    time = dt.date(day=today.day, month=today.month, year=today.year).strftime('%A %B %d, %Y')
    embed.set_footer(text='Keep on a\'rocking Sprague! | ' + time)
    if dt.date.today().weekday() is 1 or 3:
        embed.set_thumbnail(url=emojiA)
    elif dt.date.today().weekday() is 2 or 4:
        embed.set_thumbnail(url=emojiB)
    elif dt.date.today().weekday() is 0:
        embed.set_thumbnail(url=emojiAB)
    for announcement in announcements:
        if len(announcement) > 1024:
            announcement = announcement[:1021] + '...'

        embed.add_field(name='⸻\t\t\t⸻\t\t\t⸻\t\t\t⸻\t\t\t⸻',
                        value=announcement)

    await client.get_channel(619772443116175370).send(embed=embed)


# Scheduled posting of announcements
scheduler = AsyncIOScheduler()
scheduler.add_job(postAnnouncements, trigger='cron',
                  day_of_week='mon-fri', hour=7)
scheduler.start()


client.run(token)
