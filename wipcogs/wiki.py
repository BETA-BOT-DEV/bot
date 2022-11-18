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
from urllib.parse import quote

import bs4
from interactions import (
    Button,
    ButtonStyle,
    Client,
    CommandContext,
    Embed,
    EmbedAuthor,
    EmbedFooter,
    EmbedImageStruct,
    Extension,
    extension_command,
    option,
)
from loguru._logger import Logger

from utils import api_request

# from mediawiki import MediaWiki


newline = "\n"


class Wiki(Extension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.logger: Logger = kwargs.get("logger")
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

    @extension_command()
    async def wiki(self, *args, **kwargs):
        ...

    @wiki.subcommand()
    @option("條目標題")
    async def page(self, ctx: CommandContext, query: str):
        """前往維基百科條目"""
        await ctx.defer()
        data = await api_request(
            f"https://zh.wikipedia.org/api/rest_v1/page/summary/{quote(query.replace(' ', '_'))}",
            {
                "accept-language": "zh-TW",
                "accept": 'application/json; charset=utf-8; profile="https://www.mediawiki.org/wiki/Specs/Summary/1.4.2"',
            },
        )
        if not data:
            return await ctx.send(":x: baka 該條目不存在啦！")
        print(data)
        if data["type"] == "disambiguation":
            title = bs4.BeautifulSoup(data["displaytitle"], "html.parser").get_text()
            content = []
            for i in bs4.BeautifulSoup(data["extract_html"], "html.parser").find_all("li"):
                item = i.get_text().split("，", 1)
                content.append(f"**{item[0]}** - {item[1]}") if len(item) > 1 else content.append(
                    f"**{item[0]}**"
                )
            content = "\n".join(content)
            embed = Embed(
                title=f"**{title}** 可以指：",
                description=content,
                url=data["content_urls"]["desktop"]["page"],
                author=EmbedAuthor(
                    name="維基百科 - 消歧義",
                    url="https://zh.wikipedia.org/",
                    icon_url="https://www.wikipedia.org/portal/wikipedia.org/assets/img/Wikipedia-logo-v2.png",
                ),
                image=EmbedImageStruct(
                    url=data["thumbnail"]["source"],
                    width=data["thumbnail"]["width"],
                    height=data["thumbnail"]["height"],
                )
                if "thumbnail" in data
                else None,
                footer=EmbedFooter(text="請以維基百科條目名稱再次搜尋。"),
            )
        else:
            embed = Embed(
                title=bs4.BeautifulSoup(data["displaytitle"], "html.parser").get_text(),
                description=data["extract"],
                url=data["content_urls"]["desktop"]["page"],
                author=EmbedAuthor(
                    name="維基百科 - 搜尋條目",
                    url="https://zh.wikipedia.org/",
                    icon_url="https://www.wikipedia.org/portal/wikipedia.org/assets/img/Wikipedia-logo-v2.png",
                ),
                image=EmbedImageStruct(
                    url=data["thumbnail"]["source"],
                    width=data["thumbnail"]["width"],
                    height=data["thumbnail"]["height"],
                )
                if "thumbnail" in data
                else None,
            )
        components = [
            Button(
                style=ButtonStyle.LINK, label="前往頁面", url=data["content_urls"]["desktop"]["page"]
            ),
        ]
        await ctx.send(embeds=embed, components=components)

    @wiki.subcommand()
    async def random(self, ctx: CommandContext):
        """隨機顯示維基百科條目"""
        await ctx.defer()
        data = await api_request(
            "https://zh.wikipedia.org/api/rest_v1/page/random/summary",
            {"accept-language": "zh-TW", "accept": "application/problem+json"},
        )
        embed = Embed(
            title=bs4.BeautifulSoup(data["displaytitle"], "html.parser").get_text(),
            description=data["extract"],
            url=data["content_urls"]["desktop"]["page"],
            author=EmbedAuthor(
                name="維基百科 - 隨機條目",
                url="https://zh.wikipedia.org/",
                icon_url="https://www.wikipedia.org/portal/wikipedia.org/assets/img/Wikipedia-logo-v2.png",
            ),
            image=EmbedImageStruct(
                url=data["thumbnail"]["source"],
                width=data["thumbnail"]["width"],
                height=data["thumbnail"]["height"],
            )
            if "thumbnail" in data
            else None,
        )
        components = [
            Button(
                style=ButtonStyle.LINK, label="前往頁面", url=data["content_urls"]["desktop"]["page"]
            ),
        ]
        await ctx.send(embeds=embed, components=components)


def setup(client, **kwargs):
    Wiki(client, **kwargs)
