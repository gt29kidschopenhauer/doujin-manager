import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv('DISCORD_GUILD')
CATEGORY = os.getenv("DISCORD_CATEGORY")
DOUJIN_CHANNEL = os.getenv("DISCORD_DOUJIN_CHANNEL")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
	print(f'{client.user} has connected to Discord!')
	global guild, category
	guild = discord.utils.get(client.guilds, name=GUILD)
	category = discord.utils.get(guild.categories, name=CATEGORY)

@client.event
async def on_message(message):
	if message.author == client.user:
		return
	if 'nhentai.net' in message.content and (message.channel.category is category or message.channel.name == DOUJIN_CHANNEL):
		print(1)

client.run(TOKEN)
