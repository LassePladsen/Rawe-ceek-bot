from asyncio import sleep

import discord
from discord.ext import commands
from discord import File,Embed,Activity
from datetime import date

import util
import formula1 as f1

client = commands.Bot(command_prefix="&")

# Discord Channel ID
channel_id = int(util.get_discord_data("channel_id"))

async def get_rawe_ceek_embed(Date):
    title, des = util.get_all_week_info(Date)  # title and description for the embed message
    embed = Embed(title=title, description=des)
    embed.set_image(url="attachment://race.png")
    return embed

async def get_no_rawe_ceek_embed(Date):
    title = str(util.until_next_race_week(Date)) + " uke(r) til neste rawe ceek..."  # title for embed message

    en_date = util.get_event_date_str(f1.get_next_week_event(Date))
    no_date = str(int(en_date.split(" ")[0])) + " " + util.month_to_norwegian(en_date.split(" ")[1],
                                                                              caps=False)
    des = "Neste dato er " + no_date  # description for embed message
    embed = Embed(title=title, description=des)
    embed.set_image(url="attachment://sad.png")

async def update_status_message():
    Today = date.today()
    if f1.check_race_week(Today):
        # Set bot satus message to rawe ceek
        activity = Activity(type=discord.ActivityType.watching, name="RAWE CEEK!")
        await client.change_presence(status=discord.Status.idle, activity=activity)

    else:
        # Set bot satus message to no rawe ceek
        activity = Activity(type=discord.ActivityType.watching, name="no rawe ceek :(")
        await client.change_presence(status=discord.Status.idle, activity=activity)


async def send_week_embed(Date,emoji_rawe_ceek=None
                          ,emoji_no_rawe_ceek=None):
    """Sends timing embed and returns message object for later deletion"""
    # If its race week post the times, if not then post no. of weeks until next race week
    if f1.check_race_week(Date):
        rawe_ceek_image = util.get_discord_data("rawe_ceek_image")
        file = File(rawe_ceek_image, filename="race.png")
        embed = await get_rawe_ceek_embed(Date)

        Message = await client.get_channel(channel_id).send(file=file, embed=embed)
        if emoji_rawe_ceek:
            await Message.add_reaction(emoji_rawe_ceek)

    else:  # if not race week then post no. weeks until n# ext race week
        # Count how many weeks until next race week
        embed = await get_no_rawe_ceek_embed(Date)
        no_rawe_ceek_image = util.get_discord_data("no_rawe_ceek_image")
        file = File(no_rawe_ceek_image, filename="sad.png")

        Message = await client.get_channel(channel_id).send(file=file, embed=embed)
        if emoji_no_rawe_ceek:
            await Message.add_reaction(emoji_no_rawe_ceek)

    return Message

async def get_last_bot_message(max_messages=15):
    """Returns the Message for the last message the bot sent, checks up to given
    number of previous messages."""
    bot_id = util.get_discord_data("bot_id")  # the bots user id to check the previous messages
    prev_msgs = await client.get_channel(channel_id).history(limit=max_messages).flatten() # list of prev messages
    prev_ids = [str(msg.author.id) for msg in prev_msgs]    # list of the user ids for all prev messages

    if bot_id in prev_ids:
        index = prev_ids.index(bot_id)  # first index of last bot msg
        return prev_msgs[index]

async def status():
    # Initialize todays date
    prev_Date = date.today()

    # Loops after 24 hours
    while True:
        Today = date.today() # saves date to check if it has ran this week

        cond1 = util.get_sunday_date(Today) == util.get_sunday_date(prev_Date) # is same week as prev post?
        cond2 = f1.check_race_week(Today)  # is race week?

        # If it has posted this week and its a race week: only edit the embed to update f2 times
        if cond1 and cond2:
            Message = await get_last_bot_message()
            new_Embed = await get_rawe_ceek_embed(Today)
            await Message.edit(embed=new_Embed)

        # if hasnt posted this week: post embed and save date
        elif not cond1:
            rawe_ceek_emoji = util.get_discord_data("rawe_ceek_emoji")
            no_rawe_ceek_emoji = util.get_discord_data("no_rawe_ceek_emoji")
            await send_week_embed(Today,rawe_ceek_emoji,no_rawe_ceek_emoji)
            prev_Date = Today

        # Lastly update the status message
        await update_status_message()

        print("Loop complete")
        await sleep(24*3600)  # loops again after 24 hours (in seconds)

@client.event
async def on_ready():
    # await send_rawe_ceek_embed()  # send message on startup
    client.loop.create_task(status())   # then start the loop
    print("PIERRRE GASLYYYY!")


client.run(util.get_discord_data("bot_token"))
