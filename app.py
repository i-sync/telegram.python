import os
import os.path
import logging
import signal
import sys
import telethon
from config import Config

def signal_handler(signal, frame):
    print("Ctrl + C was pressed , stop...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


session_name = 'telegram'
client = telethon.TelegramClient(session = session_name, api_id = Config["api_id"], api_hash = Config["api_hash"], update_workers = 1)
client.connect()

if not os.path.exists('{}.session'.format(session_name)):
    client.sign_in(phone = Config["phone"])
    code = input("please input your code: ")
    me = client.sign_in(code = code)
    print(me)
else:
    me = client.get_me()
    print(me)

def update_handler(update)
    if

if __name__ == "__main__":
    signal.pause()