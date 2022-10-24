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
import sys
import tracemalloc
from random import randint

import interactions
from interactions import (
    Channel,
    ChannelType,
    Client,
    CommandContext,
    Embed,
    EmbedAuthor,
    EmbedField,
    EmbedImageStruct,
    Extension,
    User,
    extension_command,
    option,
)
from loguru._logger import Logger

from utils import raweb

newline = "\n"


class general(Extension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.logger: Logger = kwargs.get("logger")
        self.versions = {
            "BETA BOT": kwargs.get("version"),
            "Python": ".".join(
                [
                    str(sys.version_info.major),
                    str(sys.version_info.minor),
                    str(sys.version_info.micro),
                ]
            ),
            "interactions.py": interactions.__version__,
        }
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

    @extension_command()
    async def info(self, *args, **kwargs):
        """資訊指令"""
        ...

    @info.subcommand()
    @option(description="要查詢的頻道", channel_types=[ChannelType.GUILD_TEXT])
    async def channel(self, ctx: CommandContext, channel: Channel = None):
        """查詢頻道資訊"""
        if not channel:
            channel = await ctx.get_channel()
        if channel.type == ChannelType.DM:
            return await ctx.send(":x: baka 我不能查詢DM頻道！", ephemeral=True)
        await ctx.send(
            embeds=Embed(
                description=channel.mention,
                fields=[
                    EmbedField(name=":hash: 名稱", value=channel.name, inline=True),
                    EmbedField(
                        name=":speech_balloon: 類型",
                        value=channel.type.name.replace("_", " "),
                        inline=True,
                    ),
                    EmbedField(name=":id: ID", value=str(channel.id), inline=True),
                    EmbedField(name=":round_pushpin: 位置", value=str(channel.position), inline=True),
                    EmbedField(
                        name=":underage: NSFW", value="是" if channel.nsfw else "否", inline=True
                    ),
                    EmbedField(
                        name=":calendar_spiral: 創建時間",
                        value=f"<t:{round(channel.id.timestamp.timestamp())}:R>",
                        inline=True,
                    ),
                ],
                color=randint(0, 0xFFFFFF),
            )
        )

    @info.group()
    async def user(self, *args, **kwargs):
        ...

    @user.subcommand(name="detail")
    @option(description="要查詢的用戶")
    async def user_info(self, ctx: CommandContext, user: User = None):
        """查詢用戶資訊"""
        if not user:
            user = ctx.user
        await ctx.send(
            embeds=Embed(
                fields=[
                    EmbedField(name=":id: ID", value=str(user.id), inline=True),
                    EmbedField(
                        name=":calendar_spiral: 創建時間",
                        value=f"<t:{round(user.id.timestamp.timestamp())}:R>",
                        inline=True,
                    ),
                    EmbedField(name=":robot: 機器人", value="是" if user.bot else "否", inline=True),
                ],
                author=EmbedAuthor(
                    name=f"{user.username}#{user.discriminator}", icon_url=user.avatar_url
                ),
                color=randint(0, 0xFFFFFF),
            )
        )

    @user.subcommand(name="avatar")
    @option(description="要查詢的用戶")
    async def user_avatar(self, ctx: CommandContext, user: User = None):
        """取得用戶的頭像"""
        if not user:
            user = ctx.user
        await ctx.defer()
        if user.avatar:
            return await ctx.send(embeds=raweb(image=EmbedImageStruct(url=user.avatar_url)))
        else:
            return await ctx.send(embeds=raweb(desc=":x: baka 這個用戶沒有頭像啦！"))

    @info.subcommand(name="banner")
    @option(description="要查詢的用戶")
    async def user_banner(self, ctx: CommandContext, user: User = None):
        """取得用戶的橫幅"""
        if not user:
            user = ctx.user
        await ctx.defer()
        if user.banner:
            return await ctx.send(embeds=raweb(image=EmbedImageStruct(url=user.banner_url)))
        else:
            return await ctx.send(embeds=raweb(desc=":x: baka 這個用戶沒有橫幅啦！"))

    @info.group()
    async def server(self, *args, **kwargs):
        ...

    @server.subcommand(name="detail")
    async def server_info(self, ctx: CommandContext):
        """查詢伺服器資訊"""
        await ctx.get_channel()
        if ctx.channel.type == ChannelType.DM:
            return await ctx.send(":x: baka 沒有伺服器要我怎樣查詢！", ephemeral=True)
        await ctx.defer()
        owner = await ctx.guild.get_member(ctx.guild.owner_id)
        text = 0
        voice = 0
        category = 0
        for i in ctx.guild.channels:
            if i.type == ChannelType.GUILD_CATEGORY:
                category += 1
            elif i.type in [ChannelType.GUILD_VOICE, ChannelType.GUILD_STAGE_VOICE]:
                voice += 1
            else:
                text += 1
        await ctx.send(
            embeds=Embed(
                fields=[
                    EmbedField(name=":id: ID", value=str(ctx.guild.id), inline=True),
                    EmbedField(
                        name=":calendar_spiral: 創建時間",
                        value=f"<t:{round(ctx.guild.id.timestamp.timestamp())}:R>",
                        inline=True,
                    ),
                    EmbedField(name=":star: 擁有者", value=owner.mention, inline=True),
                    EmbedField(
                        name=":speech_balloon: 頻道數",
                        value=f"文字頻道: {text}\n語音頻道: {voice}\n分類: {category}",
                        inline=True,
                    ),
                    EmbedField(
                        name=":busts_in_silhouette: 成員",
                        value=f"成員數: {ctx.guild.member_count}\n身份組: {len(ctx.guild.roles)}",
                        inline=True,
                    ),
                    EmbedField(
                        name=":arrow_up: 加成",
                        value=f"數量: {ctx.guild.premium_subscription_count if ctx.guild.premium_subscription_count else 0}\n等級: {ctx.guild.premium_tier if ctx.guild.premium_tier else 0}",
                        inline=True,
                    ),
                    EmbedField(
                        name=":laughing: 表情符號",
                        value=f"{len(ctx.guild.emojis)}/{'50'if not ctx.guild.premium_tier or ctx.guild.premium_tier == 0 else '100' if ctx.guild.premium_tier == 1 else '150' if ctx.guild.premium_tier == 2 else '250'}",
                        inline=True,
                    ),
                ],
                author=EmbedAuthor(name=ctx.guild.name, icon_url=ctx.guild.icon_url),
                color=randint(0, 0xFFFFFF),
            )
        )

    @server.subcommand(name="icon")
    async def server_icon(self, ctx: CommandContext):
        """取得伺服器圖示"""
        await ctx.get_channel()
        if ctx.channel.type == ChannelType.DM:
            return await ctx.send(":x: baka 沒有伺服器要我怎樣查詢！", ephemeral=True)
        await ctx.defer()
        if ctx.guild.icon_url:
            return await ctx.send(embeds=raweb(image=EmbedImageStruct(url=ctx.guild.icon_url)))
        else:
            return await ctx.send(embeds=raweb(desc=":x: baka 這個伺服器沒有圖示啦！"))

    @server.subcommand(name="banner")
    async def server_banner(self, ctx: CommandContext):
        """取得伺服器橫幅"""
        await ctx.get_channel()
        if ctx.channel.type == ChannelType.DM:
            return await ctx.send(":x: baka 沒有伺服器要我怎樣查詢！", ephemeral=True)
        await ctx.defer()
        if ctx.guild.banner_url:
            return await ctx.send(embeds=raweb(image=EmbedImageStruct(url=ctx.guild.banner_url)))
        else:
            return await ctx.send(embeds=raweb(desc=":x: baka 這個伺服器沒有橫幅啦！"))

    @info.group(name="bot")
    async def _bot(self, *args, **kwargs):
        ...

    @_bot.subcommand(name="detail")
    async def bot_info(self, ctx: CommandContext):
        """查詢機器人資訊"""
        ...  # TODO: 這裡還沒寫完

    @_bot.subcommand(name="status")
    async def bot_status(self, ctx: CommandContext):
        """查看我的狀態"""
        await ctx.defer()
        channels = 0
        users = 0
        for i in self.client.guilds:
            channels += len(i.channels)
            users += i.member_count
        ver = "\n".join([f"{k}: **{v}**" for k, v in self.versions.items()])
        embed = Embed(
            title="狀態",
            description="你那麼想知道我的狀態... 嗎？",
            fields=[
                EmbedField(name="📒 版本", value=ver, inline=False),
                EmbedField(
                    name="📊 數據",
                    value=f"伺服器: **{len(self.client.guilds)}**\n頻道: **{channels}**",
                    inline=False,
                ),
                EmbedField(
                    name="📈 狀態",
                    value=f"RAM 使用量: **{round(tracemalloc.get_traced_memory()[0]/1000000, 2)}**mb\n延遲: 大概 **{abs(round(self.client.latency, 2))}**ms 吧？但是我會一直陪著你喔！",
                    inline=False,
                ),
            ],
            color=randint(0, 0xFFFFFF),
        )
        await ctx.send(embeds=embed)


def setup(client, **kwargs):
    general(client, **kwargs)
