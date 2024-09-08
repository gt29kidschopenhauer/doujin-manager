import os
import sys

from np import np_api
import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests
import helper.Constants as Constants
import sqlite3
from random import choice
import functools

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
TEST_CHANNEL_ID = int(os.getenv('DISCORD_TEST_CHANNEL_ID'))

nhentai = np_api()
con = sqlite3.connect('doujins.db')
cur = con.cursor()

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

def check_channel(doujin):
	if "Blue Archive" in doujin.parodie:
		yuri = False
		for t in doujin.tag:
			if t in Constants.others_tag:
				return OTHERS_CHANNEL_ID
			elif t == 'yuri':
				yuri = True
		if yuri:
			return EMUACH_CHANNEL_ID
		return CUNNY_CHANNEL_ID
	else:
		return DOUJIN_CHANNEL_ID

bot = commands.Bot(intents=intents, command_prefix="!")

async def run_blocking(blocking_func, *args, **kwargs):
    func = functools.partial(blocking_func, *args, **kwargs)
    return await bot.loop.run_in_executor(None, func)

@bot.event
async def on_ready():
	print(f'{bot.user} has connected to Discord!')

@bot.command(name='dou', help='Display the doujin with the specified code.')
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
			doujin = await run_blocking(nhentai.searchExplicitWithID, int(code))
			msg = doujin.echoed_doujin_message
			appr = check_channel(doujin)
			if ctx.channel.id == appr[index]:
				await ctx.send(msg + "https://nhentai.net/g/" + code + "/")
			else:
				await ctx.send("Right time, wrong place! Head over to <#" + str(appr[index]) + "> and share your sauce there!")

@bot.command(name='rand', help='Display a random BA doujin. Only usable in a BA channel.')
async def random_ba_dou(ctx, *name):
	index = GUILD.index(ctx.guild.name)
	if ctx.channel.category.name == CATEGORY[index]:
		if ctx.author == bot.user:
			return
		try:
			assert len(name) <= 1
		except AssertionError:
			await ctx.send("Too many arguments! Just one student's first name please!")
			return
		if ctx.channel.id == CUNNY_CHANNEL_ID[index]:
			doujin_type = Constants.DoujinType.CUNNY
		elif ctx.channel.id == EMUACH_CHANNEL_ID[index]:
			doujin_type = Constants.DoujinType.EMUACH
		else:
			doujin_type = Constants.DoujinType.OTHERS
		if len(name) == 1:
			data = cur.execute('SELECT full_name FROM students WHERE command = ?', (name[0].lower(),)).fetchall()
			try:
				assert len(data) != 0
			except AssertionError:
				await ctx.send("Invalid student name!")
				return
			codes = []
			for full_name in data:
				code = await run_blocking(nhentai.searchRandomBADoujin, full_name[0].lower(), doujin_type)
				codes.append(code)
		else:
			code = await run_blocking(nhentai.searchRandomBADoujin, None, doujin_type)
			codes = [code]
		normal = list(filter(lambda x: x != -1, codes))
		if len(normal) == 0:
			code = -1
		else:
			functional = list(filter(lambda x: x != 0, normal))
			if len(functional) == 0:
				code = 0
			else:
				code = choice(functional)
		if code == 0:
			await ctx.send("Sorry! There's no " + name[0][0].upper() + name[0][1:] + ' doujins of this type yet!')
			return
		elif code == -1:
			await ctx.send("Sorry! Something went wrong!")
			return
		await ctx.send(code.echoed_doujin_message + "https://nhentai.net/g/" + str(code.id) + "/")

@bot.command(name='test', help='Testing~')
async def testing(ctx, code):
	if ctx.channel.id == TEST_CHANNEL_ID:
		doujin = await run_blocking(nhentai.searchExplicitWithID, int(code))
		msg = doujin.echoed_doujin_message
		await ctx.send(msg + "https://nhentai.net/g/" + code + "/")

@bot.event
async def on_error(event, *args, **kwargs):
	if event == 'on_message':
		try:
			raise
		except InvalidNuclearCode as e:
			print(e.msg)

bot.run(TOKEN)
