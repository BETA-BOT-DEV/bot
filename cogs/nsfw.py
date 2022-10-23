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

from interactions import *
from loguru._logger import Logger

from utils import raweb, api_request


class nsfw(Extension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.logger: Logger = kwargs.get("logger")
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

    @extension_command(default_member_permissions=Permissions.ADMINISTRATOR)
    async def nsfw(self, *args, **kwargs):
        ...

    @nsfw.subcommand()
    async def pgif(self, ctx: CommandContext):
        """要色色嗎？"""
        await ctx.get_channel()
        if not ctx.channel.nsfw and not ctx.channel.type == ChannelType.DM:
            return await ctx.send(embeds=raweb(desc=":x: 不可以色色！這裡不是限制級頻道喔！", image=EmbedImageStruct(url='https://media.tenor.com/DhIuVPza3QYAAAAC/不可以色色.gif')), ephemeral=True)
        await ctx.defer()
        url = await api_request("https://nekobot.xyz/api/image?type=pgif")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url['message'])))

    @nsfw.subcommand(name="4k")
    async def _4k(self, ctx: CommandContext):
        """要色色嗎？"""
        await ctx.get_channel()
        if not ctx.channel.nsfw and not ctx.channel.type == ChannelType.DM:
            return await ctx.send(embeds=raweb(desc=":x: 不可以色色！這裡不是限制級頻道喔！", image=EmbedImageStruct(url='https://media.tenor.com/DhIuVPza3QYAAAAC/不可以色色.gif')), ephemeral=True)
        await ctx.defer()
        url = await api_request("https://nekobot.xyz/api/image?type=4k")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url['message'])))

    @nsfw.subcommand()
    async def anal(self, ctx: CommandContext):
        """要色色嗎？"""
        await ctx.get_channel()
        if not ctx.channel.nsfw and not ctx.channel.type == ChannelType.DM:
            return await ctx.send(embeds=raweb(desc=":x: 不可以色色！這裡不是限制級頻道喔！", image=EmbedImageStruct(url='https://media.tenor.com/DhIuVPza3QYAAAAC/不可以色色.gif')), ephemeral=True)
        await ctx.defer()
        url = await api_request("https://nekobot.xyz/api/image?type=anal")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url['message'])))
    
    @nsfw.subcommand()
    async def ass(self, ctx: CommandContext):
        """要色色嗎？"""
        await ctx.get_channel()
        if not ctx.channel.nsfw and not ctx.channel.type == ChannelType.DM:
            return await ctx.send(embeds=raweb(desc=":x: 不可以色色！這裡不是限制級頻道喔！", image=EmbedImageStruct(url='https://media.tenor.com/DhIuVPza3QYAAAAC/不可以色色.gif')), ephemeral=True)
        await ctx.defer()
        url = await api_request("https://nekobot.xyz/api/image?type=ass")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url['message'])))

    @nsfw.subcommand()
    async def gonewild(self, ctx: CommandContext):
        """要色色嗎？"""
        await ctx.get_channel()
        if not ctx.channel.nsfw and not ctx.channel.type == ChannelType.DM:
            return await ctx.send(embeds=raweb(desc=":x: 不可以色色！這裡不是限制級頻道喔！", image=EmbedImageStruct(url='https://media.tenor.com/DhIuVPza3QYAAAAC/不可以色色.gif')), ephemeral=True)
        await ctx.defer()
        url = await api_request("https://nekobot.xyz/api/image?type=gonewild")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url['message'])))
    
    @nsfw.subcommand()
    async def pussy(self, ctx: CommandContext):
        """要色色嗎？"""
        await ctx.get_channel()
        if not ctx.channel.nsfw and not ctx.channel.type == ChannelType.DM:
            return await ctx.send(embeds=raweb(desc=":x: 不可以色色！這裡不是限制級頻道喔！", image=EmbedImageStruct(url='https://media.tenor.com/DhIuVPza3QYAAAAC/不可以色色.gif')), ephemeral=True)
        await ctx.defer()
        url = await api_request("https://nekobot.xyz/api/image?type=pussy")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url['message'])))
    
    @nsfw.subcommand()
    async def thigh(self, ctx: CommandContext):
        """要色色嗎？"""
        await ctx.get_channel()
        if not ctx.channel.nsfw and not ctx.channel.type == ChannelType.DM:
            return await ctx.send(embeds=raweb(desc=":x: 不可以色色！這裡不是限制級頻道喔！", image=EmbedImageStruct(url='https://media.tenor.com/DhIuVPza3QYAAAAC/不可以色色.gif')), ephemeral=True)
        await ctx.defer()
        url = await api_request("https://nekobot.xyz/api/image?type=thigh")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url['message'])))

    @nsfw.subcommand()
    async def boobs(self, ctx: CommandContext):
        """要色色嗎？"""
        await ctx.get_channel()
        if not ctx.channel.nsfw and not ctx.channel.type == ChannelType.DM:
            return await ctx.send(embeds=raweb(desc=":x: 不可以色色！這裡不是限制級頻道喔！", image=EmbedImageStruct(url='https://media.tenor.com/DhIuVPza3QYAAAAC/不可以色色.gif')), ephemeral=True)
        await ctx.defer()
        url = await api_request("https://nekobot.xyz/api/image?type=boobs")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url['message'])))


def setup(client, **kwargs):
    nsfw(client, **kwargs)
