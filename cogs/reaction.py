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
    Client,
    CommandContext,
    EmbedImageStruct,
    Extension,
    extension_command,
)
from loguru._logger import Logger

from utils import api_request, raweb

newline = "\n"


class reaction(Extension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.logger: Logger = kwargs.get("logger")
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

    @extension_command()
    async def reaction(self, *args, **kwargs):
        """反應指令"""
        ...

    @reaction.subcommand()
    async def blush(self, ctx: CommandContext):
        """(⁄ ⁄•⁄ω⁄•⁄ ⁄)⁄"""
        await ctx.defer()
        match randint(0, 1):
            case 0:
                url = await api_request("https://nekos.best/api/v2/blush")
                await ctx.send(
                    embeds=raweb(
                        desc=f"{ctx.author.mention} (⁄ ⁄•⁄ω⁄•⁄ ⁄)⁄",
                        image=EmbedImageStruct(url=url["results"][0]["url"]),
                    )
                )
            case 1:
                url = await api_request("https://api.waifu.pics/sfw/blush")
                await ctx.send(
                    embeds=raweb(
                        desc=f"{ctx.author.mention} (⁄ ⁄•⁄ω⁄•⁄ ⁄)⁄",
                        image=EmbedImageStruct(url=url["url"]),
                    )
                )

    @reaction.subcommand()
    async def sleepy(self, ctx: CommandContext):
        """(。-ω-)zzz"""
        await ctx.defer()
        url = await api_request("https://nekos.best/api/v2/sleep")
        await ctx.send(
            embeds=raweb(
                desc=f"{ctx.author.mention} (。-ω-)zzz",
                image=EmbedImageStruct(url=url["results"][0]["url"]),
            )
        )

    @reaction.subcommand()
    async def cry(self, ctx: CommandContext):
        """｡･ﾟﾟ･(>д<)･ﾟﾟ･｡"""
        await ctx.defer()
        url = await api_request("https://nekos.best/api/v2/cry")
        await ctx.send(
            embeds=raweb(
                desc=f"{ctx.author.mention} ｡･ﾟﾟ･(>д<)･ﾟﾟ･｡",
                image=EmbedImageStruct(url=url["results"][0]["url"]),
            )
        )

    @reaction.subcommand()
    async def shrug(self, ctx: CommandContext):
        r"""¯\_(ツ)_/¯"""
        await ctx.defer()
        url = await api_request("https://nekos.best/api/v2/shrug")
        await ctx.send(
            embeds=raweb(
                desc=rf"{ctx.author.mention} ¯\_(ツ)_/¯",
                image=EmbedImageStruct(url=url["results"][0]["url"]),
            )
        )

    @reaction.subcommand()
    async def pout(self, ctx: CommandContext):
        """( ˘ ^˘ )=3"""
        await ctx.defer()
        url = await api_request("https://nekos.best/api/v2/pout")
        await ctx.send(
            embeds=raweb(
                desc=f"{ctx.author.mention} ( ˘ ^˘ )=3",
                image=EmbedImageStruct(url=url["results"][0]["url"]),
            )
        )

    @reaction.subcommand()
    async def baka(self, ctx: CommandContext):
        """(￣▽￣)"""
        await ctx.defer()
        url = await api_request("https://nekos.best/api/v2/baka")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["results"][0]["url"])))


def setup(client, **kwargs):
    reaction(client, **kwargs)
