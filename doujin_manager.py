import os

import discord
from discord.ext import commands
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

bot = commands.Bot(intents=intents, command_prefix="!")

@bot.event
async def on_ready():
	print(f'{bot.user} has connected to Discord!')
	global guild, category
	guild = discord.utils.get(bot.guilds, name=GUILD)
	category = discord.utils.get(guild.categories, name=CATEGORY)

@bot.event
async def on_message(message):
	if message.author == bot.user:
		return
	if 'nhentai.net' in message.content and (message.channel.category is category or message.channel.name == DOUJIN_CHANNEL):
		print(1)

@bot.event
async def on_error(event, *args, **kwargs):
	if event == 'on_message':
		try:
			raise
		except InvalidNuclearCode as e:
			print(e.code)

bot.run(TOKEN)
