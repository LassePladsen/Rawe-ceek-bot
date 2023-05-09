from asyncio import sleep

import discord
from discord.ext import commands
from datetime import date,datetime

import util
import formula1 as f1

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="&",intents=intents,case_insensitive=True)

# Discord Channel ID
channel_id = int(util.get_discord_data("channel_id"))

async def get_rawe_ceek_embed(Date):
    title, des = util.get_all_week_info(Date)  # title and description for the embed message
    embed = discord.Embed(title=title, description=des)
    embed.set_image(url="attachment://race.png")
    return embed

async def get_no_rawe_ceek_embed(Date):
    week_count = util.until_next_race_week(Date)
    if week_count == 1:
        title = str(week_count) + " uke til neste rawe ceek..."  # title for embed message

    else:
        title = str(week_count) + " uker til neste rawe ceek..."  # title for embed message

    en_date = util.get_event_date_str(f1.get_next_week_event(Date))
    no_date = str(int(en_date.split(" ")[0])) + " " + util.month_to_norwegian(en_date.split(" ")[1],
                                                                              caps=False)
    des = "Neste dato er " + no_date  # description for embed message
    embed = discord.Embed(title=title, description=des)
    embed.set_image(url="attachment://sad.png")
    return embed

async def update_status_message():
    today = date.today()
    if f1.check_race_week(today):
        # Set bot satus message to rawe ceek
        activity = discord.Activity(type=discord.ActivityType.watching, name="the RAWE CEEK!")
        await bot.change_presence(status=discord.Status.online, activity=activity)

    else:
        # Set bot satus message to no rawe ceek
        activity = discord.Activity(type=discord.ActivityType.watching, name="nothing... :(")
        await bot.change_presence(status=discord.Status.online, activity=activity)

async def send_week_embed(Date,emoji_rawe_ceek=None
                          ,emoji_no_rawe_ceek=None):
    """Sends timing embed and returns discord.Message object for later editing"""
    # If its race week post the times, if not then post no. of weeks until next race week
    if f1.check_race_week(Date):
        rawe_ceek_image = util.get_discord_data("rawe_ceek_image")
        file = discord.File(rawe_ceek_image, filename="race.png")
        embed = await get_rawe_ceek_embed(Date)

        message = await bot.get_channel(channel_id).send(file=file, embed=embed)
        if emoji_rawe_ceek:
            await message.add_reaction(emoji_rawe_ceek)

    else:  # if not race week then post no. weeks until n# ext race week
        # Count how many weeks until next race week
        embed = await get_no_rawe_ceek_embed(Date)
        no_rawe_ceek_image = util.get_discord_data("no_rawe_ceek_image")
        file = discord.File(no_rawe_ceek_image, filename="sad.png")

        message = await bot.get_channel(channel_id).send(file=file, embed=embed)
        if emoji_no_rawe_ceek:
            await message.add_reaction(emoji_no_rawe_ceek)

    return message

async def get_last_bot_message(max_messages=15):
    """Returns the discord.Message for the last message the bot sent, checks up to given
    number of previous messages."""
    bot_id = util.get_discord_data("bot_id")  # the bots user id to check the previous messages
    prev_msgs = await bot.get_channel(channel_id).history(limit=max_messages).flatten() # list of prev messages
    prev_ids = [str(msg.author.id) for msg in prev_msgs]    # list of the user ids for all prev messages

    if bot_id in prev_ids:
        index = prev_ids.index(bot_id)  # first index of last bot msg
        return prev_msgs[index]

async def execute_week_embed():
    """Checks if the bot has sent an embed the week of the given date.
    If so then update and edit the embed, if not then send a new embed."""
    today = date.today()

    message = await get_last_bot_message()
    prev_date = message.created_at.date()

    # If it has posted this week and its a race week: only edit the embed to update f2 times
    posted_cond = util.get_sunday_date(today) == util.get_sunday_date(prev_date)  # is same week as prev post?
    if f1.check_race_week(today):
        if posted_cond:  # same week then edit the embed
            new_embed = await get_rawe_ceek_embed(today)
            await message.edit(embed=new_embed)
            return

        # if not same week: post new embed and save date
        elif not posted_cond:
            rawe_ceek_emoji = util.get_discord_data("rawe_ceek_emoji")
            no_rawe_ceek_emoji = util.get_discord_data("no_rawe_ceek_emoji")
            await send_week_embed(today, rawe_ceek_emoji, no_rawe_ceek_emoji)
            return

    else: # not race week, only needs to update next week, so post new embed if there is none this week
        if not posted_cond: # post new embed and save date
            rawe_ceek_emoji = util.get_discord_data("rawe_ceek_emoji")
            no_rawe_ceek_emoji = util.get_discord_data("no_rawe_ceek_emoji")
            await send_week_embed(today, rawe_ceek_emoji, no_rawe_ceek_emoji)
            return

async def status():
    # Loops after 24 hours
    while True:
        # Check if it has sent this week: edits the weeks embed, or if not sends a new embed.
        await execute_week_embed()  # also updates the previous date if it sent a new one

        # Lastly update the status message
        await update_status_message()

        print("Loop complete",datetime.today(),"UTC")
        await sleep(24*3600)  # loops again after 24 hours (in seconds)

@bot.command(aliases=["upd"])
async def update(ctx):
    """On recieving update command with the bots prefix, executes the weekly embed send/edit
    with todays updated info. Also updates the status message just incase.
    If the command was not in #bot channel, delete both the command message and the reply message."""
    await execute_week_embed()
    await update_status_message()

    # send reply message in the same channel
    msg_channel_id = ctx.message.channel.id
    reply = await bot.get_channel(msg_channel_id).send("Update done.")

    # if its not in the #bot channel, then delete both the user and bots messages after 2 seconds
    bot_channel_id = int(util.get_discord_data("bot_channel_id"))
    if msg_channel_id != bot_channel_id:
        await sleep(2)
        await reply.delete()
        await ctx.message.delete()

    print("Update command executed",datetime.today(),"UTC")

@bot.event
async def on_ready():
    # await send_rawe_ceek_embed()  # send message on startup
    bot.loop.create_task(status())   # then start the loop
    print("PIERRRE GASLYYYY!")

# run the bot
bot.run(util.get_discord_data("bot_token"))
