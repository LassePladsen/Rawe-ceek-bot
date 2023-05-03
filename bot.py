from asyncio import sleep
from discord.ext import commands


import main

client = commands.Bot(command_prefix="$")

# Discord Channel ID
channel_id = 1101176067290570802

async def send_msg(msg):
    await client.get_channel(channel_id).send(msg)