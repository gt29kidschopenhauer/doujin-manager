import os

import discord
from dotenv import load_dotenv
import sys

class InvalidNuclearCode(discord.DiscordException):
	def __init__(self, code, **kwargs):
		super().__init__(**kwargs)
		self.code = code

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
	elif message.content.isdecimal() and int(message.content) > 600000:
		raise InvalidNuclearCode(int(message.content))

@client.event
async def on_error(event, *args, **kwargs):
	if event == 'on_message':
		try:
			raise
		except InvalidNuclearCode as e:
			print(e.code)

client.run(TOKEN)
