import logging
import sys

import traceback

from asyncio import sleep, get_event_loop, Lock
from datetime import datetime, timedelta
from typing import Union

import discord
from discord.ext import commands

import formula1 as f1
import formula2 as f2
import util

# Discord Channel ID for the bot to work in
CHANNEL_ID = int(util.get_json_data("channel_id"))

# Status run timing (24 hour format)
# NOTE: in norway it should be after 2 am since get_previous_bot_message() is in UTC time (norway time minus 2 hours).
scheduled_hour = 5
scheduled_minute = 0


# Create logging to a bot.log file
LOG_FILENAME = "bot.log"
logger = logging.getLogger(__name__)
fh = logging.FileHandler(LOG_FILENAME)  # log to logfile
fh.setFormatter(logging.Formatter("[%(asctime)s - %(levelname)s] - %(message)s"))
logger.addHandler(fh)
logger.setLevel(logging.INFO)


# Discord bot permissions
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="&", intents=intents, case_insensitive=True)

# Startup check
loop = get_event_loop()
try:
    loop.run_until_complete(util.startup_check())
except KeyboardInterrupt:
    loop.close()
    sys.exit(1)


# Lock to prevent multiple instances of the status task
lock = Lock()

async def get_race_week_embed(date_: datetime.date) -> discord.Embed:
    """Returns embed for a race week with a 'race week' image."""
    title, des = f1.get_all_week_info(
        date_
    )  # title and description for the embed message
    embed = discord.Embed(title=title, description=des)
    embed.set_image(url="attachment://race.png")
    return embed


async def get_no_race_week_embed(date_: datetime.date) -> Union[discord.Embed, None]:
    """Returns embed for a non race week with a 'no race week' image. Returns None if something messes up
    and there actually is no race week found."""
    week_count = f1.until_next_race_week(date_)
    if week_count == 0:
        logger.error(
            "bot.get_no_race_week_embed(): Count until next race is zero,"
            " meaning there is a race this week. Can't return a no_race_week_embed, returning None early."
        )
        return
    elif week_count == 1:
        title = (
            str(week_count) + " uke til neste rawe ceek..."
        )  # title for embed message

    else:
        title = (
            str(week_count) + " uker til neste rawe ceek..."
        )  # title for embed message

    next_event = f1.get_next_week_event(date_)
    next_event_name = next_event["EventName"]

    en_date = util.get_event_date_str(next_event)
    no_date = (
        str(int(en_date.split(" ")[0]))
        + " "
        + util.month_to_norwegian(en_date.split(" ")[1], caps=False)
    )
    des = f"{next_event_name} den {no_date}."  # description for embed message
    embed = discord.Embed(title=title, description=des)
    embed.set_image(url="attachment://norace.png")
    return embed


async def update_status_message() -> None:
    """Updates the bots status message with either a message depending on if its a race week or not."""
    today = datetime.now().date()
    if f1.is_f1_race_week(today):
        # Set bot satus message to rawe ceek
        activity = discord.Activity(
            type=discord.ActivityType.watching, name="the RACE WEEK!"
        )
        await bot.change_presence(status=discord.Status.online, activity=activity)

    else:
        # Set bot satus message to no rawe ceek
        until_next_race = f1.until_next_race_week(today)
        if until_next_race == 1:
            until_next_race = str(until_next_race) + " week"
        else:
            until_next_race = str(until_next_race) + " weeks"

        activity = discord.Activity(
            type=discord.ActivityType.watching, name=f"nothing for {until_next_race}..."
        )
        await bot.change_presence(status=discord.Status.online, activity=activity)


async def send_week_embed(
    date_: datetime.date, emoji_race_week=None, emoji_no_race_week=None
):
    """Sends an embed for the week, either embed for race week or non race week."""
    # If its race week post the times, if not then post no. of weeks until next race week
    if f1.is_f1_race_week(date_):
        race_week_image = util.get_json_data("race_week_image")
        file = discord.File(race_week_image, filename="race.png")
        embed = await get_race_week_embed(date_)
        message = await bot.get_channel(CHANNEL_ID).send(file=file, embed=embed)
        if emoji_race_week is not None:
            await message.add_reaction(emoji_race_week)

    else:  # if not race week then post no. weeks until next race week
        # Count how many weeks until next race week
        embed = await get_no_race_week_embed(date_)
        if not embed:  # no embed returned
            logger.error(
                "send_week_embed(): No embed returned for no race week from get_no_race_week_embed()."
                " sending no embed."
            )
            return

        no_race_week_image = util.get_json_data("no_race_week_image")
        file = discord.File(no_race_week_image, filename="norace.png")

        message = await bot.get_channel(CHANNEL_ID).send(file=file, embed=embed)
        if emoji_no_race_week is not None:
            await message.add_reaction(emoji_no_race_week)


async def edit_week_embed(date_: datetime.date):
    """Edits an already sent weeks embed."""
    message = await get_previous_bot_message()
    if f1.is_f1_race_week(date_):
        new_embed = await get_race_week_embed(date_)
    else:
        new_embed = await get_no_race_week_embed(date_)
        if not new_embed:
            logger.error(
                "edit_week_embed(): No embed returned for no race week from get_no_race_week_embed()."
                " editing no embed."
            )
            return
    await message.edit(embed=new_embed)


async def get_previous_bot_message(max_messages=15) -> Union[discord.Message, None]:
    """Returns the discord.Message for the last message the bot sent, checks up to given
    number of previous messages."""
    bot_id = util.get_json_data(
        "bot_id"
    )  # the bots user id to check the previous messages
    prev_msgs = (
        await bot.get_channel(CHANNEL_ID).history(limit=max_messages).flatten()
    )  # list of prev messages
    if not prev_msgs:
        logger.warning(
            "get_previous_bot_message(): No previous messages found in channel, returning None early."
        )
        return

    prev_ids = [
        str(msg.author.id) for msg in prev_msgs
    ]  # list of the user ids for all prev messages

    if bot_id in prev_ids:
        index = prev_ids.index(bot_id)  # first index of last bot msg
        return prev_msgs[index]


async def execute_week_embed() -> None:
    """Checks if the bot has sent an embed the week of the given date.
    If so then update and edit the embed, if not then send a new embed."""
    today = datetime.now().date()

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
    posted_cond = util.get_sunday_date_str(today) == util.get_sunday_date_str(
        prev_date
    )  # is same week as prev post?

    if posted_cond:  # same week then edit the embed
        await edit_week_embed(today)

    # if not same week: post new embed and save date
    else:
        race_week_emoji = util.get_json_data("race_week_emoji")
        no_race_week_emoji = util.get_json_data("no_race_week_emoji")
        await send_week_embed(today, race_week_emoji, no_race_week_emoji)


async def status() -> None:
    """Updates weekly embed and status message, calling execute_week_embed() and
    update_status_message(), every day at scheduled time (global variable). It
    does the update once before starting the schedule loop."""

    async def status_task():
        """The task to schedule"""
        # Lock the critical status task with asyncio.Lock()
        # This will hopefully prevent multiple embeds being posted at the same time
        async with lock:
            # Log start of task
            logger.info("Status task starting")

            retries = 0
            max_retries = 5
            while True:
                try:
                    await update_status_message()

                    f2.store_calendar_to_json(
                        f2.scrape_calendar(logger)
                    )  # update the f2 calendar json

                    # Weekly embed
                    await execute_week_embed()

                    # Status message
                    await update_status_message()

                    # Log end of the task and print to terminal
                    logmsg = "Status task complete"
                    print(logmsg + f" {datetime.now()} UTC")
                    logger.info(logmsg)
                    break

                # Log exception and add a retry after 10 seconds
                except Exception as e:
                    if retries < max_retries:
                        logger.error(
                            f"An error occured in status_task ({retries=}): {type(e)}: {e}"
                        )

                    else:
                        logger.error("Max retries reached, see error traceback:")
                        traceback.print_exc(file=open(LOG_FILENAME, "a"))
                        break

                    retries += 1
                    await sleep(10)  # sleep and retry

    # Run the task once, then create the schedule loop
    await status_task()

    # Start the scheduling loop
    now = datetime.now()
    scheduled_time = datetime(
        now.year, now.month, now.day, scheduled_hour, scheduled_minute
    )
    while True:
        # Wait to run until scheduled time
        now = datetime.now()
        if now > scheduled_time:
            scheduled_time += timedelta(
                days=1
            )  # if past scheduled time, wait until next day

        seconds = (scheduled_time - now).seconds
        logger.info(f"Sleeping {seconds} seconds until {scheduled_time}")
        await sleep(seconds)
        logger.info("Waking up")
        await status_task()


@bot.command(aliases=["upd"])
async def update(ctx) -> None:
    """On recieving update command with the bots prefix, executes the weekly embed send/edit
    with todays updated info. Also updates the status message just incase.
    If the command was not in #bot channel, delete both the command message and the reply message.
    """

    # Log start
    logger.info("Update command starting")

    try:
        f2.store_calendar_to_json(
            f2.scrape_calendar(logger)
        )  # update the f2 calendar json

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

        # Log end
        logmsg = "Update command executed"
        print(logmsg + f" {datetime.now()} UTC")
        logger.info(logmsg)

    # Log error
    except Exception as e:
        logger.exception(f"An error occurred in on_ready: {type(e)}: {e}")


@update.error
async def update_error(ctx, error):
    """Send error in channel on recieved update command when it raises an error"""
    if isinstance(error, commands.CommandError):
        # Handle command-specific errors
        await ctx.send("An error occurred during the update command.")
        logger.error(
            f"An error occurred during the update command: {type(error)}: {error}"
        )


@bot.command()
async def ping(ctx) -> None:
    """Bot responds "pong" in same channel."""
    msg_channel_id = ctx.message.channel.id
    await bot.get_channel(msg_channel_id).send("Pong")
    print("Pong", datetime.now(), "UTC")


@bot.event
async def on_ready() -> None:
    """On bot ready, create the status loop task and print to terminal"""
    try:
        bot.loop.create_task(status())

        hour = str(scheduled_hour)
        if len(hour) == 1:
            hour = "0" + hour
        minute = str(scheduled_minute)
        if len(minute) == 1:
            minute = "0" + minute

        logger.info(
            f"Bot ready with scheduled_time={hour}:{minute} in channel {CHANNEL_ID}"
        )
        print("PIERRRE GASLYYYY!")

    # Log error
    except Exception as e:
        logger.exception(f"An error occurred in on_ready: {type(e)}: {e}")


if __name__ == "__main__":
    # Run bot loop
    bot.run(util.get_json_data("bot_token"))
