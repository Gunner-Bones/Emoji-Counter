import discord
from discord.ext import commands
import sys
import asyncio
from json_abs import *
import datetime
import dateutil.relativedelta as rd
import re
import copy


BOT_PREFIX = '?'
client = commands.Bot(command_prefix=BOT_PREFIX)
client.remove_command("help")


FOLDER_DATA = "data/"

EC_HISTORY_FARTHESTDATEMONTHS = 6


SECRET = None
try:
	secret_file = open('pass.txt', 'r')
except FileNotFoundError:
	sys.exit('hey make a pass.txt file')
for line in secret_file:
	SECRET = line
	break
secret_file.close()


def filesUpdate():
	print("[filesUpdate] Updating files...")
	for guild in client.guilds:
		file_exists = True
		try:
			test_json = j_read(FOLDER_DATA + str(guild.id))
		except FileNotFoundError:
			file_exists = False
		if not file_exists:
			j_create(str(FOLDER_DATA + str(guild.id)))
			guild_json = {}
			guild_emojis = [str(emoji.id) for emoji in guild.emojis]
			for channel in guild.channels:
				guild_json[str(channel.id)] = {emoji: 0 for emoji in guild_emojis}
			j_overwrite(FOLDER_DATA + str(guild.id), guild_json)
	print("[filesUpdate] Files updated.")


"hello guys <:haha:2435234524352345> whats up"

@client.event
async def on_ready():
	print("Bot ready!")
	print("Name: " + client.user.name + ", ID: " + str(client.user.id))
	filesUpdate()


@client.command(pass_context=True)
async def ec_update(ctx):
	print("[ec_update] Emoji Refresh started...")
	file_exists = True
	guild_json = None
	try:
		guild_json = j_read(FOLDER_DATA + str(ctx.guild.id))
	except FileNotFoundError:
		file_exists = False
	if file_exists:
		await ctx.channel.send("Emoji Refresh started...")
		for channel_id in guild_json.keys():
			for emoji_id in guild_json[channel_id].keys():
				guild_json[channel_id][emoji_id] = 0
		date_limit = datetime.datetime.now() + rd.relativedelta(months=-EC_HISTORY_FARTHESTDATEMONTHS)
		for channel in ctx.guild.channels:
			oldest_message = None
			if isinstance(channel, discord.TextChannel):
				try:
					#print("Channel: " + channel.name)
					async for message in channel.history(after=date_limit, limit=None):
						if not message.author.bot:
							oldest_message = "https://discordapp.com/channels/" + str(ctx.guild.id) + \
							"/" + str(channel.id) + "/" + str(message.id)
							#print(message.created_at)
							#print(message.content)
							emoji_iter = re.finditer("<:[^:]+:([0-9]+)>", message.content)
							emoji_list = [str(emoji_id.group(1)) for emoji_id in emoji_iter]
							#print(emoji_list)
							#print()
							for reaction in message.reactions:
								if reaction.custom_emoji:
									for _ in range(reaction.count):
										emoji_list.append(str(reaction.emoji.id))
							for emoji in emoji_list:
								#print("Emoji found in " + channel.name + ": " + emoji)
								try:
									guild_json[str(ctx.channel.id)][emoji] += 1
								except KeyError:
									pass
					#print("Channel: " + channel.name + ", Dict:" + str(guild_json[str(channel.id)]))
				except discord.errors.Forbidden:
					continue
				#print(oldest_message)
		#print(guild_json)
		j_overwrite(FOLDER_DATA + str(ctx.guild.id), guild_json)
		print("[ec_update] Emoji Refresh finished!")
		await ctx.channel.send("Emoji Refresh finished!")



@client.command(pass_context=True)
async def ec_current(ctx):
	file_exists = True
	guild_json = None
	try:
		guild_json = j_read(FOLDER_DATA + str(ctx.guild.id))
	except FileNotFoundError:
		file_exists = False
	if file_exists:
		message_ec = "Number of Emojis sent in **" + ctx.channel.name + "**:\n"
		emoji_json = guild_json[str(ctx.channel.id)]
		guild_emojis = {}
		for emoji_id in emoji_json.keys():
			emoji = None
			for e in ctx.guild.emojis:
				if str(e.id) == emoji_id:
					emoji = e
					break
			emoji = "<:" + str(ctx.guild.id) + ":" + str(emoji.id) + ">"
			message_ec += emoji + " : " + str(emoji_json[emoji_id]) + "\n"
		await ctx.channel.send(message_ec)


@client.command(pass_context=True)
async def ec_all(ctx):
	file_exists = True
	guild_json = None
	try:
		guild_json = j_read(FOLDER_DATA + str(ctx.guild.id))
	except FileNotFoundError:
		file_exists = False
	if file_exists:
		message_ec = "Number of Emojis sent in all channels:\n"
		emoji_count = copy.copy(guild_json[list(guild_json.keys())[1]])
		for emoji_id in emoji_count:
			emoji_count[emoji_id] = 0
		for channel in ctx.guild.channels:
			emoji_json = guild_json[str(channel.id)]
			for emoji_id in emoji_json:
				emoji_count[emoji_id] += emoji_json[emoji_id]
		for emoji_id in emoji_count.keys():
			emoji = None
			for e in ctx.guild.emojis:
				if str(e.id) == emoji_id:
					emoji = e
					break
			emoji = "<:" + str(ctx.guild.id) + ":" + str(emoji.id) + ">"
			message_ec += emoji + " : " + str(emoji_count[emoji_id]) + "\n"
		await ctx.channel.send(message_ec)


client.run(SECRET)