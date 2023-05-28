# Rawe Ceek bot
 Discord bot that sends F1 and F2 session times each monday race week, in Norwegian. 
 
 Uses python version 3.9.
 
 Uses F1 api and scrapes F2 timings from fiaformula2.com.
 Each loop the bot checks if today is a race week, then it checks if it has already posted this week. In this case it updates the times and edits the embed, if it hasn't then it posts a new embed. If there is no race week it posts a different embed. The reason for updating the times and editing the embed is because the F2 times are not always given, they can be currently undefined given as "TBC".
 
 To implement a new language (default messages are sent in norwegian) edit titles and descriptions in the two create embed functions in bot.py, also edit the weekday titles in util.print_all_days(), and then also edit the language argument implementation in util.get_all_week_info() 
 It also sends norwegian timezone, which can be changed by changing the conversion in util.print_day_sessions() (remember to do it seperately for the f1 and f2 sessions).
 
The bot needs multiple string values given in a json default 'discord_data.json'. Inside the template 'template_discord_data.json' is the default key strings used.


Run bot.py to start the bot loop.
 

