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

import asyncio
import datetime
import os
import re
from base64 import b64encode
from random import randint

import aiohttp
import tweepy.asynchronous.client
from decouple import config
from interactions import (
    ActionRow,
    Button,
    ButtonStyle,
    Client,
    CommandContext,
    ComponentContext,
    Embed,
    EmbedField,
    EmbedImageStruct,
    Message,
    MessageReaction,
    extension_command,
    extension_listener,
    get,
    option,
)
from interactions.ext.persistence import (
    PersistenceExtension,
    PersistentCustomID,
    extension_persistent_component,
)
from loguru._logger import Logger

TWITTER_URL_REGEX = re.compile(
    r"https:\/\/(www\.)?(twitter|fxtwitter)\.com\/[A-Za-z0-9_][^ =&/:]{1,15}\/status\/[0-9]{19}"
)
TWITTER_USER_REGEX = re.compile(r"^@?[a-zA-Z0-9_]{1,15}$")
newline = "\n"


def markdown(content):
    for ch in ["*", "_", "~", "`"]:
        content = content.replace(ch, "\\" + ch)
    return content


def get_post_id(content):
    if matchs := TWITTER_URL_REGEX.search(content):
        return matchs.group().split("/")[-1]
    return None


class twitter(PersistenceExtension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.logger: Logger = kwargs.get("logger")
        self.cluster = kwargs.get("cluster")
        self.db = self.cluster.twitter
        self.tw: tweepy.asynchronous.client.AsyncClient = kwargs.get("tw")
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

    @extension_listener(name="on_message_create")
    async def _twitter_reactions(self, msg: Message):
        if msg.content and TWITTER_URL_REGEX.search(msg.content):
            for emoji in ["????", "??????"]:
                try:
                    await msg.create_reaction(emoji)
                finally:
                    await asyncio.sleep(0.3)

    @extension_listener(name="on_message_reaction_add")
    async def _reaction_add(self, reaction: MessageReaction):
        if reaction.emoji.name not in ["????", "??????"] or reaction.user_id == self.client.me.id:
            return
        msg: Message = await get(
            self.client, Message, object_id=reaction.message_id, parent_id=reaction.channel_id
        )
        if msg.content:
            if id := get_post_id(msg.content):
                document = await self.db.connected.find_one(filter={"_id": int(reaction.user_id)})
                if not document:
                    return await msg.remove_reaction_from(reaction.emoji, reaction.user_id)
                token = document["token"]
                async with aiohttp.ClientSession() as session:
                    if document["ttl"] + datetime.timedelta(
                        hours=1, minutes=30
                    ) < datetime.datetime.now(datetime.timezone.utc):
                        async with session.post(
                            "https://api.twitter.com/2/oauth2/token",
                            headers={
                                "Authorization": f"""Basic {b64encode(f"{config('twid')}:{config('twsecret')}".encode()).decode()}""",
                                "Content-Type": "application/x-www-form-urlencoded",
                            },
                            data=f"refresh_token={document['refresh']}&grant_type=refresh_token&client_id={config('twid')}",
                        ) as r:
                            resp = await r.json()
                        if "access_token" not in resp or "refresh_token" not in resp:
                            await self.db.connected.delete_one(
                                filter={"_id": int(reaction.user_id)}
                            )
                        else:
                            await self.db.connected.update_one(
                                filter={"_id": int(reaction.user_id)},
                                update={
                                    "$set": {
                                        "token": resp["access_token"],
                                        "refresh": resp["refresh_token"],
                                        "ttl": datetime.datetime.now(datetime.timezone.utc),
                                    }
                                },
                            )
                            token = resp["access_token"]
                    if reaction.emoji.name == "??????":
                        async with session.post(
                            f"https://api.twitter.com/2/users/{document['tid']}/likes",
                            headers={"Authorization": f"Bearer {token}"},
                            json={"tweet_id": str(id)},
                        ) as r:
                            resp = await r.json()
                        if resp["data"]["liked"]:
                            return
                        else:
                            return await msg.remove_reaction_from(reaction.emoji, reaction.user_id)
                    elif reaction.emoji.name == "????":
                        async with session.post(
                            f"https://api.twitter.com/2/users/{document['tid']}/retweets",
                            headers={"Authorization": f"Bearer {token}"},
                            json={"tweet_id": str(id)},
                        ) as r:
                            resp = await r.json()
                        if resp["data"]["retweeted"]:
                            return
                        else:
                            return await msg.remove_reaction_from(reaction.emoji, reaction.user_id)

    @extension_listener(name="on_message_reaction_remove")
    async def _reaction_remove(self, reaction: MessageReaction):
        if reaction.emoji.name not in ["????", "??????"]:
            return
        msg: Message = await get(
            self.client, Message, object_id=reaction.message_id, parent_id=reaction.channel_id
        )
        if msg.content:
            if id := get_post_id(msg.content):
                document = await self.db.connected.find_one(filter={"_id": int(reaction.user_id)})
                if not document:
                    return
                token = document["token"]
                async with aiohttp.ClientSession() as session:
                    if document["ttl"] + datetime.timedelta(
                        hours=1, minutes=30
                    ) < datetime.datetime.now(datetime.timezone.utc):
                        async with session.post(
                            "https://api.twitter.com/2/oauth2/token",
                            headers={
                                "Authorization": f"""Basic {b64encode(f"{config('twid')}:{config('twsecret')}".encode()).decode()}""",
                                "Content-Type": "application/x-www-form-urlencoded",
                            },
                            data=f"refresh_token={document['refresh']}&grant_type=refresh_token&client_id={config('twid')}",
                        ) as r:
                            resp = await r.json()
                        if "access_token" not in resp or "refresh_token" not in resp:
                            await self.db.connected.delete_one(
                                filter={"_id": int(reaction.user_id)}
                            )
                        else:
                            await self.db.connected.update_one(
                                filter={"_id": int(reaction.user_id)},
                                update={
                                    "$set": {
                                        "token": resp["access_token"],
                                        "refresh": resp["refresh_token"],
                                        "ttl": datetime.datetime.now(datetime.timezone.utc),
                                    }
                                },
                            )
                            token = resp["access_token"]
                    if reaction.emoji.name == "??????":
                        async with session.delete(
                            f"https://api.twitter.com/2/users/{document['tid']}/likes/{id}",
                            headers={"Authorization": f"Bearer {token}"},
                        ) as r:
                            resp = await r.json()
                    elif reaction.emoji.name == "????":
                        async with session.delete(
                            f"https://api.twitter.com/2/users/{document['tid']}/retweets/{id}",
                            headers={"Authorization": f"Bearer {token}"},
                        ) as r:
                            resp = await r.json()

    @extension_command()
    async def twitter(self, *args, **kwargs):
        ...

    @twitter.subcommand()
    async def link(self, ctx: CommandContext):
        """??????Twitter"""
        await ctx.defer(ephemeral=True)
        twitter = await self.db.connected.find_one(filter={"_id": int(ctx.author.id)})
        pending = await self.db.pending.find_one(filter={"_id": int(ctx.author.id)})
        if not twitter and not pending:
            code = None
            codes = [i["code"] async for i in self.db.pending.find()]
            while not code or code in codes:
                code = "%08d" % randint(0, 99999999)
            await self.db.pending.insert_one({"_id": int(ctx.author.id), "code": str(code)})
            await ctx.send(
                f"?????????[?????????](<https://service.itsrqtl.repl.co/link?code={code}>)????????????\n????????????????????????????????????twitter.com??????",
                ephemeral=True,
            )
        elif not twitter:
            await ctx.send(
                f"?????????[?????????](<https://service.itsrqtl.repl.co/link?code={pending['code']}>)????????????\n????????????????????????????????????twitter.com??????",
                ephemeral=True,
            )
        else:
            resp = (
                await self.tw.get_user(id=twitter["tid"], user_fields=["username"])
            ).data.username
            await ctx.send(
                f":x: baka ??????????????? [@{resp}](<https://twitter.com/{resp}>) ??????\n????????? </twitter unlink:{self.client._find_command('twitter').id}> ??????????????????",
                ephemeral=True,
            )

    @twitter.subcommand()
    async def unlink(self, ctx: CommandContext):
        """??????Twitter??????"""
        await ctx.defer(ephemeral=True)
        twitter = await self.db.connected.find_one(filter={"_id": int(ctx.author.id)})
        if not twitter:
            await ctx.send(
                f":x: baka ???????????????Twitter??????\n????????? </twitter link:{self.client._find_command('twitter').id}> ??????Twitter??????",
                ephemeral=True,
            )
        else:
            resp = (
                await self.tw.get_user(id=twitter["tid"], user_fields=["username"])
            ).data.username
            await self.db.connected.delete_one(filter={"_id": int(ctx.author.id)})
            await ctx.send(
                f"???????????????Twitter [@{resp}](<https://twitter.com/{resp}>) ???????????????",
                ephemeral=True,
            )
            self.logger.info(
                f"User {ctx.author.user.username}#{ctx.author.user.discriminator} ({ctx.author.id}) unlinked their twitter: @{resp} ({twitter['tid']})"
            )

    @twitter.subcommand()
    @option(description="???????????????")
    async def user(self, ctx: CommandContext, username: str):
        """??????Twitter???????????????"""
        if not TWITTER_USER_REGEX.match(username):
            return await ctx.send(":x: baka Twitter?????????????????????????????????", ephemeral=True)
        username = username.removeprefix("@")
        lookup = await self.tw.get_user(
            username=username,
            user_fields=[
                "created_at",
                "description",
                "id",
                "profile_image_url",
                "protected",
                "public_metrics",
                "verified",
                "name",
                "username",
            ],
        )
        if not lookup.data:
            return await ctx.send(":x: baka ?????????Twitter???????????????", ephemeral=True)
        await ctx.defer()
        await ctx.send(
            embeds=Embed(
                title=f"{lookup.data.name} (@{lookup.data.username})",
                description=lookup.data.description,
                url=f"https://twitter.com/{lookup.data.username}",
                thumbnail=EmbedImageStruct(url=lookup.data.profile_image_url)
                if lookup.data.profile_image_url
                != "https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png"
                else None,
                color=0x1DA1F2,
                fields=[
                    EmbedField(
                        name="?????????",
                        value=f"{lookup.data.public_metrics['followers_count']}",
                        inline=True,
                    ),
                    EmbedField(
                        name="?????????",
                        value=f"{lookup.data.public_metrics['following_count']}",
                        inline=True,
                    ),
                    EmbedField(
                        name="??????",
                        value=f"{lookup.data.public_metrics['tweet_count']}",
                        inline=True,
                    ),
                    EmbedField(
                        name="????????????",
                        value=f"<t:{round(lookup.data.created_at.replace(tzinfo=datetime.timezone.utc).timestamp())}:R>",
                        inline=True,
                    ),
                    EmbedField(
                        name="????????????",
                        value="???" if lookup.data.protected else "???",
                        inline=True,
                    ),
                    EmbedField(
                        name="?????????",
                        value="???" if lookup.data.verified else "???",
                        inline=True,
                    ),
                ],
            ),
            components=[
                ActionRow(
                    components=[
                        Button(
                            style=ButtonStyle.PRIMARY,
                            label="???????????????",
                            custom_id=str(
                                PersistentCustomID(self.client, "twitter_follow", lookup.data.id)
                            ),
                        ),
                    ]
                )
            ],
        )

    @extension_persistent_component("twitter_follow")
    async def _twitter_follow(self, ctx: ComponentContext, package):
        await ctx.defer(ephemeral=True)
        if ctx.author.id != ctx.message.interaction.user.id:
            return await ctx.send(":x: baka ????????????????????????????????????", ephemeral=True)
        document = await self.db.connected.find_one(filter={"_id": int(ctx.author.id)})
        if not document:
            await ctx.message.disable_all_components()
            return await ctx.send(
                f":x: baka ???????????????Twitter??????\n????????? </twitter link:{self.client._find_command('twitter').id}> ??????Twitter??????"
            )
        if document["tid"] == package:
            await ctx.message.disable_all_components()
            return await ctx.send(":x: baka ???????????????????????????")
        token = document["token"]
        async with aiohttp.ClientSession() as session:
            if document["ttl"] + datetime.timedelta(hours=1, minutes=30) < datetime.datetime.now(
                datetime.timezone.utc
            ):
                async with session.post(
                    "https://api.twitter.com/2/oauth2/token",
                    headers={
                        "Authorization": f"""Basic {b64encode(f"{config('twid')}:{config('twsecret')}".encode()).decode()}""",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    data=f"refresh_token={document['refresh']}&grant_type=refresh_token&client_id={config('twid')}",
                ) as r:
                    resp = await r.json()
                if "access_token" not in resp or "refresh_token" not in resp:
                    await self.db.connected.delete_one(filter={"_id": int(ctx.author.id)})
                    return ctx.send(
                        f":x: ????????????????????????????????? </twitter link:{self.client._find_command('twitter').id}> ????????????Twitter??????"
                    )
                else:
                    await self.db.connected.update_one(
                        filter={"_id": int(ctx.author.id)},
                        update={
                            "$set": {
                                "token": resp["access_token"],
                                "refresh": resp["refresh_token"],
                                "ttl": datetime.datetime.now(datetime.timezone.utc),
                            }
                        },
                    )
                    token = resp["access_token"]
            async with session.post(
                f"https://api.twitter.com/2/users/{document['tid']}/following",
                headers={"Authorization": f"Bearer {token}"},
                json={"target_user_id": str(package)},
            ) as r:
                resp = await r.json()
            if resp["data"]["following"]:
                await ctx.message.disable_all_components()
                return await ctx.send("?????????????????????")
            elif resp["data"]["pending_follow"]:
                await ctx.message.disable_all_components()
                return await ctx.send("????????????????????????")
            else:
                await ctx.message.disable_all_components()
                return await ctx.send(
                    f"???????????????????????????????????????????????? </feedback:{self.client._find_command('feedback').id}> ????????????"
                )

    @twitter.subcommand()
    @option(description="????????????", max_length=128)
    @option(description="???????????????", max_length=16)
    @option(description="??????#hashtag", max_length=128)
    @option(description="????????????????????? (??????: 5)", max_value=10, min_value=1)
    @option(description="???????????????????????? (??????: ???)")
    async def search(
        self,
        ctx: CommandContext,
        query: str = "",
        user: str = "",
        hashtag: str = "",
        limit: int = 5,
        reply: bool = False,
    ):
        """?????????????????????"""
        if not user and not query and not hashtag:
            return await ctx.send(":x: baka ?????????????????????????????????", ephemeral=True)
        if user:
            if not TWITTER_USER_REGEX.match(user):
                return await ctx.send(":x: baka Twitter?????????????????????????????????", ephemeral=True)
            else:
                user = user.removeprefix("@")
        if hashtag:
            hashtag = [i[1:] if i.startswith("#") else i for i in hashtag.split(" ")]
        tweets = await self.tw.search_recent_tweets(
            query=f"""{f"{query} " if query else ''}{f'from:{user} ' if user else ''}{f"#{' #'.join(hashtag)} " if hashtag else ''}{"" if reply else '-is:reply '}-is:retweet""",
            tweet_fields=["author_id", "created_at", "text"],
            user_fields=["name", "username"],
            expansions=["author_id"],
            sort_order="recency",
        )
        if not tweets.data:
            return await ctx.send(":x: ??????????????????????????????", ephemeral=True)
        await ctx.defer()
        users = {u["id"]: u for u in tweets.includes["users"]}
        ef = []
        for tweet in tweets.data:
            turl = f"https://twitter.com/{tweet.author_id}/status/{tweet.data['id']}"
            author = users[tweet.author_id]
            content = tweet.data["text"]
            ef.append(
                EmbedField(
                    name=f"{author['name']} (@{author['username']})",
                    value=f"[**[????????????????]**]({turl})\n> {markdown(content).replace(newline, f'{newline}> ')}",
                )
            )
        await ctx.send(
            embeds=Embed(
                title=f"????????? **{min(limit, len(ef))}** ????????????",
                fields=ef[:limit] if len(ef) > limit else ef,
                color=0x1DA1F2,
            )
        )


def setup(client, **kwargs):
    twitter(client, **kwargs)
