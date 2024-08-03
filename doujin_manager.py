import os
import sys

from np import np_api
import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests

class InvalidNuclearCode(discord.DiscordException):
	def __init__(self, msg, **kwargs):
		super().__init__(**kwargs)
		self.msg = msg

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv('DISCORD_GUILD').split(", ")
CATEGORY = os.getenv("DISCORD_CATEGORY").split(', ')
DOUJIN_CHANNEL = os.getenv("DISCORD_DOUJIN_CHANNEL")
CUNNY_CHANNEL_ID = list(map(int, os.getenv('DISCORD_CUNNY_CHANNEL_ID').split(', ')))
EMUACH_CHANNEL_ID = list(map(int, os.getenv('DISCORD_EMUACH_CHANNEL_ID').split(', ')))
OTHERS_CHANNEL_ID = list(map(int, os.getenv('DISCORD_OTHERS_CHANNEL_ID').split(', ')))
DOUJIN_CHANNEL_ID = list(map(int, os.getenv('DISCORD_DOUJIN_CHANNEL_ID').split(', ')))

nhentai = np_api()

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

others_tag = ['vore', 'guro', 'necrophilia', 'futanari', 'dickgirl on male', 'dickgirl on female',
			 'dickgirl on dickgirl', 'dickgirls only', 'sole dickgirl', 'male on dickgirl', 
			 'full-packaged futanari', 'futanarization', 'netorare', 'ryona', 'mmf threesome', 
			 'gang rape', 'robot', 'scat', 'scat insertion', 'enema', 'dick growth', 'pegging', 
			 'penis enlargement', 'anal birth', 'unbirth', 'penis birth', 'nipple birth', 'nipple fuck',
			 'cheating', 'swinging', 'piss drinking', 'bbm']

def check_channel(doujin):
	p = False
	for parody in doujin.parodie:
		if parody['name'] == 'blue archive':
			p = True
			break
	if p:
		for t in doujin.tag:
			if t['name'] in others_tag:
				return OTHERS_CHANNEL_ID
			elif t['name'] == 'yuri':
				return EMUACH_CHANNEL_ID
		return CUNNY_CHANNEL_ID
	else:
		return DOUJIN_CHANNEL_ID


bot = commands.Bot(intents=intents, command_prefix="!")

@bot.event
async def on_ready():
	print(f'{bot.user} has connected to Discord!')

@bot.command(name='dou', help='Display the doujin with the specified code')
async def output_link(ctx, code):
	index = GUILD.index(ctx.guild.name)
	if ctx.channel.category.name == CATEGORY[index] or ctx.channel.name == DOUJIN_CHANNEL:
		if ctx.author == bot.user:
			return
		try:
			int(code)
			req = requests.get("https://nhentai.net/g/" + code + "/")
			if req.status_code == 404:
				raise InvalidNuclearCode("ERROR: Doujin with code " + code + " doesn't exist.")
		except ValueError:
			await ctx.send("ERROR: " + code + " is not a natural number.")
		except InvalidNuclearCode as e:
			await ctx.send(e.msg)
		else:
			doujin = nhentai.searchExplicitWithID(int(code))
			appr = check_channel(doujin)
			if ctx.channel.id == appr[index]:
				await ctx.send("https://nhentai.net/g/" + code + "/")
			else:
				await ctx.send("Right time, wrong place! Head over to <#" + str(appr[index]) + "> and share your sauce there!")

@bot.event
async def on_error(event, *args, **kwargs):
	if event == 'on_message':
		try:
			raise
		except InvalidNuclearCode as e:
			print(e.msg)

bot.run(TOKEN)
