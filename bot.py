from asyncio import sleep
from discord.ext import commands
from datetime import date

import Util

client = commands.Bot(command_prefix="&")

# Discord Channel ID
channel_id = 1101176067290570802
# Discord bot token

async def send_msg(msg):
    await client.get_channel(channel_id).send(msg)

async def status():
    # initialize
    prev_day = date.today()
    # Loops again after 24 hours
    while True:
        today = date.today()
        # Run if its monday (weekday=0) AND it hasnt already ran today
        if today.weekday() == 0 and today != prev_day:
            # saves date so it doesnt execute twice in a day (bot can manually update via discord command):
            prev_day = today

            # If its race week post the times, if not post no. weeks until next race week
            if Util.check_race_week():
                Event = Util.get_week_event(today)
                sessions = sort_sessions_by_day(Event)
                # FRIDAY SESSIONS:
                ...
            else: # if race week then post no. weeks until next race week


        await sleep(24*3600)  # loops again after 24 hours (in seconds)


def reply(i):
    return ...

client.loop.create_task(status())
client.run("MTEwMzM0MjAxOTg3Njc2MTcyMQ.GDZKrD.q667R8P9yZzy9VoosKIl4GplEZbeE9abbRWhoM")