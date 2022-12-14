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

from decouple import config
from interactions import (
    Client,
    CommandContext,
    EmbedImageStruct,
    Extension,
    extension_command,
)
from loguru._logger import Logger

from utils import api_request, raweb


class sfw(Extension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.logger: Logger = kwargs.get("logger")
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

    @extension_command()
    async def image(self, *args, **kwargs):
        ...

    @image.subcommand()
    async def neko(self, ctx: CommandContext):
        """來看看可愛的貓娘吧！"""
        await ctx.defer()
        match randint(0, 5):
            case 0:
                url = await api_request("https://hmtai.herokuapp.com/v2/neko_arts")
                await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["url"])))
            case 1:
                url = await api_request("https://nekos.life/api/v2/img/neko")
                await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["url"])))
            case 2:
                url = await api_request("https://nekobot.xyz/api/image?type=neko")
                if url == 429:
                    return await ctx.send(":x: 對不起！我被伺服器限制速率啦！ ><")
                await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["message"])))
            case 3:
                url = await api_request("https://nekos.moe/api/v1/random/image?nsfw=false&tags=cat")
                await ctx.send(
                    embeds=raweb(
                        image=EmbedImageStruct(
                            url=f"https://nekos.moe/image/{url['images'][0]['id']}"
                        )
                    )
                )
            case 4:
                url = await api_request("https://nekos.best/api/v2/neko")
                await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["results"][0]["url"])))
            case 5:
                url = await api_request("https://api.waifu.pics/sfw/neko")
                await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["url"])))

    @image.subcommand()
    async def kitsune(self, ctx: CommandContext):
        """狐狸也是很可愛的喔！"""
        await ctx.defer()
        url = await api_request("https://nekos.life/api/v2/img/fox_girl")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["url"])))

    @image.subcommand()
    async def kanna(self, ctx: CommandContext):
        """我的主人很懶，沒有留下說明。"""  # TODO: Add description
        await ctx.defer()
        url = await api_request("https://nekobot.xyz/api/image?type=kanna")
        if url == 429:
            return await ctx.send(":x: 對不起！我被伺服器限制速率啦！ ><")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["message"])))

    @image.subcommand()
    async def kemonomimi(self, ctx: CommandContext):
        """我的主人很懶，沒有留下說明。"""  # TODO: Add description
        await ctx.defer()
        url = await api_request("https://nekobot.xyz/api/image?type=kemonomimi")
        if url == 429:
            return await ctx.send(":x: 對不起！我被伺服器限制速率啦！ ><")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["message"])))

    @image.subcommand()
    async def holo(self, ctx: CommandContext):
        """我的主人很懶，沒有留下說明。"""  # TODO: Add description
        await ctx.defer()
        url = await api_request("https://nekobot.xyz/api/image?type=holo")
        if url == 429:
            return await ctx.send(":x: 對不起！我被伺服器限制速率啦！ ><")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["message"])))

    @image.subcommand()
    async def waifu(self, ctx: CommandContext):
        """我的主人很懶，沒有留下說明。"""  # TODO: Add description
        await ctx.defer()
        url = await api_request("https://api.waifu.pics/sfw/waifu")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["url"])))

    @image.subcommand()
    async def megumin(self, ctx: CommandContext):
        """我的主人很懶，沒有留下說明。"""  # TODO: Add description
        await ctx.defer()
        url = await api_request("https://api.waifu.pics/sfw/megumin")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["url"])))

    @image.subcommand()
    async def awoo(self, ctx: CommandContext):
        """我的主人很懶，沒有留下說明。"""  # TODO: Add description
        await ctx.defer()
        url = await api_request("https://api.waifu.pics/sfw/awoo")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["url"])))

    @image.subcommand()
    async def cat(self, ctx: CommandContext):
        """是貓咪喔！"""
        await ctx.defer()
        match randint(0, 1):
            case 0:
                url = await api_request(
                    "https://api.thecatapi.com/v1/images/search", {"x-api-key": config("thecatapi")}
                )
                url = url[0]["url"]
            case 1:
                url = await api_request("https://nekos.life/api/v2/img/meow")
                url = url["url"]
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url)))

    @image.subcommand()
    async def dog(self, ctx: CommandContext):
        """來看狗勾！"""
        await ctx.defer()
        url = await api_request("https://dog.ceo/api/breeds/image/random")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["message"])))

    @image.subcommand()
    async def coffee(self, ctx: CommandContext):
        """要來杯咖啡嗎？"""
        await ctx.defer()
        url = await api_request("https://nekobot.xyz/api/image?type=coffee")
        if url == 429:
            return await ctx.send(":x: 對不起！我被伺服器限制速率啦！ ><")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["message"])))

    @image.subcommand()
    async def food(self, ctx: CommandContext):
        """好吃的東西！"""
        await ctx.defer()
        url = await api_request("https://nekobot.xyz/api/image?type=food")
        if url == 429:
            return await ctx.send(":x: 對不起！我被伺服器限制速率啦！ ><")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["message"])))


def setup(client, **kwargs):
    sfw(client, **kwargs)
