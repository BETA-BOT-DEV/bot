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
newline = "\n"


def markdown(content):
    for ch in ["*", "_", "~", "`"]:
        content = content.replace(ch, "\\" + ch)
    return content


def get_post_id(content):
    matchs = TWITTER_URL_REGEX.search(content)
    if matchs:
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
            for emoji in ["🔁", "❤️"]:
                try:
                    await msg.create_reaction(emoji)
                finally:
                    await asyncio.sleep(0.3)

    @extension_listener(name="on_message_reaction_add")
    async def _reaction_add(self, reaction: MessageReaction):
        if reaction.emoji.name not in ["🔁", "❤️"] or reaction.user_id == self.client.me.id:
            return
        msg: Message = await get(
            self.client, Message, object_id=reaction.message_id, parent_id=reaction.channel_id
        )
        if msg.content:
            id = get_post_id(msg.content)
            if id:
                document = await self.db.connected.find_one(filter={"_id": int(reaction.user_id)})
                if not document:
                    return await msg.remove_reaction_from(reaction.emoji, reaction.user_id)
                token = document["token"]
                async with aiohttp.ClientSession() as session:
                    if (
                        document["ttl"] + datetime.timedelta(hours=1, minutes=30)
                        < datetime.datetime.utcnow()
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
                                        "ttl": datetime.datetime.utcnow(),
                                    }
                                },
                            )
                            token = resp["access_token"]
                    if reaction.emoji.name == "❤️":
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
                    elif reaction.emoji.name == "🔁":
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
        if reaction.emoji.name not in ["🔁", "❤️"]:
            return
        msg: Message = await get(
            self.client, Message, object_id=reaction.message_id, parent_id=reaction.channel_id
        )
        if msg.content:
            id = get_post_id(msg.content)
            if id:
                document = await self.db.connected.find_one(filter={"_id": int(reaction.user_id)})
                if not document:
                    return
                token = document["token"]
                async with aiohttp.ClientSession() as session:
                    if (
                        document["ttl"] + datetime.timedelta(hours=1, minutes=30)
                        < datetime.datetime.utcnow()
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
                                        "ttl": datetime.datetime.utcnow(),
                                    }
                                },
                            )
                            token = resp["access_token"]
                    if reaction.emoji.name == "❤️":
                        async with session.delete(
                            f"https://api.twitter.com/2/users/{document['tid']}/likes/{id}",
                            headers={"Authorization": f"Bearer {token}"},
                        ) as r:
                            resp = await r.json()
                    elif reaction.emoji.name == "🔁":
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
        """連結Twitter"""
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
                f"請點擊[此連結](<https://service.itsrqtl.repl.co/link?code={code}>)進行連結\n輸入密碼時，請確保網域為twitter.com喔！",
                ephemeral=True,
            )
        elif not twitter and pending:
            await ctx.send(
                f"請點擊[此連結](<https://service.itsrqtl.repl.co/link?code={pending['code']}>)進行連結\n輸入密碼時，請確保網域為twitter.com喔！",
                ephemeral=True,
            )
        elif twitter:
            resp = (
                await self.tw.get_user(id=twitter["tid"], user_fields=["username"])
            ).data.username
            await ctx.send(
                f":x: baka 你已連結到 [@{resp}](<https://twitter.com/{resp}>) 啦！\n請先用 </twitter unlink:{self.client._find_command('twitter').id}> 解除連結喔！",
                ephemeral=True,
            )

    @twitter.subcommand()
    async def unlink(self, ctx: CommandContext):
        """解除Twitter連結"""
        await ctx.defer(ephemeral=True)
        twitter = await self.db.connected.find_one(filter={"_id": int(ctx.author.id)})
        if not twitter:
            await ctx.send(
                f":x: baka 你沒有連結Twitter啦！\n請先用 </twitter link:{self.client._find_command('twitter').id}> 連結Twitter喔！",
                ephemeral=True,
            )
        else:
            resp = (
                await self.tw.get_user(id=twitter["tid"], user_fields=["username"])
            ).data.username
            await self.db.connected.delete_one(filter={"_id": int(ctx.author.id)})
            await ctx.send(
                f"成功解除與Twitter [@{resp}](<https://twitter.com/{resp}>) 的連結了！",
                ephemeral=True,
            )
            self.logger.info(
                f"User {ctx.author.user.username}#{ctx.author.user.discriminator} ({ctx.author.id}) unlinked their twitter: @{resp} ({twitter['tid']})"
            )

    @twitter.subcommand()
    @option(description="使用者名稱")
    async def user(self, ctx: CommandContext, username: str):
        """尋找Twitter使用者資料"""
        if not re.compile(r"^@?(\w){1,15}$").match(username):
            return await ctx.send(":x: baka Twitter使用者名稱格式錯誤啦！", ephemeral=True)
        else:
            if username.startswith("@"):
                username = username[1:]
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
            return await ctx.send(":x: baka 找不到Twitter使用者啦！", ephemeral=True)
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
                        name="跟隨者",
                        value=f"{lookup.data.public_metrics['followers_count']}",
                        inline=True,
                    ),
                    EmbedField(
                        name="跟隨中",
                        value=f"{lookup.data.public_metrics['following_count']}",
                        inline=True,
                    ),
                    EmbedField(
                        name="推文",
                        value=f"{lookup.data.public_metrics['tweet_count']}",
                        inline=True,
                    ),
                    EmbedField(
                        name="創建時間",
                        value=f"<t:{round(lookup.data.created_at.timestamp())}:R>",
                        inline=True,
                    ),
                    EmbedField(
                        name="保護推文",
                        value="是" if lookup.data.protected else "否",
                        inline=True,
                    ),
                    EmbedField(
                        name="已驗證",
                        value="是" if lookup.data.verified else "否",
                        inline=True,
                    ),
                ],
            ),
            components=[
                ActionRow(
                    components=[
                        Button(
                            style=ButtonStyle.PRIMARY,
                            label="跟隨使用者",
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
            return await ctx.send(":x: baka 你不是這個查詢的主人啦！", ephemeral=True)
        document = await self.db.connected.find_one(filter={"_id": int(ctx.author.id)})
        if not document:
            await ctx.message.disable_all_components()
            return await ctx.send(
                f":x: baka 你沒有連結Twitter啦！\n請先用 </twitter link:{self.client._find_command('twitter').id}> 連結Twitter喔！"
            )
        if document["tid"] == package:
            await ctx.message.disable_all_components()
            return await ctx.send(":x: baka 你不能跟隨自己啦！")
        token = document["token"]
        async with aiohttp.ClientSession() as session:
            if (
                document["ttl"] + datetime.timedelta(hours=1, minutes=30)
                < datetime.datetime.utcnow()
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
                        f":x: 無法驗證使用者，請使用 </twitter link:{self.client._find_command('twitter').id}> 重新連結Twitter喔！"
                    )
                else:
                    await self.db.connected.update_one(
                        filter={"_id": int(ctx.author.id)},
                        update={
                            "$set": {
                                "token": resp["access_token"],
                                "refresh": resp["refresh_token"],
                                "ttl": datetime.datetime.utcnow(),
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
                return await ctx.send("跟隨使用者了！")
            elif not resp["data"]["following"] and resp["data"]["pending_follow"]:
                await ctx.message.disable_all_components()
                return await ctx.send("發出跟隨請求了！")
            else:
                await ctx.message.disable_all_components()
                return await ctx.send(
                    f"發生錯誤了！請稍後再試，或是使用 </feedback:{self.client._find_command('feedback').id}> 回報喔！"
                )

    @twitter.subcommand()
    @option(description="搜尋內容", max_length=128)
    @option(description="搜尋使用者", max_length=16)
    @option(description="搜尋#hashtag", max_length=128)
    @option(description="顯示推文的數量 (預設: 5)", max_value=10, min_value=1)
    @option(description="是否包含回覆內容 (預設: 否)")
    async def search(
        self,
        ctx: CommandContext,
        query: str = "",
        user: str = "",
        hashtag: str = "",
        limit: int = 5,
        reply: bool = False,
    ):
        """搜尋最近的推文"""
        if not user and not query and not hashtag:
            return await ctx.send(":x: baka 你沒有指定搜尋內容啦！", ephemeral=True)
        if user:
            if not re.compile(r"^@?(\w){1,15}$").match(user):
                return await ctx.send(":x: baka Twitter使用者名稱格式錯誤啦！", ephemeral=True)
            else:
                if user.startswith("@"):
                    user = user[1:]
        if hashtag:
            hashtag = [i[1:] if i.startswith("#") else i for i in hashtag.split(" ")]
        tweets = await self.tw.search_recent_tweets(
            query=f"""{f"{query} " if query else ''}{f'from:{user} ' if user else ''}{f"#{' #'.join(hashtag)} " if hashtag else ''}{"-is:reply " if not reply else ''}-is:retweet""",
            tweet_fields=["author_id", "created_at", "text"],
            user_fields=["name", "username"],
            expansions=["author_id"],
            sort_order="recency",
        )
        if not tweets.data:
            return await ctx.send(":x: 我找不到相關的推文！", ephemeral=True)
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
                    value=f"[**[推文連結🔗]**]({turl})\n> {markdown(content).replace(newline, f'{newline}> ')}",
                )
            )
        await ctx.send(
            embeds=Embed(
                title=f"找到了 **{min(limit, len(ef))}** 個推文！",
                fields=ef[:limit] if len(ef) > limit else ef,
                color=0x1DA1F2,
            )
        )


def setup(client, **kwargs):
    twitter(client, **kwargs)
