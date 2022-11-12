#  __      __        .__  __    __                  ___.
# /  \    /  \_______|__|/  |__/  |_  ____   ____   \_ |__ ___.__. /\
# \   \/\/   /\_  __ \  \   __\   __\/ __ \ /    \   | __ <   |  | \/
#  \        /  |  | \/  ||  |  |  | \  ___/|   |  \  | \_\ \___  | /\
#   \__/\  /   |__|  |__||__|  |__|  \___  >___|  /  |___  / ____| \/
#        \/                              \/     \/       \/\/
#                   .___  __         __________          __  .__
#                   |   |/  |_  _____\______   \ _______/  |_|  |
#                   |   \   __\/  ___/|       _// ____/\   __\  |
#                   |   ||  |  \___ \ |    |   < <_|  | |  | |  |__
#                   |___||__| /____  >|____|_  /\__   | |__| |____/
#                                  \/        \/    |__|

import tracemalloc
from random import randint

tracemalloc.start(25)

version = "development"

# import modules for the bot
import asyncio
import os
import traceback

import aiosqlite
from decouple import config
from interactions import (
    ApplicationCommandType,
    Channel,
    ClientPresence,
    CommandContext,
    Embed,
    EmbedField,
    HTTPClient,
    Intents,
    PresenceActivity,
    PresenceActivityType,
    StatusType,
)
from interactions.ext.lavalink import VoiceClient
from interactions.ext.tasks import IntervalTrigger, create_task
from interactions.ext.wait_for import setup

from utils import logger

# create the bot instance
logger.info("Initializing discord client.")
client = VoiceClient(
    token=config("dev"),  # change this to "token" if deploying on production server
    intents=Intents.ALL,
)
setup(client)

# initialize database
logger.info("Initializing motor client.")
import motor.motor_asyncio

cluster = motor.motor_asyncio.AsyncIOMotorClient(config("mongouri"))
db = cluster.bot

# initialize local storage
logger.info("Initializing local storage.")
import sqlite3

db3 = sqlite3.connect("./storage/storage.db", detect_types=sqlite3.PARSE_DECLTYPES)
db3.cursor().execute(
    "CREATE TABLE IF NOT EXISTS `feedback_blocked` (`user` BIGINT unsigned NOT NULL, `time` TIMESTAMP NOT NULL, PRIMARY KEY (`user`))"
)
db3.cursor().execute(
    "CREATE TABLE IF NOT EXISTS `metric` (`name` VARCHAR NOT NULL, `uses` BIGINT unsigned NOT NULL, PRIMARY KEY (`name`))"
)
db3.cursor().execute(
    "CREATE TABLE IF NOT EXISTS `counting` (`guild` BIGINT unsigned NOT NULL, `channel` BIGINT unsigned NOT NULL, `user` BIGINT unsigned DEFAULT NULL, `count` BIGINT unsigned NOT NULL DEFAULT '0', PRIMARY KEY (`guild`))"
)
db3.commit()
db3.close()

# initialize twitter api client
logger.info("Initializing tweepy client.")
import tweepy.asynchronous.client

tw = tweepy.asynchronous.client.AsyncClient(
    config("twitterbearer"),
    config("twitter"),
    config("twittersecret"),
    config("twitteraccess"),
    config("twitteraccesssecret"),
)

# load interactions extensions
logger.info("Loading interactions extensions.")
client.load("interactions.ext.files")
# client.load("interactions.ext.help")
client.load("interactions.ext.persistence", cipher_key=config("cipher"))

# load cogs
logger.info("Loading client extensions.")
for i in os.listdir("./cogs"):
    if i.endswith(".py"):
        client.load(f"cogs.{i[:-3]}", logger=logger, version=version, db=db, tw=tw, cluster=cluster)
for i in os.listdir("./wipcogs"):
    if i.endswith(".py"):
        client.load(
            f"wipcogs.{i[:-3]}", logger=logger, version=version, db=db, tw=tw, cluster=cluster
        )


current = 0


@create_task(IntervalTrigger(15))
async def _loop_presence():
    global current
    match current:
        case 0:
            name = "beta-bot.itsrqtl.me"
        case _:
            name = "/help"
            current = -1
    await client.change_presence(
        presence=ClientPresence(
            activities=[PresenceActivity(type=PresenceActivityType.GAME, name=name)],
            status=StatusType.ONLINE,
        )
    )
    current += 1


@client.event
async def on_start():
    if isinstance(client._http, str):
        logger.debug("Patching HTTPClient.")
        client._http = HTTPClient(client._http)

    logger.info("Client has started.")
    bot = await client._http.get_self()
    logger.info(f"Logged in as {bot['username']}#{bot['discriminator']} ({bot['id']})")

    await client.change_presence(
        presence=ClientPresence(
            activities=[PresenceActivity(type=PresenceActivityType.GAME, name="準備中...")],
            status=StatusType.ONLINE,
        )
    )

    _loop_presence.start()


@client.event
async def on_command(ctx: CommandContext):
    await asyncio.sleep(0.1)
    if ctx.command.type != ApplicationCommandType.CHAT_INPUT:
        return
    async with aiosqlite.connect("./storage/storage.db") as db3:
        await db3.execute(f'INSERT OR IGNORE INTO metric VALUES ("{ctx.command.name}", 0)')
        async with db3.execute(f'SELECT * FROM metric WHERE name="{ctx.command.name}"') as cursor:
            data = [i async for i in cursor]
        await db3.execute(f'UPDATE metric SET uses={data[0][1]+1} WHERE name="{ctx.command.name}"')
        await db3.commit()


def markdown(content):
    for ch in ["*", "_", "~", "`"]:
        content = content.replace(ch, "\\" + ch)
    return content


@client.event
async def on_command_error(ctx: CommandContext, error: Exception):
    try:
        raise error
    except Exception:
        tb = f"Traceback: \n```{markdown(traceback.format_exc())}```"
    if len(tb) > 4096:
        tb = f"{tb[:4090]}...```"
    msg = error.args[0] or "Unknown error."
    if isinstance(msg, str):
        msg = msg.replace("\n  ", "\n")
    await Channel(
        **await client._http.create_dm(recipient_id=int(client.me.owner.id)), _client=client._http
    ).send(
        embeds=Embed(
            title="出錯了啦！都怪你亂來程式隨便寫...",
            description=tb,
            fields=[
                EmbedField(name="錯誤訊息", value=f"```{msg}```"),
            ],
            color=randint(0, 0xFFFFFF),
        )
    )


# shard the bot if needed
# from interactions.ext.autosharder import shard
# shard(client)

# run the bot
client.start()
