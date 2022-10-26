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
    Choice,
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
    @option(description="用戶名稱")
    async def user(self, ctx: CommandContext, username: str):
        """尋找Twitter用戶資料"""
        if not re.compile(r"^@?(\w){1,15}$").match(username):
            return await ctx.send(":x: baka Twitter用戶名稱格式錯誤啦！", ephemeral=True)
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
            return await ctx.send(":x: baka 找不到Twitter用戶啦！", ephemeral=True)
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
    @option(description="搜尋內容", max_length=512)
    @option(description="顯示推文的數量", max_value=10, min_value=1)
    @option(
        description="推文的順序",
        choices=[Choice(name="最新", value="最新"), Choice(name="最相關", value="最相關")],
    )
    async def search(self, ctx: CommandContext, query: str, limit: int = 5, sort: str = "最新"):
        """搜尋推文"""
        await ctx.defer()
        sorting = "relevancy" if sort == "最相關" else "recency"
        tweets = await self.tw.search_recent_tweets(
            query,
            tweet_fields=["author_id", "created_at", "text"],
            user_fields=["name", "username"],
            expansions=["author_id"],
            sort_order=sorting,
        )
        users = {u["id"]: u for u in tweets.includes["users"]}
        ef = []
        for tweet in tweets.data:
            turl = f"https://twitter.com/{tweet.author_id}/status/{tweet.data['id']}"
            author = users[tweet.author_id]
            content = tweet.data["text"]
            ef.append(
                EmbedField(
                    name=f"{author['name']} (@{author['username']})",
                    value=f"[**[推文連結🔗]**]({turl})\n{content}",
                )
            )
        await ctx.send(
            embeds=Embed(
                title="找到了！",
                description=f"**{limit}** 個關於 **{query}** 的 **{sort}** 推文",
                fields=ef[:limit] if len(ef) > limit else ef,
                color=0x1DA1F2,
            )
        )


def setup(client, **kwargs):
    twitter(client, **kwargs)
