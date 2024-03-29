# Rawe Ceek bot

Discord bot that sends F1 and F2 session times each monday race week, in Norwegian (can easily be changed).

Uses F1 api and scrapes F2 timings from fiaformula2.com.
Each loop the bot checks if today is a race week, then it checks if it has already posted this week. In this case it
updates the times and edits the embed, if it hasn't then it posts a new embed. If there is no race week it posts a
different embed. The reason for updating the times and editing the embed is because the F2 times are not always given,
they can be currently undefined given as "TBC".

To implement a new language (default messages are sent in norwegian) edit embed titles and descriptions in the two create
embed functions in bot.py, also edit the weekday titles in util.print_all_days(), and lastly edit the language
argument implementation in util.get_all_week_info().

It also sends norwegian timezone, which can be changed by changing the conversion in util.print_day_sessions() (remember
to do it seperately for the f1 and f2 sessions).

The bot needs multiple string values given in a json default 'discord_data.json'. Inside the template '
template_discord_data.json' is the default key strings used.

## Requirements
- Python >= 3.9.0.
- See requirements.txt for package/module requirements.

## Installation
Clone the repo 
```shell
git clone https://github.com/LassePladsen/Rawe-ceek-bot.git
```
Install the dependencies
```shell
cd Rawe-ceek-bot
```
```shell
python3 -m pip install -r requirements.txt
```

## Setup the discord bot
This bot script needs three things to run: the discord bot token, the bot user ID, and the channel ID of whatever channel it should send in. 
Creating the discord bot from the discord developer portal you can follow [discord's guide here](https://discordpy.readthedocs.io/en/stable/discord.html).
After creating your bot and inviting it to your server, make sure you get its token from the 'Bot' submeny on discord's dev portal, and then also the bot's id under the submeny 'OAuth2' -> 'General': 'Client id'.

Then, in the repo directory, create a `data/discord_data.json` file from the template `data/template_discord_data.json` and fill in the following required values: `"bot_token", "bot_id", "channel_id"`. To get your channel id you may have to enable developer mode on discord, then right click the channel and copy its id.

## Running
Run the bot script 
```shell
python3 bot.py
```

# "Rawe ceek??"
See https://knowyourmeme.com/memes/rawe-ceek.
![Rawe ceek origin](data/raweceek_origin_meme.jpg)
