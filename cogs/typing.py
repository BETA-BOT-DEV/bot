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

import aiofiles
from interactions import (
    Channel,
    Client,
    CommandContext,
    Extension,
    Permissions,
    extension_command,
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
            await self.client._http.trigger_typing(int(i))

    @extension_command(default_member_permissions=Permissions.MANAGE_CHANNELS, dm_permission=False)
    async def typing(self, *args, **kwargs):
        ...

    @typing.subcommand()
    @option("要我開始打字的頻道")
    async def start(self, ctx: CommandContext, channel: Channel = None):
        """讓我開始打字"""
        if not channel:
            channel = int(ctx.channel_id)
        else:
            channel = int(channel.id)
        async with aiofiles.open("./storage/typing.txt", "r") as f:
            data = await f.read()
        if str(channel) in data:
            await ctx.send(":x: baka 我已經在這個頻道輸入中...", ephemeral=True)
        else:
            await ctx.send(f"好了！我會在 <#{channel}> 開始輸入...", ephemeral=True)
            self._channels.append(channel)
            async with aiofiles.open("./storage/typing.txt", "a") as f:
                await f.write(f"{channel}\n")
        await self.client._http.trigger_typing(int(channel))

    @typing.subcommand()
    @option("要我停止打字的頻道")
    async def stop(self, ctx: CommandContext, channel: Channel = None):
        """讓我停止打字"""
        if not channel:
            channel = int(ctx.channel_id)
        else:
            channel = int(channel.id)
        async with aiofiles.open("./storage/typing.txt", "r") as f:
            data = await f.read()
        if str(channel) not in data:
            return await ctx.send(":x: baka 我沒有在這個頻道輸入喔！", ephemeral=True)
        self._channels.remove(channel)
        async with aiofiles.open("./storage/typing.txt", "w") as f:
            await f.write(newline.join(self._channels))
        await ctx.send(f"好了！我會停止在 <#{channel}> 輸入了", ephemeral=True)


def setup(client, **kwargs):
    typing(client, **kwargs)