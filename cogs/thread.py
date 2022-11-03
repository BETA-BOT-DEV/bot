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

from interactions import (
    ChannelType,
    Client,
    CommandContext,
    Extension,
    LibraryException,
    Member,
    Permissions,
    Thread,
    extension_command,
    extension_listener,
    option,
)
from loguru._logger import Logger

newline = "\n"


class thread(Extension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.logger: Logger = kwargs.get("logger")
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

    @extension_listener
    async def on_thread_create(self, thread: Thread):
        try:
            await thread.join()
        except LibraryException:
            pass

    @extension_command(default_member_permissions=Permissions.MANAGE_THREADS)
    async def thread(self, *args, **kwargs):
        ...

    @thread.subcommand()
    async def archive(self, ctx: CommandContext):
        """關閉貼文或討論串"""
        await ctx.get_channel()
        if ctx.channel.type not in [ChannelType.PUBLIC_THREAD, ChannelType.PRIVATE_THREAD]:
            return await ctx.send(":x: baka 你只能關閉貼文或者討論串啦！", ephemeral=True)
        await ctx.send("關閉中...")
        try:
            await ctx.channel.modify(archived=True, locked=True)
        except LibraryException:
            await ctx.send(":x: 對不起！關閉貼文或者討論串時出現錯誤了！", ephemeral=True)

    @thread.subcommand()
    @option("要新增的成員")
    async def add(self, ctx: CommandContext, user: Member):
        """新增討論串成員"""
        await ctx.get_channel()
        if ctx.channel.type not in [ChannelType.PUBLIC_THREAD, ChannelType.PRIVATE_THREAD]:
            return await ctx.send(":x: baka 你只能在貼文或者討論串新增成員啦！", ephemeral=True)
        if user.id in [i.user_id for i in await ctx.channel.get_members()]:
            return await ctx.send(":x: baka 這個成員已經在討論串裡了啦！", ephemeral=True)
        await ctx.channel.add_member(user)
        await ctx.send(f"好了！{user.mention} 已經被新增到討論串了！")

    @thread.subcommand()
    @option("要移除的成員")
    async def remove(self, ctx: CommandContext, user: Member):
        """移除討論串成員"""
        await ctx.get_channel()
        if ctx.channel.type not in [ChannelType.PUBLIC_THREAD, ChannelType.PRIVATE_THREAD]:
            return await ctx.send(":x: baka 你只能在貼文或者討論串移除成員啦！", ephemeral=True)
        if user.id not in [i.user_id for i in await ctx.channel.get_members()]:
            return await ctx.send(":x: baka 這個成員不在討論串裡面啦！", ephemeral=True)
        await ctx.channel.remove_member(user)
        await ctx.send(f"好了！{user.mention} 已經被移出討論串了！")


def setup(client, **kwargs):
    thread(client, **kwargs)
