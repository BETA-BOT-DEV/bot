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

from datetime import datetime, timedelta
import os

from interactions import *
from loguru._logger import Logger

newline = '\n'


class moderate(Extension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.logger: Logger = kwargs.get("logger")
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )
# TODO: consider adding user interactions + rework content
    @extension_command(dm_permission=False, default_member_permissions=Permissions.MANAGE_MESSAGES)
    @option("要刪除的訊息數量", min_value=1)
    async def purge(self, ctx: CommandContext, limit: int):
        """清除訊息"""
        await ctx.defer(ephemeral=True)
        await ctx.get_channel()
        try:
            deleted = await ctx.channel.purge(amount=limit)
        except LibraryException:
            await ctx.send(":x: 有些訊息我刪不掉 ;-;", ephemeral=True)
        else:
            await ctx.send(f"我清除了 {len(deleted)} 條訊息！不過14天之前的訊息我動不了。", ephemeral=True)
    
    @extension_command(dm_permission=False, default_member_permissions=Permissions.KICK_MEMBERS)
    @option("要踢的人")
    @option("原因")
    async def kick(self, ctx: CommandContext, member: Member, reason: str = None):
        """踢出成員"""
        await ctx.defer(ephemeral=True)
        if not ctx.app_permissions.KICK_MEMBERS:
            return await ctx.send(":x: 我沒權限踢人 ;-;", ephemeral=True)
        try:
            await member.kick(ctx.guild_id, reason)
        except LibraryException:
            return await ctx.send(f":x: 我踢不動 {member.mention} ;-;", ephemeral=True)
        else:
            await ctx.send(f"我把 {member.user.username}#{member.user.discriminator} 踢出去了！再見！", ephemeral=True)

    @extension_command(dm_permission=False, default_member_permissions=Permissions.BAN_MEMBERS)
    @option("要封鎖的人")
    @option("原因")
    async def ban(self, ctx: CommandContext, member: Member, reason: str = None):
        """封鎖成員"""
        await ctx.defer(ephemeral=True)
        if not ctx.app_permissions.BAN_MEMBERS:
            return await ctx.send(":x: 我沒權限封鎖其他人 ;-;", ephemeral=True)
        try:
            await member.ban(ctx.guild_id, reason)
        except LibraryException:
            return await ctx.send(f":x: 我封鎖不了 {member.mention} ;-;", ephemeral=True)
        else:
            await ctx.send(f"我把 {member.user.username}#{member.user.discriminator} 封鎖了！再見！", ephemeral=True)
    
    @extension_command(dm_permission=False, default_member_permissions=Permissions.MODERATE_MEMBERS)
    @option("要禁言的人")
    @option("禁言時間", choices=[Choice(name='60秒', value=0), Choice(name='5分鐘', value=1), Choice(name='10分鐘', value=2), Choice(name='1小時', value=3), Choice(name='1天', value=4), Choice(name='1週', value=5)])
    @option("原因")
    async def timeout(self, ctx: CommandContext, member: Member, time: int, reason: str = None):
        """禁言成員"""
        await ctx.defer(ephemeral=True)
        if not ctx.app_permissions.MODERATE_MEMBERS:
            return await ctx.send(":x: 我沒權限禁言 ;-;", ephemeral=True)
        match time:
            case 0: length = timedelta(seconds=60)
            case 1: length = timedelta(minutes=5)
            case 2: length = timedelta(minutes=10)
            case 3: length = timedelta(hours=1)
            case 4: length = timedelta(days=1)
            case 5: length = timedelta(days=7)
            case _: return await ctx.send(":x: baka 你到底要禁言多久啊？", ephemeral=True)
        try:
            await member.modify(ctx.guild_id, reason=reason, communication_disabled_until=(datetime.utcnow()+length).isoformat())
        except LibraryException:
            return await ctx.send(f":x: 我禁言不了 {member.mention} ;-;", ephemeral=True)
        else:
            await ctx.send(f"我把 {member.mention} 禁言了！", ephemeral=True)


def setup(client, **kwargs):
    moderate(client, **kwargs)
