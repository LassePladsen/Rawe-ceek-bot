from asyncio import sleep
from datetime import date, datetime, timedelta
from typing import Union

import discord
from discord.ext import commands

import formula1 as f1
import formula2 as f2
import util

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="&", intents=intents, case_insensitive=True)

# Discord Channel ID
CHANNEL_ID = int(util.get_json_data("channel_id"))

# Status run timing
SCHEDULED_HOUR = 1  # 24 hour format local time
SCHEDULED_MINUTE = 0


async def get_race_week_embed(date_: datetime.date) -> discord.Embed:
    """Returns embed for a race week with a 'race week' image."""
    title, des = f1.get_all_week_info(date_)  # title and description for the embed message
    embed = discord.Embed(title=title, description=des)
    embed.set_image(url="attachment://race.png")
    return embed


async def get_no_race_week_embed(date_: datetime.date) -> discord.Embed:
    """Returns embed for a non race week with a 'no race week' image."""
    week_count = f1.until_next_race_week(date_)
    if week_count == 1:
        title = str(week_count) + " uke til neste rawe ceek..."  # title for embed message

    else:
        title = str(week_count) + " uker til neste rawe ceek..."  # title for embed message

    next_event_name = f1.get_next_week_event(date_)["EventName"]

    en_date = util.get_event_date_str(f1.get_next_week_event(date_))
    no_date = str(int(en_date.split(" ")[0])) + " " + util.month_to_norwegian(en_date.split(" ")[1],
                                                                              caps=False)
    des = f"{next_event_name} den {no_date}."  # description for embed message
    embed = discord.Embed(title=title, description=des)
    embed.set_image(url="attachment://norace.png")
    return embed


async def update_status_message() -> None:
    """Updates the bots status message with either a message depending on if its a race week or not."""
    today = date.today()
    if f1.check_f1_race_week(str(today)):
        # Set bot satus message to rawe ceek
        activity = discord.Activity(type=discord.ActivityType.watching, name="the RACE WEEK!")
        await bot.change_presence(status=discord.Status.online, activity=activity)

    else:
        # Set bot satus message to no rawe ceek
        activity = discord.Activity(type=discord.ActivityType.watching, name="nothing... :(")
        await bot.change_presence(status=discord.Status.online, activity=activity)


async def send_week_embed(date_: datetime.date, emoji_race_week=None, emoji_no_race_week=None):
    """Sends an embed for the week, either embed for race week or non race week."""
    # If its race week post the times, if not then post no. of weeks until next race week
    if f1.check_f1_race_week(date_):
        race_week_image = util.get_json_data("race_week_image")
        file = discord.File(race_week_image, filename="race.png")
        embed = await get_race_week_embed(date_)

        message = await bot.get_channel(CHANNEL_ID).send(file=file, embed=embed)
        if emoji_race_week is not None:
            await message.add_reaction(emoji_race_week)

    else:  # if not race week then post no. weeks until next race week
        # Count how many weeks until next race week
        embed = await get_no_race_week_embed(date_)
        no_race_week_image = util.get_json_data("no_race_week_image")
        file = discord.File(no_race_week_image, filename="norace.png")

        message = await bot.get_channel(CHANNEL_ID).send(file=file, embed=embed)
        if emoji_no_race_week is not None:
            await message.add_reaction(emoji_no_race_week)


async def edit_week_embed(date_: datetime.date):
    """Edits an already sent weeks embed."""
    message = await get_previous_bot_message()
    if f1.check_f1_race_week(date_):
        new_embed = await get_race_week_embed(date_)
    else:
        new_embed = await get_no_race_week_embed(date_)
    await message.edit(embed=new_embed)


async def get_previous_bot_message(max_messages=15) -> Union[discord.Message, None]:
    """Returns the discord.Message for the last message the bot sent, checks up to given
    number of previous messages."""
    bot_id = util.get_json_data("bot_id")  # the bots user id to check the previous messages
    prev_msgs = await bot.get_channel(CHANNEL_ID).history(limit=max_messages).flatten()  # list of prev messages
    prev_ids = [str(msg.author.id) for msg in prev_msgs]  # list of the user ids for all prev messages

    if bot_id in prev_ids:
        index = prev_ids.index(bot_id)  # first index of last bot msg
        return prev_msgs[index]


async def execute_week_embed() -> None:
    """Checks if the bot has sent an embed the week of the given date.
    If so then update and edit the embed, if not then send a new embed."""
    today = date.today()

    # Check if new year, archive f2 calendar json
    if "01-01" in str(today):
        util.archive_json("data/f2_calendar.json")

    # Retrieves the previous bot message. If a message is not found, it sets the date as 8 days before today
    message = await get_previous_bot_message()
    if message:
        prev_date = message.created_at.date()
    else:
        prev_date = today - timedelta(days=8)

    # If it has posted this week and its a race week: only edit the embed to update f2 times
    posted_cond = util.get_sunday_date_str(today) == util.get_sunday_date_str(prev_date)  # is same week as prev post?
    if posted_cond:  # same week then edit the embed
        await edit_week_embed(today)

    # if not same week: post new embed and save date
    else:
        race_week_emoji = util.get_json_data("race_week_emoji")
        no_race_week_emoji = util.get_json_data("no_race_week_emoji")
        await send_week_embed(today, race_week_emoji, no_race_week_emoji)


async def status(print_msg=True) -> None:
    """Runs execute_week_embed() and
    update_status_message() functions every 24 hours at scheduled time."""

    await update_status_message()  # start with status message, then wait until scheduled time to send embed
    now = datetime.now()
    future = datetime(now.year, now.month, now.day, SCHEDULED_HOUR, SCHEDULED_MINUTE)
    while True:
        # Wait to run until scheduled time
        now = datetime.now()
        if now.hour >= SCHEDULED_HOUR and now.minute > SCHEDULED_MINUTE:
            future += timedelta(days=1)  # if past scheduled time, wait until next day
        await sleep((future - now).seconds)

        f2.store_calendar_to_json(f2.scrape_calendar())  # update the f2 calendar json

        await execute_week_embed()

        # Lastly update the status message
        await update_status_message()

        if print_msg:
            print("Loop complete", datetime.today(), "UTC")

        future += timedelta(days=1)  # add 24 hours for next loop


@bot.command(aliases=["upd"])
async def update(ctx) -> None:
    """On recieving update command with the bots prefix, executes the weekly embed send/edit
    with todays updated info. Also updates the status message just incase.
    If the command was not in #bot channel, delete both the command message and the reply message."""
    await execute_week_embed()
    await update_status_message()

    # send reply message in the same channel
    msg_channel_id = ctx.message.channel.id
    reply = await bot.get_channel(msg_channel_id).send("Update done.")

    # if its not in the #bot channel, then delete both the user and bots messages after 2 seconds
    bot_channel_id = int(util.get_json_data("bot_channel_id"))
    if msg_channel_id != bot_channel_id:
        await sleep(2)
        await reply.delete()
        await ctx.message.delete()

    print("Update command executed", datetime.today(), "UTC")


@bot.event
async def on_ready() -> None:
    """On bot ready, start the status loop."""
    bot.loop.create_task(status())  # start the loop
    print("PIERRRE GASLYYYY!")


if __name__ == "__main__":
    bot.run(util.get_json_data("bot_token"))
