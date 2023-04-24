import time
import logging
import watchdog.events
import watchdog.observers
import re
import zulip
import sqlite3
import os
import configparser
from smb.SMBConnection import SMBConnection

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

# Load config file
config = configparser.ConfigParser()
config.read("bot_config.ini")

# Load config values
config_path = os.path.abspath("bot_config.ini")
logging.debug(f"config file: {config_path}")
db_path = config.get("Database", "db_path")
logging.debug(f"db file: {db_path}")
zuliprc_path = config.get("Zulip", "zuliprc_path")
logging.debug(f"zuliprc file: {zuliprc_path}")

smb_username = config.get("SMB", "username")
smb_password = config.get("SMB", "password")
smb_server = config.get("SMB", "smb_server")
watched_folder = config.get("SMB", "watched_folder")

# Connect to Zulip
client = zulip.Client(config_file=zuliprc_path)

# Connect to SMB-Server
conn = SMBConnection(smb_username, smb_password, "", smb_server, use_ntlm_v2=True, is_direct_tcp=True)
conn.connect(smb_server,445)

# Define a custom event handler for file system events
class SMBFileEventHandler(watchdog.events.FileSystemEventHandler):
    def process(self, event):
        if type(event) == watchdog.events.FileMovedEvent:
            filename = os.path.basename(event.dest_path)
        else:
            filename = os.path.basename(event.src_path)
        
        users_and_patterns = self.get_users_and_patterns()

        for email, pattern in users_and_patterns:
            if re.match(pattern, filename):
                message = {
                    "type": "private",
                    "to": email,
                    "content": f"File '{filename}' was {event.event_type} in the SMB share: {filename}",
                }
                response = client.send_message(message)
                logging.info(f"Sent notification message: {response}")

    def on_created(self, event):
        logging.info(f"{event.src_path} was created: {type(event)}")
        self.process(event)

    def on_moved(self, event):
        logging.info(f"{event.src_path} was moved: {type(event)}, now {event.dest_path}")
        self.process(event)

    def get_users_and_patterns(self):
        try:
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            cursor.execute("SELECT zulip_email, text_string FROM user_prefs")
            users_and_patterns = cursor.fetchall()
        except Exception as e:
            logging.error(f"exception during database connection (get_users_and_patterns): {repr(e)}")
        finally:
            connection.close()
        return users_and_patterns

# Set up the file system observer
event_handler = SMBFileEventHandler()
observer = watchdog.observers.Observer()
observer.schedule(event_handler, watched_folder, recursive=True)

# Start the file system observer
logging.info(f"Watching network share {watched_folder} for new files...")
observer.start()

# Keep the script running until it is interrupted
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
    conn.close()
    logging.info("Script terminated by user.")
observer.join()

# Disconnect from the SMB server
conn.close()