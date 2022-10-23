# import modules for logger initialization
import math
import os
import sys
import time as t
import pytz
from datetime import time, timedelta
from interactions import Button, ButtonStyle, Emoji

# set environment variables
os.environ["LOGURU_AUTOINIT"] = "0"
os.environ["LOGURU_FORMAT"] = " | ".join(
    [
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS!UTC}</green>",
        "<level>{level: <8}</level>",
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>",
        "<level>{message}</level>",
    ]
)

# initialize logger
from loguru import logger

server_offset = t.localtime().tm_gmtoff / 3600
logger.add(sys.stderr)
logger.add("./logs/{time:YYYY-MM-DD_HH-mm-ss_SSS!UTC}.log", rotation=time(math.trunc(server_offset) if server_offset >= 0 else 24 + math.trunc(server_offset), int(server_offset * 4 % 4 * 15) if not server_offset.is_integer() else 0, 0, 0), retention=timedelta(days=14), encoding="utf-8", compression="gz", diagnose=False)


from datetime import datetime
import json
import re
from interactions import Embed, EmbedFooter, EmbedImageStruct
from random import randint, choice
from io import BytesIO
from decouple import config 
import aiohttp
import aiofiles

ratelimit = {}

o_enc = ["o", "ο", "о", "ᴏ"]
o_current = "oooo"
a_enc = {'0': 'a', '1': 'à', '2': 'á', '3': 'â', '4': 'ã', '5': 'ä', '6': 'å', '7': 'æ', '8': 'A', '9': 'À', 'a': 'Á', 'b': 'Â', 'c': 'Ã', 'd': 'Ä', 'e': 'Å', 'f': 'Æ'}

def raweb(title: str = "", desc: str = "", image: EmbedImageStruct = None, footer: EmbedFooter = None, color: int = None):
    return Embed(
        title=title, description=desc, image=image, footer=footer, color=color if color else randint(0, 0xFFFFFF)
    )

async def api_request(url: str, headers:dict=None):
    if datetime.now().timestamp() < (ratelimit['trace.moe'] if 'trace.moe' in ratelimit else 0):
        return 429
    async with aiohttp.ClientSession() as s, s.get(url, headers=headers) as r:
        if r.status == 429:
            if url.startswith('https://api.trace.moe/search?url='):
                ratelimit['trace.moe'] = r.headers['x-ratelimit-reset']
            return 429
        return await r.json()

async def request_img(url: str):
    async with aiohttp.ClientSession() as s, s.get(url) as r:
        return BytesIO(await r.content.read())
    
async def requset_raw_img(url: str):
    async with aiohttp.ClientSession() as s, s.get(url) as r:
        if r.status == 404:
            return None
        return await r.content.read()

async def translate(text: str, target: str, source: str = ''):
    async with aiohttp.ClientSession() as s, s.post('https://api-free.deepl.com/v2/translate', headers={"Authorization": f"DeepL-Auth-Key {config('deepl')}"}, data={"text": text, "target_lang": target, "source_lang": source}) as r:
        if r.status not in [429, 456]:
            used, limit = await translator_quota()
            log = f"Translated {len(text)} words. DeepL quota: {used}/{limit} ({used/limit*100}%)"
            if used/limit > 0.9:
                logger.warning(log)
            else:
                logger.info(log)
            return (j:=await r.json())['translations'][0]['text'], j['translations'][0]['detected_source_language']
        if r.status == 429:
            logger.warning(f"DeepL rate limit exceeded while translating {len(text)} words.")
        elif r.status == 456:
            logger.warning(f"DeepL quota exceeded while translating {len(text)} words.")
        return r.status, None

async def translator_quota():
    async with aiohttp.ClientSession() as s, s.post('https://api-free.deepl.com/v2/usage', headers={"Authorization": f"DeepL-Auth-Key {config('deepl')}"}) as r:
        return (j:=await r.json())['character_count'], j['character_limit']

def lengthen_url(url: str, mode: str = "o"):
    result = re.findall(r"(http:\/\/|https:\/\/)([\w_-]+(?:(?:\.[\w_-]+)+)[\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])", url)
    if not result:
        return None
    if result[0][1].startswith("ooooooooooooooooooooooo.ooo") or result[0][1].startswith("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.com"):
        return 1
    match mode:
        case "o":
            url = ''.join(list(result[0]))
            utf8 = []
            for i in url:
                code = ord(i)
                if code < 0x80:
                    utf8.append(code)
                elif code < 0x800:
                    utf8.append(0xc0 | (code >> 6), 0x80 | (code & 0x3f))
                elif code < 0xd800 and code >= 0xe000:
                    utf8.append(0xe0 | (code >> 12), 0x80 | ((code >> 6) & 0x3f), 0x80 | (code & 0x3f))
                else:
                    code = ((code & 0x3ff) << 10) | (code & 0x3ff)
                    utf8.append(0xf0 | (code >> 18), 0x80 | ((code >> 12) & 0x3f), 0x80 | ((code >> 6) & 0x3f), 0x80 | (code & 0x3f))
            base4 = []
            for i in utf8:
                if i == 0:
                    base4.append('0'.rjust(4, '0'))
                nums = []
                while i:
                    i, r = divmod(i, 4)
                    nums.append(str(r))
                base4.append(''.join(reversed(nums)).rjust(4, '0'))
            return 'http://ooooooooooooooooooooooo.ooo/'+o_current+''.join(list(map(lambda x: o_enc[int(x)], ''.join(base4))))
        case "a":
            url = 'https://'+result[0][1]
            filler = 'a'
            new = ''.join(list(map(lambda x: a_enc[x], ''.join([hex(ord(i))[2:] for i in url]))))
            while len(new)+len(filler) < 200:
                filler += choice(list(a_enc.values()))
            return 'https://aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.com/' + filler + "?" + new
        case _:
            return None

async def bullshit_generator(topic: str, length: int):
    async with aiofiles.open("./assets/bullshit.json", encoding="utf-8") as f:
        data = json.loads(await f.read())
        generated = ''
    while topic not in generated:
        generated = ''
        while len(generated) < length:
            r = randint(0, 99)
            if r <3 and generated and generated[-1] in "。？！?!":
                sentence = '\n\n'
            elif r < 25:
                sentence = choice(data["famous"]).replace("[A]", choice(data['before'])).replace("[B]", choice(data['after']))
            else:
                sentence = choice(data["bullshit"]).replace("x", topic)
            if sentence == '\n\n' or sentence not in generated:
                generated += sentence
    return generated

def parse_sqlite_datetime(dt: str):
    return datetime.strptime(dt, '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=pytz.utc)

destroy = Button(style=ButtonStyle.DANGER, custom_id="destroy", label="移除訊息", emoji=Emoji(name="🗑️"))