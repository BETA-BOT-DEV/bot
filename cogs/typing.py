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

import contextlib
import os

import aiofiles
from interactions import (
    Channel,
    ChannelType,
    Client,
    CommandContext,
    Extension,
    Member,
    Permissions,
    extension_command,
    get,
    option,
)
from interactions.ext.tasks import IntervalTrigger, create_task
from loguru._logger import Logger

newline = "\n"


class typing(Extension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.logger: Logger = kwargs.get("logger")
        self._channels = None
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )
        self._typing.start(self)

    @create_task(IntervalTrigger(5))
    async def _typing(self):
        if self._channels is None:
            async with aiofiles.open("./storage/typing.txt", "r") as f:
                data = await f.read()
                self._channels = [int(i) for i in data.split(newline) if i != ""]
        for i in self._channels:
            with contextlib.suppress(Exception):
                await self.client._http.trigger_typing(int(i))

    @extension_command(default_member_permissions=Permissions.MANAGE_CHANNELS, dm_permission=False)
    async def typing(self, *args, **kwargs):
        ...

    @typing.subcommand()
    @option(
        "要我開始打字的頻道",
        channel_type=[
            ChannelType.GUILD_TEXT,
            ChannelType.GUILD_ANNOUNCEMENT,
            ChannelType.PUBLIC_THREAD,
            ChannelType.PRIVATE_THREAD,
            ChannelType.ANNOUNCEMENT_THREAD,
            ChannelType.GUILD_VOICE,
        ],
    )
    async def start(self, ctx: CommandContext, channel: Channel = None):
        """讓我開始打字"""
        await ctx.defer(ephemeral=True)
        bot = await get(self.client, Member, object_id=self.client.me.id, parent_id=ctx.guild_id)
        if not channel:
            channel = await ctx.get_channel()
        async with aiofiles.open("./storage/typing.txt", "r") as f:
            data = await f.read()
        if str(channel.id) in data:
            await ctx.send(":x: baka 我已經在這個頻道輸入中...", ephemeral=True)
        elif await channel.get_permissions_for(bot) & Permissions.SEND_MESSAGES:
            await ctx.send(f"好了！我會在 {channel.mention} 開始輸入...", ephemeral=True)
            self._channels.append(int(channel.id))
            async with aiofiles.open("./storage/typing.txt", "a") as f:
                await f.write(f"{channel.id}\n")
        else:
            await ctx.send(":x: baka 我沒有權限在那個頻道輸入...", ephemeral=True)
        await self.client._http.trigger_typing(channel.id)

    @typing.subcommand()
    @option(
        "要我停止打字的頻道",
        channel_type=[
            ChannelType.GUILD_TEXT,
            ChannelType.GUILD_ANNOUNCEMENT,
            ChannelType.PUBLIC_THREAD,
            ChannelType.PRIVATE_THREAD,
            ChannelType.ANNOUNCEMENT_THREAD,
            ChannelType.GUILD_VOICE,
        ],
    )
    async def stop(self, ctx: CommandContext, channel: Channel = None):
        """讓我停止打字"""
        channel = int(channel.id) if channel else int(ctx.channel_id)
        async with aiofiles.open("./storage/typing.txt", "r") as f:
            data = await f.read()
        if str(channel) not in data:
            return await ctx.send(":x: baka 我沒有在這個頻道輸入喔！", ephemeral=True)
        self._channels.remove(channel)
        async with aiofiles.open("./storage/typing.txt", "w") as f:
            await f.write(newline.join([str(i) for i in self._channels]))
        await ctx.send(f"好了！我會停止在 <#{channel}> 輸入了", ephemeral=True)


def setup(client, **kwargs):
    typing(client, **kwargs)
