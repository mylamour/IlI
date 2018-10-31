import os
import fire
import uuid
import base64
import logging
from telethon import TelegramClient, events, sync
from telethon.tl.types import PeerUser, PeerChat, PeerChannel

api_id=123456
api_hash='aaa'

client = TelegramClient('session_name', api_id, api_hash)
client.start()

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('telethon').setLevel(level=logging.WARNING)
idownload = logging.getLogger('image')
idownload.setLevel(level=logging.INFO)

def download(channel,output):

    titswiki = client.get_entity(channel)
    c = client.get_entity(PeerChannel(titswiki.id))

    if not os.path.isdir(output):
        os.makedirs(output)

    for m in client.iter_messages(c):
        uuidstring = str(uuid.uuid1())
        z = base64.encodebytes(uuid.UUID(uuidstring).bytes).decode("ascii").rstrip('=\n').replace('/', '_')
        suid = "{}/{}".format(output,z)

        m.download_media(suid)

        fname = "{}.jpg".format(suid)
        if os.path.isfile(fname):
            idownload.info("✔  {} Downloaded Sucessful".format(fname))

if __name__ == '__main__':
    fire.Fire()