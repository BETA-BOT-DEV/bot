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
from datetime import datetime
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
    extension_user_command,
    get,
    option,
)
from loguru._logger import Logger

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
                title="頻道查詢結果",
                description=f"以下是 {channel.mention} 的相關資訊喔！",
                fields=[
                    EmbedField(name="**頻道名稱**", value=f"`{channel.name}`", inline=True),
                    EmbedField(name="**頻道ID**", value=str(channel.id), inline=True),
                    EmbedField(
                        name="**頻道類型**",
                        value=channel.type.name.replace("_", " "),
                        inline=True,
                    ),
                    EmbedField(name="**頻道位置**", value=str(channel.position), inline=True),
                    EmbedField(name="**NSFW**", value="是" if channel.nsfw else "否", inline=True),
                    EmbedField(
                        name="**創建時間**",
                        value=f"<t:{round(channel.id.timestamp.timestamp())}:F> (<t:{round(channel.id.timestamp.timestamp())}:R>)",
                        inline=True,
                    ),
                ],
                color=randint(0, 0xFFFFFF),
            )
        )

    @info.subcommand()
    @option(description="要查詢的使用者")
    async def user(self, ctx: CommandContext, user: User = None):
        """查詢使用者資訊"""
        if not user:
            user = ctx.user
        user = await get(self.client, User, object_id=user.id)
        await ctx.send(
            embeds=Embed(
                title="使用者查詢結果",
                description=f"以下是 {user.mention} 的相關資訊喔！",
                fields=[
                    EmbedField(
                        name="**使用者名稱**",
                        value=f"`{user.username}#{user.discriminator}`",
                        inline=True,
                    ),
                    EmbedField(name="**使用者ID**", value=str(user.id), inline=True),
                    EmbedField(name="**機器人**", value="是" if user.bot else "否", inline=False),
                    EmbedField(
                        name="**創建時間**",
                        value=f"<t:{round(user.id.timestamp.timestamp())}:F> (<t:{round(user.id.timestamp.timestamp())}:R>)",
                        inline=True,
                    ),
                ],
                author=EmbedAuthor(
                    name=f"{user.username}#{user.discriminator}", icon_url=user.avatar_url
                ),
                thumbnail=EmbedImageStruct(url=user.avatar_url) if user.avatar else None,
                image=EmbedImageStruct(url=f"{user.banner_url}?size=480") if user.banner else None,
                color=randint(0, 0xFFFFFF),
            )
        )

    @info.subcommand()
    async def server(self, ctx: CommandContext):
        """查詢伺服器資訊"""
        await ctx.get_channel()
        if ctx.channel.type == ChannelType.DM:
            return await ctx.send(":x: baka 沒有伺服器要我怎樣查詢！", ephemeral=True)
        await ctx.defer()
        await ctx.get_guild()
        owner = await ctx.guild.get_member(ctx.guild.owner_id)
        text = 0
        voice = 0
        category = 0
        for i in ctx.guild.channels:
            if i.type == ChannelType.GUILD_CATEGORY:
                category += 1
            elif i.type in [ChannelType.GUILD_VOICE, ChannelType.GUILD_STAGE_VOICE]:
                voice += 1
            elif i.type in [
                ChannelType.ANNOUNCEMENT_THREAD,
                ChannelType.PUBLIC_THREAD,
                ChannelType.PRIVATE_THREAD,
            ]:
                continue
            else:
                text += 1
        await ctx.send(
            embeds=Embed(
                title="伺服器查詢結果",
                description=f"以下是 {ctx.guild.name} 伺服器的相關資訊喔！",
                fields=[
                    EmbedField(name="**伺服器名稱**", value=f"`{ctx.guild.name}`", inline=True),
                    EmbedField(name="**伺服器ID**", value=str(ctx.guild.id), inline=True),
                    EmbedField(name="**伺服器擁有者**", value=owner.mention, inline=True),
                    EmbedField(
                        name="**頻道數量**",
                        value=f"文字頻道: {text}\n語音頻道: {voice}\n分類: {category}",
                        inline=True,
                    ),
                    EmbedField(
                        name="**成員資訊**",
                        value=f"成員數: {ctx.guild.member_count}\n身份組: {len(ctx.guild.roles)}",
                        inline=True,
                    ),
                    EmbedField(
                        name="**伺服器加成**",
                        value=f"數量: {ctx.guild.premium_subscription_count if ctx.guild.premium_subscription_count else 0}\n等級: {ctx.guild.premium_tier if ctx.guild.premium_tier else 0}",
                        inline=True,
                    ),
                    # EmbedField(
                    #     name="**伺服器表情符號**",
                    #     value=f"{len(ctx.guild.emojis)}/{'50'if not ctx.guild.premium_tier or ctx.guild.premium_tier == 0 else '100' if ctx.guild.premium_tier == 1 else '150' if ctx.guild.premium_tier == 2 else '250'}",
                    #     inline=True,
                    # ),
                    EmbedField(
                        name="**創建時間**",
                        value=f"<t:{round(ctx.guild.id.timestamp.timestamp())}:F> (<t:{round(ctx.guild.id.timestamp.timestamp())}:R>)",
                        inline=True,
                    ),
                ],
                author=EmbedAuthor(name=ctx.guild.name, icon_url=ctx.guild.icon_url),
                thumbnail=EmbedImageStruct(url=ctx.guild.icon_url) if ctx.guild.icon else None,
                image=EmbedImageStruct(url=f"{ctx.guild.banner_url}?size=480")
                if ctx.guild.banner
                else None,
                color=randint(0, 0xFFFFFF),
            )
        )

    @info.group(name="bot")
    async def _bot(self, *args, **kwargs):
        ...

    @_bot.subcommand(name="detail")
    async def bot_info(self, ctx: CommandContext):
        """查詢機器人資訊"""
        await ctx.send(":x: 我還沒有學會這個指令！")  # TODO: 這裡還沒寫完

    @_bot.subcommand(name="status")
    async def bot_status(self, ctx: CommandContext):
        """查看我的狀態"""
        callback_time = datetime.utcnow()
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
                    value=f"RAM 使用量: **{round(tracemalloc.get_traced_memory()[0]/1000000, 2)}**mb\n延遲: 大概 **{abs(round((ctx.id.timestamp - callback_time).total_seconds()/1000, 2))}**ms 吧？\n我會一直陪著你喔！",
                    inline=False,
                ),
            ],
            color=randint(0, 0xFFFFFF),
        )
        await ctx.send(embeds=embed)

    @extension_user_command(name="使用者查詢")
    async def _user_info(self, ctx: CommandContext):
        user = await get(self.client, User, object_id=ctx.target.id)
        await ctx.send(
            embeds=Embed(
                title="使用者查詢結果",
                description=f"以下是 {user.mention} 的相關資訊喔！",
                fields=[
                    EmbedField(
                        name="**使用者名稱**",
                        value=f"`{user.username}#{user.discriminator}`",
                        inline=True,
                    ),
                    EmbedField(name="**使用者ID**", value=str(user.id), inline=True),
                    EmbedField(name="**機器人**", value="是" if user.bot else "否", inline=False),
                    EmbedField(
                        name="**創建時間**",
                        value=f"<t:{round(user.id.timestamp.timestamp())}:F> (<t:{round(user.id.timestamp.timestamp())}:R>)",
                        inline=True,
                    ),
                ],
                author=EmbedAuthor(
                    name=f"{user.username}#{user.discriminator}", icon_url=user.avatar_url
                ),
                thumbnail=EmbedImageStruct(url=user.avatar_url) if user.avatar else None,
                image=EmbedImageStruct(url=f"{user.banner_url}?size=480") if user.banner else None,
                color=randint(0, 0xFFFFFF),
            )
        )


def setup(client, **kwargs):
    general(client, **kwargs)
