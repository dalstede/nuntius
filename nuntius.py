import zulip
import sqlite3
import re
import logging
import os
import configparser

from typing import Any, Dict

from zulip_bots.lib import BotHandler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

config = configparser.ConfigParser()
config.read("bot_config.ini")
config_path = os.path.abspath("bot_config.ini")
logging.debug(f"config file: {config_path}")

# SQLite database path
db_path = config.get("Database", "db_path")
logging.debug(f"database file: {db_path}")

class NuntiusHandler:
    def usage(self) -> str:
        return """
        This is an interactive bot that will allow users to manage the filename changes they want to be informed about
        """

    def handle_message(self, message: Dict[str, Any], bot_handler: BotHandler) -> None:

        logging.debug(f"input: {message}")

        pref = PreferenceManager(bot_handler)
        pref.process_message(message)
        return

class PreferenceManager:
    def __init__(self, botHandler) -> None:
        self.botHandler = botHandler

    def add_user_strings(self, email, strings):
        try:
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            for string in strings:
                cursor.execute("INSERT OR IGNORE INTO user_prefs (zulip_email, text_string) VALUES (?, ?)", (email, string.strip()))
            connection.commit()
        except Exception as e:
            logging.error(f"exception during database connection (add_user_strings): {repr(e)}")
        finally:
            connection.close()

    def delete_user_strings(self, email, strings):
        try:
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            for string in strings:
                cursor.execute("DELETE FROM user_prefs WHERE zulip_email = ? AND text_string = ?", (email, string.strip()))
            connection.commit()
        except Exception as e:
            logging.error(f"exception during database connection (delete_user_strings): {repr(e)}")
        finally:
            connection.close()

    def get_user_strings(self, email):
        try:
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            cursor.execute("SELECT text_string FROM user_prefs WHERE zulip_email = ?", (email,))
            strings = cursor.fetchall()
            connection.close()
            return [string_tuple[0] for string_tuple in strings]
        except Exception as e:
            logging.error(f"exception during database connection (get_user_strings): {repr(e)}")
        finally:
            connection.close()

    def process_message(self, message):
        sender_email = message["sender_email"]
        content = message["content"].strip()

        if content.startswith("add_strings"):
            try:
                text_strings = content.split(" ", 1)[1].split(";")
                self.add_user_strings(sender_email, text_strings)
                response = f"Strings '{text_strings}' added for notifications."
            except Exception as e:
                response = "Error: Invalid input. Please provide a valid regex pattern."
                logging.error(f"exception during add_string: {content}, {repr(e)}")

        elif content.startswith("delete_strings"):
            try:
                text_strings = content.split(" ", 1)[1].split(";")
                self.delete_user_strings(sender_email, text_strings)
                response = f"Strings {text_strings} deleted."
            except Exception as e:
                response = f"Error: Could not delete strings {text_strings}"
                logging.error(f"exception during delete_string: {content}, {repr(e)}")

        elif content.startswith("list_strings"):
            text_strings = self.get_user_strings(sender_email)
            if text_strings:
                response = f"Text strings you're watching:\n- " + "\n- ".join(text_strings)
            else:
                response = "You have no text strings currently being watched."

        else:
            response = (
            "Available commands:\n"
            "1. add_strings [text_strings]: Add multiple text strings for notifications (separated by semicolons).\n"
            "2. delete_strings [text_strings]: Delete multiple text strings (separated by semicolons).\n"
            "3. list_strings: List all the text strings you're watching."
            )

        self.botHandler.send_reply(message, response)

handler_class = NuntiusHandler