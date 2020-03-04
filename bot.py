# region Header
# ---
# TODO: Censorship warning system, download image to check for adult content, read text, and keep track of who has recieved warnings and why
# TODO: Connect to a student database to auto-assign roles and nick-names? Same system that does schedule changes with
#      student ID, first letter of last name, email, etc. (Doubt we would get access... unless..?)
# TODO: Try to make this ass professional as possible :) - IN PROGRESS
# ---
# endregion


# region Imports
import re
import ast
import sys
import json
import furl
import discord
import requests
import psycopg2
import sqlalchemy
import sqlalchemy_utils
import pytesseract
import datetime as dt
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from discord.ext import commands
from sqlalchemy_utils import CompositeType
from sqlalchemy.dialects import postgresql
from sqlalchemy import *
from sightengine.client import SightengineClient
from profanity_check import predict, predict_prob
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# endregion


# region Miscellaneous Functions/Other

emojiA = 'https://i.imgur.com/dmTKeTi.png'
emojiB = 'https://i.imgur.com/oLJnbDL.png'
emojiAB = 'https://i.imgur.com/dVOtgZq.png'
emojiAnnouncements = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/228/public-address-loudspeaker_1f4e2.png'
emojiExclamation = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/228/double-exclamation-mark_203c.png'
emojiWave = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/228/waving-hand-sign_1f44b.png'
announcements = []
date = ''
dayType = ''

# URL Validation


async def URL(str):
    url = re.findall(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str)
    return url


class Warning():
    def __init__(self, c=None, o=None):
        self.cause, self.offences = c, o


async def predictText(text):
    prob = predict_prob(text)
    return prob


async def predictImage(url):
    txt = pytesseract.image_to_string(Image.open(
        BytesIO(requests.get(url).content)))  # ughhhhh
    img_prob = predict_prob([txt])

    return img_prob


# TODO: Train these variables? Make them modifyable in json?
async def Sight(message, url):
    output = sight.check(
        'nudity', 'wad', 'offensive').set_url(url)
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

        with open('test.json', 'w') as outfile:
            json.dump(output, outfile, indent=4)
        outfile.close()

        return offenses
    else:  # error, send to be manually reviewed
        addReport(message, message.id)


async def Warn(cause, offences, author):
    # add to user's warnings, if > 3 then ban
    giveWarning('discord_id', author, cause, offences)
    warnings = warningCount('discord_id', author)

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

    if URL(cause) != None:
        embed.set_image(url=URL(cause))
    embed.set_footer(text='Remember to make it a great day!')

    # TODO: Send to an admin chat to confirm warnings
    await author.send(embed=embed)


# Web crawler grabs announcements, modifies, then posts to id=619772443116175370
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
    time = dt.date(day=today.day, month=today.month,
                   year=today.year).strftime('%A %B %d, %Y')
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

# endregion


# region Database Initialization
# TODO: Include student id, grade, more?
# https://www.compose.com/articles/using-postgresql-through-sqlalchemy/
# https://stackoverflow.com/questions/9521020/sqlalchemy-array-of-postgresql-custom-types
# View database easily with PGAdmin
engine = sqlalchemy.create_engine(
    'postgresql://tech:webbie64@localhost:5432/spragueBot.db')
metadata = MetaData(engine)

sqlalchemy_utils.functions.drop_database(engine.url)
sqlalchemy_utils.functions.create_database(engine.url)

metadata = MetaData(engine)
warned = Table('warned', metadata,
               Column('first_last', sqlalchemy.types.String, primary_key=True),
               #Column('student_id', sqlalchemy.types.SmallInteger, primary_key=True),
               #Column('grade', sqlalchemy.types.SmallInteger),
               Column('discord_id', sqlalchemy.types.String),
               Column('banned', sqlalchemy.types.Boolean),
               Column('warnings', sqlalchemy.types.ARRAY(CompositeType(
                   'warning',  # Include if manually overridden?
                   [
                       Column('cause', sqlalchemy.types.String),
                       Column('offenses', sqlalchemy.types.ARRAY(
                           sqlalchemy.String))
                   ]
               )))
               )
staff = Table('staff', metadata,
              Column('first_last', sqlalchemy.types.String, primary_key=True),
              #Column('student_id', sqlalchemy.types.SmallInteger, primary_key=True),
              #Column('grade', sqlalchemy.types.SmallInteger),
              Column('discord_id', sqlalchemy.types.String),
              Column('role', sqlalchemy.types.String)
              )
verification = Table('verification', metadata,
                     Column('message_id', sqlalchemy.types.String,
                            primary_key=True),
                     Column('channel_id', sqlalchemy.types.String),
                     #Column('student_id', sqlalchemy.types.SmallInteger, primary_key=True),
                     #Column('grade', sqlalchemy.types.SmallInteger),
                     Column('confirmed_by', sqlalchemy.types.String),
                     Column('denied_by', sqlalchemy.types.String)
                     )
# metadata.create_all(engine)
# endregion


# region Database Functions


async def openDB():
    global sq
    sq = engine.connect()


async def closeDB():
    sq.execute('commit')
    sq.close()

# TODO: support for searaching for ids?

# region Warning Functions


async def getWarnings(indexer, value):
    s = text('SELECT warnings[:i] FROM warned WHERE :ind = :v')
    warnings = []
    await openDB()
    for x in range(3):
        try:
            result = sq.execute(s, i=x, ind=indexer, v=value)
            temp = result.first()[0].split(',', 1)
            cause = temp[0][1:]
            offences = temp[1][2:-3].replace('\"', '').split(',')
            warnings.append(Warning(cause, offences))
        except:
            NotImplemented

    await closeDB()
    return warnings


async def warningCount(indexer, value):
    s = text('SELECT warned, ARRAY_LENGTH(warnings) WHERE :i = :v')
    await openDB()
    count = sq.execute(s, i=indexer, v=value)
    await closeDB()
    return int(count)


async def giveWarning(indexer, value, cause, offences):  # TODO: Send message to user
    u = text(
        'UPDATE warned SET warnings = array_append(warnings, (:c, :o)::warning) WHERE :i = :v')
    await openDB()
    sq.execute(u, c=cause, o=offences, i=indexer, v=value)
    await closeDB()


async def removeWarning(indexer, value, cause, offences):  # TODO: Send message to user
    u = text(
        'UPDATE warned SET warnings = array_remove(warnings, (:c, :o)::warning) WHERE :i = :v')
    await openDB()
    sq.execute(u, c=cause, o=offences, i=indexer, v=value)
    await closeDB()
# endregion

# region Staff Functions


async def getStaff(indexer, value):
    s = text('SELECT * FROM staff WHERE :i = :v')
    await openDB()
    staff = sq.execute(s, i=indexer, v=value)
    await closeDB()
    return staff


async def addStaff(name, id, role):  # TODO: Send message to user
    i = text(
        'INSERT INTO staff (first_last, discord_id, role) VALUES (:name, :id, :role)')
    await openDB()
    sq.execute(i, name=name, id=id, role=role)
    await closeDB()


async def removeStaff(indexer, value):  # TODO: Send message to user
    d = text('DELETE FROM staff WHERE :i = :v')
    await openDB()
    sq.execute(d, i=indexer, v=value)
    await closeDB()
# endregion

# region Verification Functions


async def addReport(message, id=None):
    if id == None:
        id = message.content.split(' ')[1]
    msg = message.channel.fetch_message(id)

    i = text(
        'INSERT IGNORE INTO verification (message_id, channel_id) VALUES (:msg, :cha)')
    await openDB()
    sq.execute(i, msg=msg.id, cha=msg.channel.id)
    await closeDB()
    await sendVerificationUpdate(msg)


async def getReport(message, id):
    msg = message.channel.fetch_message(id)

    s = text('SELECT * FROM verification WHERE message_id = :id')
    await openDB()
    report = sq.execute(s, id=msg.id)
    await closeDB()
    return report


async def verify(indexer, value, id):
    u = text('UPDATE verification SET :i = :v WHERE message_id = :id')
    await openDB()
    sq.execute(u, i=indexer, v=value, id=id)
    await closeDB()


async def sendVerificationUpdate(message):
    embed = discord.Embed(title='Please Verify:',
                          description='Case **#%s**' % message.id, color=0xf04923)
    if len(message.attachments) > 1:
        def check(author):
            def inner_check(message):
                return message.author == author and 0 < int(message.content) <= len(message.attachments)
            return inner_check

        await message.channel.send('Which attachment? (Decending 1-%i)' % len(message.attachments), delete_after=30)
        try:
            result = await client.wait_for('message', check=check(message.author), timeout=30)
        except:
            await message.channel.send('Error', delete_after=30)
        else:
            sight = await Sight(message, message.attachments[result - 1].proxy_url)
            embed.set_image(url=message.attachments[result - 1].proxy_url)
            embed.add_field(name='Offenses:',
                            value=', '.join(sight), inline=True)
    else:
        sight = await Sight(message, message.attachments[0].proxy_url)
        embed.set_image(url=message.attachments[0].proxy_url)
        embed.add_field(
            name='Cause:', value='[Link](%s)' % message.attachments[0].proxy_url, inline=True)
        embed.add_field(name='Offenses:', value=', '.join(sight), inline=True)

    embed.set_footer(text='✅ to Confirm  |  ❌ to Deny')

    await client.get_channel(682637318569721898).send(embed=embed)
# endregion
# endregion


# region Initialization

# Grab bot token and prefix, sightengine, and tosc file location from json, TODO: Make the prefix changable
with open('info.json', 'r') as json_file:
    data = json.load(json_file)
    for j in data['info']:
        token = j['botToken']
        prefix = j['botPrefix']
        SEUser = j['SEUser']
        SESecret = j['SESecret']
        ocrLocation = j['tesseractLocation']
    json_file.close()

# client initialization
client = commands.Bot(command_prefix=prefix)
sight = SightengineClient(SEUser, SESecret)
pytesseract.pytesseract.tesseract_cmd = ocrLocation

# https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v5.0.0-alpha.20190708.exe
# https://stackoverflow.com/questions/50951955/pytesseract-tesseractnotfound-error-tesseract-is-not-installed-or-its-not-i

# endregion


# region Bot Events
@client.event
async def on_ready():
    print('\nLogged in as:', client.user.name)
    print('ID:', client.user.id)
    print('Discord.py version:', discord.__version__)  # using 1.3.1
    print('Python version:', sys.version.split(' ')[0])  # using 3.7.0
    print('SQLAlchemy version:', sqlalchemy.__version__)  # using 1.3.13
    print('Ready to use\n')


# Sends new users a message on joining the guild
# TODO: Test
# TODO: Check username for profanity
# TODO: Check pfp with sight engine and require change
# TODO: Add new users to Database
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
    elif message.content.startswith(prefix):
        if 'test' in message.content:
            url = 'https://cdn.discordapp.com/attachments/620167820558204928/675434297775357962/n4VQ3hbwOkofbjhdiqEj_PWILJQ9ssqsCDRuOguC-AufrmYgdaamPE8kxotb52EzoT3ZkkItcvfMIaWzZlpT_yqof2OBocKMu6Dk.png'
            embed = discord.Embed(
                title='Please Verify:', description='Case **#683034905051004999**', color=0xf04923)
            embed.set_image(url=url)
            embed.set_footer(text='✅ to Confirm  |  ❌ to Deny')
            embed.add_field(
                name='Cause:', value='[Link](%s)' % url, inline=True)
            x = ['Gun', 'Racist']
            embed.add_field(name='Offenses:', value=', '.join(x), inline=True)

            await message.channel.send(embed=embed)

            # await sentMessage.add_reaction(emoji='✅')
            # await sentMessage.add_reaction(emoji='❌')

            def check(reaction, user):
                return user == message.author and str(reaction.emoji) == '✅' or '❌'

            try:
                reaction, user = await client.wait_for('reaction_add', timeout=99999, check=check)
            except:
                await message.channel.send('Error')
            else:
                # TODO: change (user == message.author) to check against list of admins/mods/whatever and send to admin chat in server
                if (user == message.author) and (reaction == '✅' or '❌'):
                    await message.channel.send(reaction)

        elif 'report' in message.content:
            await addReport(message)

        elif 'verify ' in message.content:
            if message.author in getStaff('role', 'admin'):
                caseNum = message.content.replace('#', '').split(' ')[1]
                if caseNum != None:
                    report = getReport(message, caseNum)
                    if report != None:
                        await message.add_reaction(emoji='✅')
                        await message.add_reaction(emoji='❌')

                        def check(reaction, user):
                            return user == message.author and str(reaction.emoji) == '✅' or '❌'

                        try:
                            reaction, user = await client.wait_for('reaction_add', timeout=30, check=check)
                        except:
                            await message.channel.send('Error')
                        else:
                            # TODO: change (user == message.author) to check against list of admins/mods/whatever and send to admin chat in server
                            if (user == message.author) and (reaction == '✅' or '❌'):
                                if reaction == '✅':
                                    verify('confirmed_by',
                                           message.author, caseNum)
                                elif reaction == '❌':
                                    verify('denied_by', message.author, caseNum)
                    else:
                        await message.channel.send(content='Case #%s not found!' % caseNum)

                else:
                    await message.channel.send(content='Case number cannot be blank! Check `CHANNEL_NAME` for more info.')

        elif 'admin' in message.content:
            # await addStaff('Caden Garrett', '147926148616159233', 'master')
            NotImplemented

    attachments = []
    for url in await URL(text):
        attachments.append(url)
    for attach in message.attachments:
        attachments.append(attach.proxy_url)

    prob = predictText(message.content)
    if prob > 0.5:  # change this value?
        Warn(message.content, '%i%% offensive' % prob, message.author)

    for attach in attachments:
        Sight(message, attach)
# endregion


# region Startup
# Scheduled posting of announcements
scheduler = AsyncIOScheduler()
scheduler.add_job(postAnnouncements, trigger='cron',
                  day_of_week='mon-fri', hour=7)
scheduler.start()


client.run(token)
# endregion
