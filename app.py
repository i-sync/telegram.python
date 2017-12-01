import os
import os.path
import logging
import signal
import sys
import telethon
import json
from config import Config
logging.basicConfig(level=logging.INFO)

session_name = 'telegram'

client = telethon.TelegramClient(session = session_name, api_id = Config["api_id"], api_hash = Config["api_hash"], update_workers = 20)

def init():
    client.connect()

    if not os.path.exists('{}.session'.format(session_name)):
        client.sign_in(phone = Config["phone"])
        code = input("please input your code: ")
        me = client.sign_in(code = code)
        print(me)
    else:
        me = client.get_me()
        print(me)

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
    print("downloading complete : {} %".format(current/total * 100))

def downloadMediaFile(message):
    #print(str(message))
    file_path = 'downloads/'
    possible_names = get_possible_names(message.media.document)
    file_name = telethon.TelegramClient._get_proper_filename(
            file_path, 'document', telethon.utils.get_extension(message.media),
            date=message.date, possible_names=possible_names
        )
    print("Start download file: {}.".format(file_name))
    client.download_media(message, file_path, process_handler)
    client.send_message(Config['user_id'], 'Download {} completed.'.format(file_name))
    print('Download {} completed.'.format(file_name))

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
    if isinstance(update, telethon.tl.types.UpdateNewMessage) and update.message.from_id == Config["user_id"] and update.message.media is not None:
        downloadMediaFile(update.message)

def signal_handler(signal, frame):
    print("Ctrl + C was pressed , stop ...")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    #init
    init()

    signal.pause()