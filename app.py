import os
import os.path
import logging
import signal
import sys
from config import Config
#logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
import telethon
import json
import threading
import time

session_name = 'telegram'
me = None
client = telethon.TelegramClient(session = session_name, api_id = Config["api_id"], api_hash = Config["api_hash"], update_workers = 20)

lock_filename = threading.Lock()
completed_filename = 'completed.txt'
completed_filename_list = []
def loading_downloaded_filename():
    global completed_filename_list
    if not os.path.exists(completed_filename):
        return None
    with open(completed_filename) as f:
        for name in f:
            completed_filename_list.append(name.strip('\n'))
def write_downloaded_filename(name):
    if not os.path.exists(completed_filename):
        with open(completed_filename, 'w') as f:
            pass
    with lock_filename:
        with open(completed_filename, 'w+') as f:
            f.write('{}\n'.format(name))

def init():
    global me
    loading_downloaded_filename()
    client.connect()

    me = client.get_me()
    if me is None:
        client.sign_in(phone = Config["phone"])
        code = input("please input your code: ")
        me = client.sign_in(code = code)
        logging.info(me)
    else:
        #me = client.get_me()
        logging.info(me)

    client.add_update_handler(update_handler)

def get_possible_names(document):
    possible_names = []
    for attr in document.attributes:
        if isinstance(attr, telethon.tl.types.DocumentAttributeFilename):
            possible_names.insert(0, attr.file_name)

        elif isinstance(attr, telethon.tl.types.DocumentAttributeAudio):
            possible_names.append('{} - {}'.format(
                attr.performer, attr.title
            ))
    return possible_names

def process_handler(current, total):
    logging.info("downloading complete : {} %".format(current/total * 100))

def downloadMediaFile(message):
    #logging.info(str(message))
    file_path = '/data/downloads/'
    possible_names = get_possible_names(message.media.document)
    file_name = telethon.TelegramClient._get_proper_filename(
            file_path, 'document', telethon.utils.get_extension(message.media),
            date=message.date, possible_names=possible_names
        )

    #check file is if downloaded
    if file_name in completed_filename_list:
        logging.info("{}, has downloaded ...".format(file_name))
        return None
    else:
        completed_filename_list.append(file_name)
        write_downloaded_filename(file_name)
    
    logging.info("Start download file: {}.".format(file_name))
    #client.download_media(message, file_path, process_handler)
    client.download_media(message, file_path)
    client.send_message(Config['user_id'], 'Download {} completed.'.format(file_name))
    logging.info('Download {} completed.'.format(file_name))

def update_handler(update):
    '''
    UpdateNewMessage(
        message=Message(
            out=False, 
            mentioned=False, 
            media_unread=False, 
            silent=False, 
            post=False, 
            id=2906, 
            from_id=376585058, 
            to_id=PeerUser(user_id=376585058), 
            fwd_from=None, 
            via_bot_id=None, 
            reply_to_msg_id=None, 
            date=datetime.utcfromtimestamp(1512068474), 
            message='', 
            media=MessageMediaDocument(
                document=Document(
                    id=6127232058512113706, 
                    access_hash=7134142665936045460, 
                    date=datetime.utcfromtimestamp(1512068473),
                    mime_type='video/mp4', 
                    size=557657, 
                    thumb=PhotoSize(
                        type='s', 
                        location=FileLocation(
                            dc_id=5, 
                            volume_id=852711456, 
                            local_id=8748, 
                            secret=-7247416071172767183
                        ), 
                        w=51, 
                        h=90, 
                        size=1680
                    ), 
                    dc_id=5, 
                    version=0, 
                    attributes=[
                        DocumentAttributeVideo(
                            round_message=False, 
                            duration=4, 
                            w=360, 
                            h=640
                        )
                    ]
                ), 
                caption=None, 
                ttl_seconds=None
            ), 
            reply_markup=None, 
            entities=None, 
            views=None, 
            edit_date=None, 
            post_author=None, 
            grouped_id=None
        ), 
        pts=6983, 
        pts_count=1
    )
    '''
    logging.info(str(update))
    if isinstance(update, telethon.tl.types.UpdateNewMessage) and update.message.from_id == Config["user_id"] and update.message.media is not None:
        downloadMediaFile(update.message)

def signal_handler(signal, frame):
    logging.info("Ctrl + C was pressed , stop ...")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    #init
    init()
    '''
    logging.info(me.id)
    while True:
        count, messages, _ = client.get_message_history(me.id, limit= 10)
        logging.info('Get history total count: {}, message count: {}'.format(count, len(messages)))
        if count:
            while len(messages) > 0:
                m = messages.pop()
                logging.info(str(m))
                if m.from_id == Config["user_id"] and m.media is not None:
                    downloadMediaFile(m)
                    time.sleep(10)
        time.sleep(1)
    '''