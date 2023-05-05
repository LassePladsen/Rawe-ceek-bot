# Rawe Ceek bot
 Discord bot that sends F1 and F2 session times each monday race week, in Norwegian. 
 Uses F1 api and scrapes F2 timings from fiaformula2.com
 It updates every 24 hours on race weeks to update the F2 times, as they are often not specified (shown as "TBC") until around the race week.
 
 To implement a new language (default messages are sent in norwegian) edit titles and descriptions in bot.send_rawe_ceek_embed(), and edit the weekday titles in util.print_all_days().
 It also sends norwegian timezone, which can be changed by changing the conversion in util.print_day_sessions() (seperately for the f1 and f2 sessions).
 
 Needs a discord bot token given in a file named "token.txt" by default.
 Run bot.py for the bot to be active.
 

