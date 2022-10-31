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

import os
import re

import tweepy.asynchronous.client
from interactions import (
    Client,
    CommandContext,
    Embed,
    EmbedField,
    EmbedImageStruct,
    Extension,
    extension_command,
    option,
)
from loguru._logger import Logger

newline = "\n"


def markdown(content):
    for ch in ["*", "_", "~", "`"]:
        content = content.replace(ch, "\\" + ch)
    return content


class twitter(Extension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.logger: Logger = kwargs.get("logger")
        self.tw: tweepy.asynchronous.client.AsyncClient = kwargs.get("tw")
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

    @extension_command()
    async def twitter(self, *args, **kwargs):
        ...

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
                    value=f"[**[推文連結🔗]**]({turl})\n{markdown(content)}",
                )
            )
        await ctx.send(
            embeds=Embed(
                title="找到了！",
                description=f"**{min(limit, len(ef))}** 個推文",
                fields=ef[:limit] if len(ef) > limit else ef,
                color=0x1DA1F2,
            )
        )


def setup(client, **kwargs):
    twitter(client, **kwargs)
