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
from io import BytesIO, StringIO

import aiohttp
import qrcode
from interactions import (
    Client,
    CommandContext,
    EmbedImageStruct,
    Extension,
    File,
    Member,
    extension_command,
    option,
)
from loguru._logger import Logger
from petpetgif import petpet

from utils import api_request, bullshit_generator, raweb

newline = "\n"


class generate(Extension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.logger: Logger = kwargs.get("logger")
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

    @extension_command()
    async def generate(self, *args, **kwargs):
        ...

    @generate.subcommand()
    @option("要唬爛的主題")
    @option("要生成的字數", max_value=50000, min_value=1)
    async def bullshit(self, ctx: CommandContext, topic: str, length: int = 250):
        """唬爛產生器"""
        await ctx.defer()
        data = await bullshit_generator(topic, length)
        file = File("bs.txt", StringIO(data)) if len(data) > 1950 else None
        await ctx.send(
            f"我幫你唬爛了關於 {topic} 的 {len(data)} 字文章！{f'{newline}{newline}{data}' if not file else ''}",
            files=file,
        )

    @generate.subcommand()
    @option("使用指令的對象")
    async def pet(self, ctx: CommandContext, user: Member):
        """摸一個用戶的頭"""
        if (url := user.user.avatar_url).startswith("https://cdn.discordapp.com/embed/avatars/"):
            return await ctx.send(":x: baka 我摸不到沒有頭像的人啦！", ephemeral=True)
        await ctx.defer()
        dest = BytesIO()
        async with aiohttp.ClientSession() as s, s.get(url) as r:
            petpet.make(BytesIO(await r.content.read()), dest)
        dest.seek(0)
        await ctx.send(
            embeds=raweb(
                desc=f"<@{ctx.user.id}> 摸了 <@{user.id}> 的頭",
                image=EmbedImageStruct(url="attachment://pet.gif"),
            ),
            files=File(filename="pet.gif", fp=dest),
        )

    @generate.subcommand()
    @option("要Clyde說的話", max_value=50000, min_value=1)
    async def clyde(self, ctx: CommandContext, text: str):
        """讓 Clyde 說話"""
        await ctx.defer()
        url = await api_request(f"https://nekobot.xyz/api/imagegen?type=clyde&text={text}")
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["message"])))

    @generate.subcommand()
    @option("用戶名稱")
    @option("要發的內容", max_length=280)
    async def faketweet(self, ctx: CommandContext, username: str, text: str):
        """發出假的推文"""
        await ctx.defer()
        if username.startswith("@"):
            username = username[1:]
        url = await api_request(
            f"https://nekobot.xyz/api/imagegen?type=tweet&username={username}&text={text}"
        )
        await ctx.send(embeds=raweb(image=EmbedImageStruct(url=url["message"])))

    @generate.subcommand()
    @option("要包含的文字", max_length=500)
    async def qr(self, ctx: CommandContext, text: str):
        """生成 QR Code"""
        await ctx.defer()
        qrcode.make(text).save(dest := BytesIO())
        dest.seek(0)
        await ctx.send(
            embeds=raweb(image=EmbedImageStruct(url="attachment://qr.png")),
            files=File(filename="qr.png", fp=dest),
        )


def setup(client, **kwargs):
    generate(client, **kwargs)
