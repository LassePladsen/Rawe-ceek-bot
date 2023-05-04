from asyncio import sleep
from discord.ext import commands
from discord import File,Embed,Emoji
from datetime import date

import util
import formula2 as f2
import formula1 as f1

client = commands.Bot(command_prefix="&")

# Discord Channel ID
# channel_id = 886642751737827328         # "#test"-channel
channel_id = 1101176067290570802      # "#f1"-channel

async def send_rawe_ceek_embed():
    Today = date.today()
    # If its race week post the times, if not post no. weeks until next race week
    if f1.check_race_week(Today):
        title, des = util.print_all_week_info(Today)

        file = File("rawe_ceek_frog.png", filename="race.png")
        embed = Embed(title=title, description=des)
        embed.set_image(url="attachment://race.png")

        emoji = "<:gorilla:984044880575750174>"


        message = await client.get_channel(channel_id).send(file=file, embed=embed)
        await message.add_reaction(emoji)

    else:  # if not race week then post no. weeks until n# ext race week
        # Count how many weeks until next race week
        title = str(util.until_next_race_week(Today)) + " uker til neste rawe ceek..."

        en_date = util.get_event_date_str(f1.get_next_week_event(Today))
        no_date = str(int(en_date.split(" ")[0])) + " " + util.month_to_norwegian(en_date.split(" ")[1],
                                                                                  caps=False)
        des = "Neste dato er " + no_date
        emoji = "<:sadge:920711330955132929>"

        file = File("no_rawe_ceek.png", filename="sad.png")
        embed = Embed(title=title, description=des)
        embed.set_image(url="attachment://sad.png")
        message = await client.get_channel(channel_id).send(file=file, embed=embed)
        await message.add_reaction(emoji)

async def status():
    # Initialize, save todays date so it doesnt send again
    Prev_day = date.today()

    # Loops after 24 hours
    while True:
        Today = date.today()
        # Run if its monday (weekday=0) AND it hasnt already ran today
        if Today.weekday() == 0 and Today != Prev_day:
            # saves date so it doesnt execute twice in a day (bot can manually update via discord command):
            await send_rawe_ceek_embed()
            Prev_day = Today

        await sleep(24*3600)  # loops again after 24 hours (in seconds)



@client.event
async def on_ready():
    await send_rawe_ceek_embed()
    print("PIERRRE GASLYYYY!")


client.loop.create_task(status())
client.run(util.get_discord_bot_token("token.txt"))
