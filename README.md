# Rawe Ceek bot
 Discord bot that sends F1 and F2 session times each monday race week, in Norwegian. 
 Uses F1 api and scrapes F2 timings from fiaformula2.com.
 Bot updates every 24 hours, if there is a race week it checks if it has already posted this week. In that case it updates the times and edits the embed, if not it posts a new embed for the week. If there is no race week it posts a different embed. The reason for updating the times and editing the embed is because the F2 times are not always given, they can be currently undefined given as "TBC".
 
 To implement a new language (default messages are sent in norwegian) edit titles and descriptions in the two create embed functions in bot.py, also edit the weekday titles in util.print_all_days(), and then also edit the language argument implementation in util.get_all_week_info() 
 It also sends norwegian timezone, which can be changed by changing the conversion in util.print_day_sessions() (remember to do it seperately for the f1 and f2 sessions).
 
The bot needs multiple string values given in a json default 'discord_data.json'. Below are the values needed with default key used.
-Discord bot token: "bot_token"
-Discord bot user id: "bot_id"
-Discord channel id: "channel_id"
-Image to post during race week: "rawe_ceek_image"
-Image to post during non-race week: "no_rawe_ceek_image"
-(Optional) reaction emoji id during race week: "rawe_ceek_emoji"
-(Optional) reaction emoji id during non-race week: "no_rawe_ceek_emoji"
 
 Run bot.py to start the bot loop.
 

