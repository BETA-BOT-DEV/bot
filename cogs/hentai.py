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
from random import randint

from interactions import (
    ChannelType,
    Client,
    CommandContext,
    EmbedImageStruct,
    Extension,
    Permissions,
    extension_command,
)
from loguru._logger import Logger

from utils import api_request, raweb


class hentai(Extension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.logger: Logger = kwargs.get("logger")
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

    @extension_command(default_member_permissions=Permissions.ADMINISTRATOR)
    async def hentai(self, *args, **kwargs):
        ...

    @hentai.subcommand()
    async def ass(self, ctx: CommandContext):
        """要色色嗎？"""
        await ctx.get_channel()
        if not ctx.channel.nsfw and not ctx.channel.type == ChannelType.DM:
            return await ctx.send(
                embeds=raweb(
                    desc=":x: 不可以色色！這裡不是限制級頻道喔！",
                    image=EmbedImageStruct(
                        url="https://media.tenor.com/DhIuVPza3QYAAAAC/不可以色色.gif"
                    ),
                ),
                ephemeral=True,
            )
        await ctx.defer()
        url = await api_request("https://nekobot.xyz/api/image?type=hass")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["message"])))

    @hentai.subcommand()
    async def tummy(self, ctx: CommandContext):
        """要色色嗎？"""
        await ctx.get_channel()
        if not ctx.channel.nsfw and not ctx.channel.type == ChannelType.DM:
            return await ctx.send(
                embeds=raweb(
                    desc=":x: 不可以色色！這裡不是限制級頻道喔！",
                    image=EmbedImageStruct(
                        url="https://media.tenor.com/DhIuVPza3QYAAAAC/不可以色色.gif"
                    ),
                ),
                ephemeral=True,
            )
        await ctx.defer()
        url = await api_request("https://nekobot.xyz/api/image?type=hmidriff")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["message"])))

    @hentai.subcommand()
    async def thigh(self, ctx: CommandContext):
        """要色色嗎？"""
        await ctx.get_channel()
        if not ctx.channel.nsfw and not ctx.channel.type == ChannelType.DM:
            return await ctx.send(
                embeds=raweb(
                    desc=":x: 不可以色色！這裡不是限制級頻道喔！",
                    image=EmbedImageStruct(
                        url="https://media.tenor.com/DhIuVPza3QYAAAAC/不可以色色.gif"
                    ),
                ),
                ephemeral=True,
            )
        await ctx.defer()
        match randint(0, 1):
            case 0:
                url = await api_request("https://hmtai.herokuapp.com/v2/thighs")
                await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["url"])))
            case 1:
                url = await api_request("https://nekobot.xyz/api/image?type=hthigh")
                await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["message"])))

    @hentai.subcommand()
    async def hentai(self, ctx: CommandContext):
        """要色色嗎？"""
        await ctx.get_channel()
        if not ctx.channel.nsfw and not ctx.channel.type == ChannelType.DM:
            return await ctx.send(
                embeds=raweb(
                    desc=":x: 不可以色色！這裡不是限制級頻道喔！",
                    image=EmbedImageStruct(
                        url="https://media.tenor.com/DhIuVPza3QYAAAAC/不可以色色.gif"
                    ),
                ),
                ephemeral=True,
            )
        await ctx.defer()
        match randint(0, 1):
            case 0:
                url = await api_request("https://hmtai.herokuapp.com/v2/hentai")
                await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["url"])))
            case 1:
                url = await api_request("https://nekobot.xyz/api/image?type=hentai")
                await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["message"])))

    @hentai.subcommand()
    async def kitsune(self, ctx: CommandContext):
        """要色色嗎？"""
        await ctx.get_channel()
        if not ctx.channel.nsfw and not ctx.channel.type == ChannelType.DM:
            return await ctx.send(
                embeds=raweb(
                    desc=":x: 不可以色色！這裡不是限制級頻道喔！",
                    image=EmbedImageStruct(
                        url="https://media.tenor.com/DhIuVPza3QYAAAAC/不可以色色.gif"
                    ),
                ),
                ephemeral=True,
            )
        await ctx.defer()
        url = await api_request("https://nekobot.xyz/api/image?type=hkitsune")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["message"])))

    @hentai.subcommand()
    async def anal(self, ctx: CommandContext):
        """要色色嗎？"""
        await ctx.get_channel()
        if not ctx.channel.nsfw and not ctx.channel.type == ChannelType.DM:
            return await ctx.send(
                embeds=raweb(
                    desc=":x: 不可以色色！這裡不是限制級頻道喔！",
                    image=EmbedImageStruct(
                        url="https://media.tenor.com/DhIuVPza3QYAAAAC/不可以色色.gif"
                    ),
                ),
                ephemeral=True,
            )
        await ctx.defer()
        url = await api_request("https://nekobot.xyz/api/image?type=hanal")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["message"])))

    @hentai.subcommand()
    async def neko(self, ctx: CommandContext):
        """要色色嗎？"""
        await ctx.get_channel()
        if not ctx.channel.nsfw and not ctx.channel.type == ChannelType.DM:
            return await ctx.send(
                embeds=raweb(
                    desc=":x: 不可以色色！這裡不是限制級頻道喔！",
                    image=EmbedImageStruct(
                        url="https://media.tenor.com/DhIuVPza3QYAAAAC/不可以色色.gif"
                    ),
                ),
                ephemeral=True,
            )
        await ctx.defer()
        match randint(0, 3):
            case 0:
                url = await api_request("https://hmtai.herokuapp.com/v2/nsfwNeko")
                await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["url"])))
            case 1:
                url = await api_request("https://nekobot.xyz/api/image?type=hneko")
                await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["message"])))
            case 2:
                url = await api_request("https://neko-love.xyz/api/v1/nekolewd")
                await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["url"])))
            case 3:
                url = await api_request("https://nekos.moe/api/v1/random/image?nsfw=true&tags=cat")
                await ctx.send(
                    embeds=raweb(
                        image=EmbedImageStruct(
                            url=f"https://nekos.moe/image/{url['images'][0]['id']}"
                        )
                    )
                )

    @hentai.subcommand()
    async def paizuri(self, ctx: CommandContext):
        """要色色嗎？"""
        await ctx.get_channel()
        if not ctx.channel.nsfw and not ctx.channel.type == ChannelType.DM:
            return await ctx.send(
                embeds=raweb(
                    desc=":x: 不可以色色！這裡不是限制級頻道喔！",
                    image=EmbedImageStruct(
                        url="https://media.tenor.com/DhIuVPza3QYAAAAC/不可以色色.gif"
                    ),
                ),
                ephemeral=True,
            )
        await ctx.defer()
        url = await api_request("https://nekobot.xyz/api/image?type=paizuri")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["message"])))

    @hentai.subcommand()
    async def tentacle(self, ctx: CommandContext):
        """要色色嗎？"""
        await ctx.get_channel()
        if not ctx.channel.nsfw and not ctx.channel.type == ChannelType.DM:
            return await ctx.send(
                embeds=raweb(
                    desc=":x: 不可以色色！這裡不是限制級頻道喔！",
                    image=EmbedImageStruct(
                        url="https://media.tenor.com/DhIuVPza3QYAAAAC/不可以色色.gif"
                    ),
                ),
                ephemeral=True,
            )
        await ctx.defer()
        match randint(0, 1):
            case 0:
                url = await api_request("https://hmtai.herokuapp.com/v2/tentacle")
                await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["url"])))
            case 1:
                url = await api_request("https://nekobot.xyz/api/image?type=tentacle")
                await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["message"])))

    @hentai.subcommand()
    async def boobs(self, ctx: CommandContext):
        """要色色嗎？"""
        await ctx.get_channel()
        if not ctx.channel.nsfw and not ctx.channel.type == ChannelType.DM:
            return await ctx.send(
                embeds=raweb(
                    desc=":x: 不可以色色！這裡不是限制級頻道喔！",
                    image=EmbedImageStruct(
                        url="https://media.tenor.com/DhIuVPza3QYAAAAC/不可以色色.gif"
                    ),
                ),
                ephemeral=True,
            )
        await ctx.defer()
        match randint(0, 1):
            case 0:
                url = await api_request("https://hmtai.herokuapp.com/v2/boobs")
                await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["url"])))
            case 1:
                url = await api_request("https://nekobot.xyz/api/image?type=hboobs")
                await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["message"])))

    @hentai.subcommand()
    async def yuri(self, ctx: CommandContext):
        """要色色嗎？"""
        await ctx.get_channel()
        if not ctx.channel.nsfw and not ctx.channel.type == ChannelType.DM:
            return await ctx.send(
                embeds=raweb(
                    desc=":x: 不可以色色！這裡不是限制級頻道喔！",
                    image=EmbedImageStruct(
                        url="https://media.tenor.com/DhIuVPza3QYAAAAC/不可以色色.gif"
                    ),
                ),
                ephemeral=True,
            )
        await ctx.defer()
        url = await api_request("https://hmtai.herokuapp.com/v2/yuri")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["url"])))

    @hentai.subcommand()
    async def pantsu(self, ctx: CommandContext):
        """要色色嗎？"""
        await ctx.get_channel()
        if not ctx.channel.nsfw and not ctx.channel.type == ChannelType.DM:
            return await ctx.send(
                embeds=raweb(
                    desc=":x: 不可以色色！這裡不是限制級頻道喔！",
                    image=EmbedImageStruct(
                        url="https://media.tenor.com/DhIuVPza3QYAAAAC/不可以色色.gif"
                    ),
                ),
                ephemeral=True,
            )
        await ctx.defer()
        url = await api_request("https://hmtai.herokuapp.com/v2/pantsu")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["url"])))

    @hentai.subcommand()
    async def waifu(self, ctx: CommandContext):
        """要色色嗎？"""
        await ctx.get_channel()
        if not ctx.channel.nsfw and not ctx.channel.type == ChannelType.DM:
            return await ctx.send(
                embeds=raweb(
                    desc=":x: 不可以色色！這裡不是限制級頻道喔！",
                    image=EmbedImageStruct(
                        url="https://media.tenor.com/DhIuVPza3QYAAAAC/不可以色色.gif"
                    ),
                ),
                ephemeral=True,
            )
        await ctx.defer()
        url = await api_request("https://api.waifu.pics/nsfw/waifu")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["url"])))


def setup(client, **kwargs):
    hentai(client, **kwargs)
