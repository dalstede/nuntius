# Nuntius - A Zulip file watchdog bot

A Zulip (https://github.com/zulip) bot that watches an SMB share and informs users in personal messages about changes they want to be informed about. The bot can be messaged to change the text strings about which the bot will inform.

This is my first try of creating a Zulip bot.

The bot consists of two python files, a configuration file and an SQLite database:
- `nuntius_watchdog.py`: A python script running in a loop watching the SMB folder for changes, which will send messages to the users according to their text-string subscriptions
- `nuntius.py`: An interactive Zulip-bot which will be executed according to Zulip's interactive bot guide (https://zulip.com/api/running-bots), providing an interface to add, delete and list the text strings that the user wants to be informed about
- `bot_config.ini`: A config file containing the SMB credentials to be used, as well as the paths to the network folder, the zuliprc-config file with the bot API key and the user_prefs.db
- `user_prefs.db`: An SQLite database containing the email address of the users and the text strings they want to be informed about

### nuntius_watchdog

The folder will be monitored for the following events:
- **on_modified** (file moved to here or renamed within the folder)
- **on_created** (file created in the watched directory)

The text strings to be monitored will be read from the user_prefs.db. If a matching event is detected the user will be informed by personal messages

### nuntius

The interactive bot will accept the following commands:
1. add_strings [text_strings]: Add multiple text strings for notifications (separated by semicolons).
1. delete_strings [text_strings]: Delete multiple text strings (separated by semicolons).
1. list_strings: List all the text strings you're watching.

The [text_strings] will be saved together with the email address with the user in the user_prefs.db

#### file locations

First, I followed the instructions provided by Zulip for setting up a bot development version: https://zulip.com/api/writing-bots

In my testing setup I've placed all files in the following in the bot folder: `python-zulip-api\zulip_bots\zulip_bots\bots\nuntius`

## Outlook

This is a personal project to solve a very specific use case and it also allowed me to learn the basics of how a Zulip bot can be implemented. I'm sure there is lots of room for improvement and I'm grateful for any feedback to learn from. Depending on how helpful the bot will be I might flesh it out more and fix issues that I haven't encountered while developing it. One obvious improvement would be to not tie the text strings in the database to the user's email but instead the user_id (during testing the email was more helpful because it allowed to easily keep track of the saved entries).


