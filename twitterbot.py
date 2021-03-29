from discord.ext import commands
from tinydb import TinyDB, Query
from tinydb.operations import set
import discord
import discord.ext.commands.errors
from discord.message import Attachment
import configparser
import tweepy
import asyncio
import requests
import shutil

database = TinyDB("banlist.json", sort_keys=True, indent=4, separators=(',', ': '))
data = Query()

config = configparser.ConfigParser()
config.read('keys.ini')

consumer_key = config['twitter']['consumer_key']
consumer_secret = config['twitter']['consumer_secret']
access_token = config['twitter']['access_token']
access_token_secret = config['twitter']['access_token_secret']

token = config["discord"]["discordtoken"]

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

Intents = discord.Intents.default()

description = "Commands for Susan"
bot = commands.Bot(command_prefix="$", intents=Intents, description=description)

moderators = [752158397255647252, 580697936493674507]
approved = [578219178066968576, 752163420962422795]
channels = [823651597971750922, 824056645205753897]
guilds = [752157598232477786, 576153162394894376]

@bot.command(brief="Bot license", description="Displays the GNU GPLv3 license for the bot's code, including its Github link")
async def license(ctx):
    await ctx.send("""This bot is licensed under the GNU VERSION 3 GENERAL PUBLIC LICENSE.

    The GNU General Public License is a free, copyleft license for software and other kinds of works.

    The licensed material and derivatives may be used for commercial purposes.
    The licensed material may be distributed.
    The licensed material may be modified.
    This license provides an express grant of patent rights from contributors.
    The licensed material may be used and modified in private.

    Source code must be made available when the licensed material is distributed.
    A copy of the license and copyright notice must be included with the licensed material.
    Modifications must be released under the same license when distributing the licensed material.
    Changes made to the licensed material must be documented.

    This license includes a limitation and/or no liability.
    This liceense explicitly states that it does NOT provide any warranty.

    The full license document may be read at <https://choosealicense.com/licenses/gpl-3.0/>
    The repository may be found at  <https://github.com/hanadrizz/twitterbot>
    """)

@bot.command()
@commands.has_any_role(*approved)
async def tweet(ctx, *, contents):
    userid = ctx.message.author.id
    datasearch = database.search(data.userid == userid)
    if datasearch == []:
        if not ctx.message.attachments:
            tweet = api.update_status(status=contents)
            url = "https://twitter.com/SusanCummings83/status/" + tweet.id_str
            print(f"{tweet.text}\n")
            await ctx.send(url)
            if ctx.guild.id == guilds[0]:
                channel = bot.get_channel(channels[1])
                await channel.send(url)
            elif ctx.guild.id == guilds[1]:
                channel = bot.get_channel(channels[0])
                await channel.send(url)
        else:
            image = ctx.message.attachments[0]
            url = image.url
            filename = image.filename
            r = requests.get(url, stream = True)
            if r.status_code == 200:
                r.raw.decode_content = True
                with open(filename,'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                f.close()
            img = api.media_upload(filename=filename)
            tweet = api.update_status(status=contents, media_ids=[img.media_id])
            url = "https://twitter.com/SusanCummings83/status/" + tweet.id_str
            print(tweet.text)
            await ctx.send(url)

            if ctx.guild.id == guilds[0]:
                channel = bot.get_channel(channels[1])
                await channel.send(url)
            elif ctx.guild.id == guilds[1]:
                channel = bot.get_channel(channels[0])
                await channel.send(url)
            

    else:
        await ctx.send(content="You're banned from sending tweets.", delete_after=5)

@bot.command()
@commands.has_any_role(*approved)
async def reply(ctx, tweeturl, *, content):
    userid = ctx.message.author.id
    datasearch = database.search(data.userid == userid)
    if datasearch == []:
        graburl = tweeturl.split("/")
        tweetid = graburl[5]
        tweet = api.update_status(status=content, in_reply_to_status_id = tweetid , auto_populate_reply_metadata=True)
        url = "https://twitter.com/SusanCummings83/status/" + tweet.id_str
        await ctx.send(url)
        print(f"{tweet.text}\n")
        if ctx.guild.id == guilds[0]:
            channel = bot.get_channel(channels[1])
            await channel.send(url)
        elif ctx.guild.id == guilds[1]:
            channel = bot.get_channel(channels[0])
            await channel.send(url)
    else:
        await ctx.send(content="You're banned from sending tweets.", delete_after=5)

@bot.command()
@commands.has_any_role(*approved)
async def rt(ctx, tweeturl):
    userid = ctx.message.author.id
    datasearch = database.search(data.userid == userid)
    if datasearch == []:
        graburl = tweeturl.split("/")
        api.retweet(graburl[5])
        await ctx.send("Tweet retweeted.")
    else:
        await ctx.send(content="You're banned from sending tweets.", delete_after=5)
@bot.command()
@commands.has_any_role(*approved)
async def qrt(ctx, tweeturl, *, content):
    userid = ctx.message.author.id
    datasearch = database.search(data.userid == userid)
    if datasearch == []:
        tweet = api.update_status(status=content+"\n"+tweeturl)
        url = "https://twitter.com/SusanCummings83/status/" + tweet.id_str
        await ctx.send(url)
        print(f"{tweet.text}\n")
        if ctx.guild.id == guilds[0]:
            channel = bot.get_channel(channels[1])
            await channel.send(url)
        elif ctx.guild.id == guilds[1]:
            channel = bot.get_channel(channels[0])
            await channel.send(url)
    else:
        await ctx.send(content="You're banned from sending tweets.", delete_after=5)

@bot.command()
@commands.has_any_role(*approved)
async def like(ctx, tweeturl):
    userid = ctx.message.author.id
    datasearch = database.search(data.userid == userid)
    if datasearch == []:
        graburl = tweeturl.split("/")
        api.create_favorite(graburl[5])
        await ctx.send("Tweet liked.")
    else:
        await ctx.send(content="You're banned from sending tweets.", delete_after=5)
@bot.command()
@commands.has_any_role(*moderators)
async def tweetban(ctx, member: discord.Member):
    database.insert({"userid": member.id})
    await ctx.send(f"Banned user {member.name}")

@bot.event
async def on_ready():
    print(f'Bot has connected to Discord!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Russan politics"))


bot.run(token)
