import discord

token = 'Mzg1MjIxNzkyMzcxMDQ4NDQ5.XXMsJg.mDfe-dRJccKRhKh7q4o4wwESht4'

client = discord.Client()

startsWith = '!'


@client.event
async def on_ready():
    print('Logged in as: ' + client.user.name)
    print('ID: ' + client.user.id)
    print('Ready to use\n')


@client.event
async def on_message(message):
    if message.content.startswith(startsWith):
        print('hey')
