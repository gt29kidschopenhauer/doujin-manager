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
from time import time
from exceptions import *
import datetime
from string import capwords

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

def check_date(date):
	dates = date.split('-')
	if len(dates) != 3:
		return False
	try:
		x = datetime.datetime(int(dates[2]), int(dates[1]), int(dates[0]), tzinfo=datetime.timezone.utc)
		return int(x.timestamp())
	except ValueError:
		return False

bot = commands.Bot(intents=intents, command_prefix="!")

async def run_blocking(blocking_func, *args, **kwargs):
    func = functools.partial(blocking_func, *args, **kwargs)
    return await bot.loop.run_in_executor(None, func)

def parse_inputs(data):
	con = sqlite3.connect('doujins.db')
	cur = con.cursor()
	if len(data) % 2 == 1:
		if data[0][0] == '-':
			raise InvalidInput(InvalidInput.nameWrongPosition, data[0])
		name = cur.execute('SELECT full_name FROM command WHERE command = ?', (data[0].lower(),)).fetchall()
		if len(name) == 0:
			raise InvalidInput(InvalidInput.invalidName, data[0])
		params = parse_inputs(data[1:])
		params['name'] = name
	else:
		params = {}
		for i in range(len(data) // 2):
			if data[2 * i][0] != '-':
				raise InvalidInput(InvalidInput.flagWrongPosition, data[2 * i])
			if data[2 * i] == '-a':
				if 'author' not in params:
					params['author'] = data[2 * i + 1].lower()
				else:
					raise InvalidInput(InvalidInput.repetitiveFlag, '-a')
			elif data[2 * i] == '-g':
				if 'group' not in params:
					params['group'] = data[2 * i + 1].lower()
				else:
					raise InvalidInput(InvalidInput.repetitiveFlag, '-g')
			elif data[2 * i] == '-da':
				check = check_date(data[2 * i + 1])
				if not check:
					raise InvalidInput(InvalidInput.invalidDate, data[2 * i + 1])
				if 'after' in params:
					raise InvalidInput(InvalidInput.repetitiveFlag, '-da')
				params['after'] = check
				after = data[2 * i + 1]
			elif data[2 * i] == '-db':
				check = check_date(data[2 * i + 1])
				if not check:
					raise InvalidInput(InvalidInput.invalidDate, data[2 * i + 1])
				if 'before' in params:
					raise InvalidInput(InvalidInput.repetitiveFlag, '-db')
				params['before'] = check
				before = data[2 * i + 1]
			elif data[2 * i] == '-l':
				language = data[2 * i + 1]
				if language.lower() not in ('japanese', 'chinese', 'english'):
					raise InvalidInput(InvalidInput.invalidLanguage, data[2 * i + 1])
				if 'language' in params:
					raise InvalidInput(InvalidInput.repetitiveFlag, '-l')
				params['language'] = language.lower()
			else:
				raise InvalidInput(InvalidInput.invalidFlag, data[2 * i])
		if 'before' in params and 'after' in params and params['before'] <= params['after']:
			raise InvalidInput(InvalidInput.invalidTimePeriod, (before, after))
	con.close()
	return params

def generate_random_BA_doujin(doujin_type, full_name, after, before, language, author, group):
	con = sqlite3.connect('doujins.db')
	cur = con.cursor()
	components = ["SELECT id FROM doujin"]
	if full_name:
	    components.append("JOIN student ON (student.doujin_id = doujin.id)")
	if author:
	    components.append("JOIN author ON (author.doujin_id = doujin.id)")
	if group:
	    components.append("JOIN [group] ON ([group].doujin_id = doujin.id)")
	components.append("WHERE doujin.type = ?")
	args = []
	if doujin_type == Constants.DoujinType.CUNNY:
		args.append('cunny')
	elif doujin_type == Constants.DoujinType.EMUACH:
		args.append('emuach')
	else:
		args.append('others')
	if full_name:
		components.append("AND student.full_name = ?")
		args.append(full_name)
	if after:
		components.append("AND doujin.upload_date > ?")
		args.append(after)
	if before:
		components.append("AND doujin.upload_date < ?")
		args.append(before)
	if language:
		components.append("AND doujin.language = ?")
		args.append(language)
	if author:
		components.append('AND author.name = ?')
		args.append(author)
	if group:
		components.append('AND [group].name = ?')
		args.append(group)
	script = ' '.join(components)
	cur.execute(script, args)
	try:
		code = choice(cur.fetchall())[0]
	except IndexError:
		return 0
	con.close()
	return code

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
				raise InvalidNuclearCode(code, 0)
		except InvalidNuclearCode as e:
			await ctx.send(e.msg)
		except ValueError:
			await ctx.send("ERROR: " + code + " is not a natural number.")
		else:
			doujin = await run_blocking(nhentai.searchExplicitWithID, int(code))
			msg = doujin.echoed_doujin_message
			appr = check_channel(doujin)
			if ctx.channel.id == appr[index]:
				await ctx.send(msg + "https://nhentai.net/g/" + code + "/")
			else:
				await ctx.send("Right time, wrong place! Head over to <#" + str(appr[index]) + "> and share your sauce there!")

@bot.command(name='rand', help='Display a random doujin.')
async def random_ba_dou(ctx, *args):
	index = GUILD.index(ctx.guild.name)
	if ctx.channel.category.name == CATEGORY[index]:
		if ctx.author == bot.user:
			return
		if ctx.channel.id == CUNNY_CHANNEL_ID[index]:
			doujin_type = Constants.DoujinType.CUNNY
		elif ctx.channel.id == EMUACH_CHANNEL_ID[index]:
			doujin_type = Constants.DoujinType.EMUACH
		else:
			doujin_type = Constants.DoujinType.OTHERS
		try:
			params = parse_inputs(args)
			if 'group' not in params:
				params['group'] = None
			if 'author' not in params:
				params['author'] = None
			if 'after' not in params:
				params['after'] = None
			if 'before' not in params:
				params['before'] = None
			if 'language' not in params:
				params['language'] = None
			if 'name' not in params:
				code = await run_blocking(generate_random_BA_doujin, doujin_type, None, params['after'], params['before'], params['language'], params['author'], params['group'])
				codes = [code]
			else:
				codes = []
				for full_name in params['name']:
					code = await run_blocking(generate_random_BA_doujin, doujin_type, full_name[0], params['after'], params['before'], params['language'], params['author'], params['group'])
					codes.append(code)
			codes = list(filter(lambda x: x != 0, codes))
			if len(codes) == 0:
				await ctx.send("Sorry! There's no doujins of this type yet!")
				return
			code = nhentai.searchExplicitWithID(choice(codes))
		except InvalidInput as e:
			await ctx.send(e.msg)
	elif ctx.channel.name == DOUJIN_CHANNEL:
		code = nhentai.pickRandom()
		while "Blue Archive" in code.parodie:
			code = nhentai.pickRandom()
	await ctx.send(code.echoed_doujin_message + "https://nhentai.net/g/" + str(code.id) + "/")

@bot.command(name='test', help='Testing~')
async def testing(ctx, *args):
	if ctx.channel.id == TEST_CHANNEL_ID:
		doujin_type = Constants.DoujinType.OTHERS
		try:
			params = parse_inputs(args)
			if 'group' not in params:
				params['group'] = None
			if 'author' not in params:
				params['author'] = None
			if 'after' not in params:
				params['after'] = None
			if 'before' not in params:
				params['before'] = None
			if 'language' not in params:
				params['language'] = None
			if 'name' not in params:
				code = await run_blocking(generate_random_BA_doujin, doujin_type, None, params['after'], params['before'], params['language'], params['author'], params['group'])
				codes = [code]
			else:
				codes = []
				for full_name in params['name']:
					code = await run_blocking(generate_random_BA_doujin, doujin_type, full_name[0], params['after'], params['before'], params['language'], params['author'], params['group'])
					codes.append(code)
			codes = list(filter(lambda x: x != 0, codes))
			if len(codes) == 0:
				await ctx.send("Sorry! There's no doujins of this type yet!")
				return
			code = choice(codes)
			doujin = nhentai.searchExplicitWithID(code)
			await ctx.send(doujin.echoed_doujin_message + "https://nhentai.net/g/" + str(code) + "/")
		except InvalidInput as e:
			await ctx.send(e.msg)

@bot.event
async def on_error(event, *args, **kwargs):
	if event == 'on_message':
		try:
			raise
		except InvalidNuclearCode as e:
			print(e.msg)

bot.run(TOKEN)
