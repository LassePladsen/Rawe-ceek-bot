from asyncio import sleep
from discord.ext import commands
from datetime import date

import util
import formula2 as f2
import formula1 as f1

client = commands.Bot(command_prefix="&")

# Discord Channel ID
channel_id = 886642751737827328         # "#test"-channel
# channel_id = 1101176067290570802      # "#f1"-channel

async def send_msg(msg):
    await client.get_channel(channel_id).send(msg)

async def status():
    # Initialize, save todays date so it doesnt send again
    prev_day = date.today()

    # Loops after 24 hours
    while True:
        today = date.today()
        # Run if its monday (weekday=0) AND it hasnt already ran today
        if today.weekday() == 0 and today != prev_day:
            # saves date so it doesnt execute twice in a day (bot can manually update via discord command):
            prev_day = today

            # If its race week post the times, if not post no. weeks until next race week
            if f1.check_race_week():
                Event = f1.get_week_event(today)

                f1_days = f1.sort_sessions_by_day(Event)
                f2_calendar = f2.get_calendar()
                f2_days = f2.extract_days(Event, f2_calendar)

                eventtitle = util.print_event_info(Event)
                eventinfo = util.print_all_days(Event, f2_calendar, f2_days, f1_days)

                await client.get_channel(channel_id).send(eventtitle+eventinfo)
            else: # if not race week then post no. weeks until n# ext race week
                ...


        await sleep(24*3600)  # loops again after 24 hours (in seconds)



@client.event
async def on_ready():
    today = date.today()
    msg = util.print_all_week_info(today)
    await client.get_channel(channel_id).send(msg)
    print("PIERRRE GASLYYYY!")


# client.loop.create_task(status())
client.run(util.get_discord_token)
