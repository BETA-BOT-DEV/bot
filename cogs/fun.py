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
import re
from datetime import datetime, timedelta, timezone
from io import BytesIO
from random import choice, randint
from urllib.parse import quote_plus

import aiohttp
from interactions import (
    ActionRow,
    AllowedMentions,
    Attachment,
    Button,
    ButtonStyle,
    Choice,
    Client,
    CommandContext,
    ComponentContext,
    Embed,
    EmbedField,
    EmbedFooter,
    EmbedImageStruct,
    File,
    Image,
    LibraryException,
    Message,
    OptionType,
    Permissions,
    SelectMenu,
    SelectOption,
    User,
    extension_autocomplete,
    extension_command,
    extension_message_command,
    get,
    option,
)
from interactions.ext.persistence import (
    PersistenceExtension,
    PersistentCustomID,
    extension_persistent_component,
)
from loguru._logger import Logger

from utils import api_request, lengthen_url, raweb, request_raw_image, translate

newline = "\n"

target_lang = {
    "Bulgarian": "BG",
    "Czech": "CS",
    "Danish": "DA",
    "German": "DE",
    "Greek": "EL",
    "English": "EN",
    "Spanish": "ES",
    "Estonian": "ET",
    "Finnish": "FI",
    "French": "FR",
    "Hungarian": "HU",
    "Indonesian": "ID",
    "Italian": "IT",
    "Japanese": "JA",
    "Lithuanian": "LT",
    "Latvian": "LV",
    "Dutch": "NL",
    "Polish": "PL",
    "Portuguese": "PT",
    "Romanian": "RO",
    "Russian": "RU",
    "Slovak": "SK",
    "Slovenian": "SL",
    "Swedish": "SV",
    "Turkish": "TR",
    "Ukrainian": "UK",
    "Chinese (simplified)": "ZH",
}

message_target_lang = {
    "Bulgarian": "BG",
    "Czech": "CS",
    "Danish": "DA",
    "German": "DE",
    "Greek": "EL",
    "English": "EN",
    "Spanish": "ES",
    "Finnish": "FI",
    "French": "FR",
    "Hungarian": "HU",
    "Indonesian": "ID",
    "Italian": "IT",
    "Japanese": "JA",
    "Latvian": "LV",
    "Dutch": "NL",
    "Polish": "PL",
    "Portuguese": "PT",
    "Romanian": "RO",
    "Russian": "RU",
    "Slovak": "SK",
    "Slovenian": "SL",
    "Swedish": "SV",
    "Turkish": "TR",
    "Ukrainian": "UK",
    "Chinese (simplified)": "ZH",
}

original_lang = {
    "Bulgarian": "BG",
    "Czech": "CS",
    "Danish": "DA",
    "German": "DE",
    "Greek": "EL",
    "English": "EN",
    "Spanish": "ES",
    "Estonian": "ET",
    "Finnish": "FI",
    "French": "FR",
    "Hungarian": "HU",
    "Indonesian": "ID",
    "Italian": "IT",
    "Japanese": "JA",
    "Lithuanian": "LT",
    "Latvian": "LV",
    "Dutch": "NL",
    "Polish": "PL",
    "Portuguese": "PT",
    "Romanian": "RO",
    "Russian": "RU",
    "Slovak": "SK",
    "Slovenian": "SL",
    "Swedish": "SV",
    "Turkish": "TR",
    "Ukrainian": "UK",
    "Chinese": "ZH",
}

temp = {
    "c": "°C",
    "f": "°F",
    "k": "K",
}


class fun(PersistenceExtension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.logger: Logger = kwargs.get("logger")
        self.db = kwargs.get("db")
        self._say = self.db.say
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

    def ttt_btn(self, value, index, disabled):
        match value:
            case 0:
                return Button(
                    style=ButtonStyle.SECONDARY,
                    label=" ",
                    custom_id=str(PersistentCustomID(self.client, "ttt-button", index)),
                    disabled=disabled,
                )
            case 1:
                disabled = True
                return Button(
                    style=ButtonStyle.DANGER,
                    label="X",
                    custom_id=str(PersistentCustomID(self.client, "ttt-button", index)),
                    disabled=disabled,
                )
            case 2:
                disabled = True
                return Button(
                    style=ButtonStyle.SUCCESS,
                    label="O",
                    custom_id=str(PersistentCustomID(self.client, "ttt-button", index)),
                    disabled=disabled,
                )
            case _:
                raise ValueError("Invalid value")

    def win(self, board, player):
        wincond = [
            [board[0][0], board[0][1], board[0][2]],
            [board[1][0], board[1][1], board[1][2]],
            [board[2][0], board[2][1], board[2][2]],
            [board[0][0], board[1][0], board[2][0]],
            [board[0][1], board[1][1], board[2][1]],
            [board[0][2], board[1][2], board[2][2]],
            [board[0][0], board[1][1], board[2][2]],
            [board[2][0], board[1][1], board[0][2]],
        ]
        return [player, player, player] in wincond

    def build_board(self, current=None, update=None):
        p1win = False
        p2win = False
        tie = False
        build = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        if current:
            available = []
            for i in range(3):
                for j in range(3):
                    match current[i].components[j].label:
                        case "O":
                            build[i][j] = 2
                        case "X":
                            build[i][j] = 1
                        case _:
                            available.append([i, j])
            if update in [1, 2, 3]:
                row = 0
                col = update - 1
            elif update in [4, 5, 6]:
                row = 1
                col = update - 4
                build[1][update - 4] = 1
            elif update in [7, 8, 9]:
                row = 2
                col = update - 7
            build[row][col] = 1
            available.remove([row, col])
            p1win = self.win(build, 1)
            if not p1win and len(available) == 0:
                tie = True
            if not p1win and not tie:
                i, j = choice(available)
                build[i][j] = 2
                p2win = self.win(build, 2)
                if not p2win and len(available) == 1:
                    tie = True
        ended = True if p1win or p2win or tie else False
        return (
            [
                ActionRow(
                    components=[
                        self.ttt_btn(build[0][0], 1, ended),
                        self.ttt_btn(build[0][1], 2, ended),
                        self.ttt_btn(build[0][2], 3, ended),
                    ]
                ),
                ActionRow(
                    components=[
                        self.ttt_btn(build[1][0], 4, ended),
                        self.ttt_btn(build[1][1], 5, ended),
                        self.ttt_btn(build[1][2], 6, ended),
                    ]
                ),
                ActionRow(
                    components=[
                        self.ttt_btn(build[2][0], 7, ended),
                        self.ttt_btn(build[2][1], 8, ended),
                        self.ttt_btn(build[2][2], 9, ended),
                    ]
                ),
            ],
            p1win,
            p2win,
            tie,
        )

    @extension_command()
    async def tictactoe(self, ctx: CommandContext):
        """和我來玩一場圈圈叉叉遊戲！"""
        await ctx.defer()
        await ctx.send("遊戲開始了！你先放吧！", components=self.build_board()[0])

    @extension_persistent_component("ttt-button")
    async def ttt_button(self, ctx: ComponentContext, package):
        if ctx.author.id != ctx.message.interaction.user.id:
            return await ctx.send(":x: baka 這不是你的遊戲啦！", ephemeral=True)
        await ctx.defer(edit_origin=True)
        board, p1win, p2win, tie = self.build_board(ctx.message.components, package)
        if p1win:
            await ctx.edit("你贏了！", components=board)
        elif p2win:
            await ctx.edit("你輸了！不用灰心喔，再來一遍就好了！", components=board)
        elif tie:
            await ctx.edit("是平手！", components=board)
        else:
            await ctx.edit("到你了喔！", components=board)

    @extension_command()
    @option("數值")
    @option(
        "原始單位",
        name="from",
        choices=[
            Choice(name="攝氏", value="c"),
            Choice(name="華氏", value="f"),
            Choice(name="克耳文", value="k"),
        ],
    )
    @option(
        "目標單位",
        choices=[
            Choice(name="攝氏", value="c"),
            Choice(name="華氏", value="f"),
            Choice(name="克耳文", value="k"),
        ],
    )
    async def temp(self, ctx: CommandContext, value: float, _from: str, to: str):
        """幫你轉換溫度單位"""
        if _from == to:
            return await ctx.send("baka 你輸入了相同的單位啦！")
        if _from not in ["c", "f", "k"] or to not in ["c", "f", "k"]:
            return await ctx.send("baka 你輸入的單位無效啦！")
        match _from:
            case "c":
                if to == "f":
                    result = value * 9 / 5 + 32
                elif to == "k":
                    result = value + 273.15
            case "f":
                if to == "c":
                    result = (value - 32) * 5 / 9
                elif to == "k":
                    result = (value + 459.67) * 5 / 9
            case "k":
                if to == "c":
                    result = value - 273.15
                elif to == "f":
                    result = value * 9 / 5 - 459.67
        await ctx.send(f"**{round(value, 2)}**{temp[_from]} 等於 **{round(result, 2)}**{temp[to]} 喔！")

    @extension_command(
        dm_permission=False, default_member_permissions=Permissions.MANAGE_EMOJIS_AND_STICKERS
    )
    @option("要偷取的表情符號")
    async def steal(self, ctx: CommandContext, emoji: str):
        """偷取其他伺服器的表情符號"""
        await ctx.defer()
        match = re.findall(r"<(a)?:([^: ]+):([0-9]+)>", emoji)
        if not match:
            return await ctx.send(":x: baka 你只能夠偷取自訂表情符號啦！")
        if len(match) > 1:
            return await ctx.send(":x: baka 可以不要那麼貪心嗎？")
        await ctx.get_guild()
        ext = "gif" if match[0][0] == "a" else "png"
        name = match[0][1]
        _id = int(match[0][2])
        if _id in [int(e.id) for e in ctx.guild.emojis]:
            return await ctx.send(":x: baka 這個伺服器已經有這個表情符號了啦！")
        url = f"https://cdn.discordapp.com/emojis/{_id}.{ext}"
        img = await request_raw_image(url)
        if not img:
            return await ctx.send(":x: baka 這個表情符號不存在啦！")
        try:
            result = await ctx.guild.create_emoji(
                image=Image(file=f"{name}.{ext}", fp=img), name=name
            )
        except LibraryException:
            return await ctx.send(":x: 我無法將這個表情符號新增到這個伺服器！\n(可能是因為我沒有權限，或者是這個伺服器的表情符號數量已達上限)")
        await ctx.send(f"成功偷取表情符號 {result}！")

    @extension_command()
    @option("要加長的連結")
    @option("模式", choices=[Choice(name=i, value=i) for i in ["a", "o"]])
    async def lengthen(self, ctx: CommandContext, url: str, mode: str = "o"):
        """連結太短？加長一下吧！"""
        url = lengthen_url(url, mode)
        if not url:
            return await ctx.send(":x: baka 你輸入的不是連結啦！", ephemeral=True)
        if url == 1:
            return await ctx.send(":x: baka 你不可以重複加長啦！", ephemeral=True)
        if len(url) > 4090:
            return await ctx.send(":x: 連結太長了我記不住！><", ephemeral=True)
        await ctx.send(embeds=raweb("你的超長連結準備好了！", f"```{url}```"))

    @extension_command()
    @option("要翻譯的文字", max_length=128)
    @option("目標語言", autocomplete=True)
    @option("原始語言 (留空為自動偵測)", autocomplete=True)
    async def translate(self, ctx: CommandContext, text: str, target: str, original: str = ""):
        """我來幫你翻譯吧！"""
        await ctx.defer(ephemeral=True)
        resp, lang = await translate(text, target, original)
        if resp == 429:
            return await ctx.send(":x: 對不起！我被伺服器限制速率啦！ ><")
        elif resp == 456:
            return await ctx.send(":x: 對不起！我這個月的翻譯限額用盡了！ ><")
        else:
            await ctx.send(
                embeds=Embed(
                    title="翻譯結果",
                    description=f"[未能完整顯示的翻譯內容](<https://www.deepl.com/translator#{lang}/{target}/{text}>)"
                    if len(resp) > 1024
                    else "",
                    fields=[
                        EmbedField(name="原文", value=text, inline=False),
                        EmbedField(
                            name="翻譯",
                            value=resp if len(resp) <= 1024 else f"{resp[:1021]}...",
                            inline=False,
                        ),
                    ],
                    color=randint(0, 0xFFFFFF),
                    footer=EmbedFooter(
                        text=f"DeepL 翻譯 {[k for k, v in original_lang.items() if v == lang][0] if original_lang != '' else '自動偵測'} → {[k for k, v in target_lang.items() if v == target][0]}"
                    ),
                )
            )

    @extension_message_command(
        name="偷取貼圖", default_member_permissions=Permissions.MANAGE_EMOJIS_AND_STICKERS
    )
    async def steal_sticker(self, ctx: CommandContext):
        await ctx.defer(ephemeral=True)
        if not ctx.target.sticker_items:
            return await ctx.send(":x: baka 這個訊息沒有貼圖啦！")
        if ctx.target.sticker_items[0].format_type == 3:
            return await ctx.send(":x: baka 你只能偷取自訂貼圖啦！(無法偷取 LOTTIE 格式的貼圖)")
        await ctx.get_guild()
        image = await request_raw_image(
            f"https://media.discordapp.net/stickers/{ctx.target.sticker_items[0].id}.png"
        )
        if not image:
            return await ctx.send(":x: baka 你只能偷取自訂貼圖啦！")
        try:
            # FIXME: This version of the lib will cause an error when creating a sticker, therefore doing it manually
            data = aiohttp.FormData()
            data.add_field("file", image, filename="sticker.png", content_type="image/png")
            data.add_field("name", ctx.target.sticker_items[0].name)
            data.add_field("tags", ctx.target.sticker_items[0].name.split(" ")[0])
            async with aiohttp.ClientSession() as s, s.post(
                f"https://discord.com/api/v10/guilds/{ctx.guild_id}/stickers",
                headers={"Authorization": f"Bot {self.client._token}"},
                data=data,
            ) as r:
                result = await r.json()
                if "message" in result:
                    raise LibraryException(code=13)
        except LibraryException:
            return await ctx.send(":x: 我無法將這個貼圖新增到這個伺服器！\n(可能是因為我沒有權限，或者是這個伺服器的貼圖數量已達上限)")
        await ctx.send("成功偷取貼圖！")

    @extension_message_command(name="翻譯文字")
    async def message_translate(self, ctx: CommandContext):
        if ctx.target.content == "":
            return await ctx.send(":x: 對不起！我沒有看到任何文字！ ><", ephemeral=True)
        if len(ctx.target.content) > 128:
            return await ctx.send(":x: 對不起！文字太長了我記不住！ ><", ephemeral=True)
        components = [
            SelectMenu(
                custom_id=str(
                    PersistentCustomID(
                        self.client,
                        "message_translate",
                        [str(ctx.target.id), str(ctx.target.channel_id)],
                    )
                ),
                options=[SelectOption(label=k, value=v) for k, v in message_target_lang.items()],
                placeholder="告訴我吧！",
                min_values=1,
                max_values=1,
            )
        ]
        await ctx.send(embeds=raweb("我來幫你翻譯了！你想翻譯到什麼語言？"), components=components, ephemeral=True)

    @extension_persistent_component("message_translate")
    async def _message_translate(self, ctx: ComponentContext, package, selected=None):
        await ctx.defer(edit_origin=True)
        target = selected[0] or ctx.data.values[0]
        text = (
            await get(self.client, Message, object_id=int(package[0]), parent_id=int(package[1]))
        ).content
        resp, lang = await translate(text, target)
        if resp == 429:
            return await ctx.edit(":x: 對不起！我被伺服器限制速率啦！ ><", components=[], ephemeral=True)
        elif resp == 456:
            return await ctx.edit(":x: 對不起！我這個月的翻譯限額用盡了！ ><", components=[], ephemeral=True)
        else:
            await ctx.edit(
                embeds=Embed(
                    title="翻譯結果",
                    description=f"[未能完整顯示的翻譯內容](<https://www.deepl.com/translator#{lang}/{target}/{text}>)"
                    if len(resp) > 1024
                    else "",
                    fields=[
                        EmbedField(name="原文", value=text, inline=False),
                        EmbedField(
                            name="翻譯",
                            value=resp if len(resp) <= 1024 else f"{resp[:1021]}...",
                            inline=False,
                        ),
                    ],
                    color=randint(0, 0xFFFFFF),
                    footer=EmbedFooter(
                        text=f"DeepL 翻譯 {[k for k, v in original_lang.items() if v == lang][0] if lang != '' else '自動偵測'} → {[k for k, v in message_target_lang.items() if v == target][0]}"
                    ),
                ),
                components=[],
            )

    @extension_command()
    @option("要尋找的截圖", type=OptionType.ATTACHMENT)
    async def whatanime(self, ctx: CommandContext, image: Attachment):
        """忘記了這是哪部動畫的截圖嗎？"""
        await ctx.defer()
        if "image" not in image.content_type:
            return await ctx.send(":x: baka 你只能上傳圖片！", ephemeral=True)
        url = await api_request(f"https://api.trace.moe/search?url={quote_plus(image.url)}")
        if url == 429:
            return await ctx.send(":x: 對不起！我被伺服器限制速率啦！ ><", ephemeral=True)
        if url["result"][0]["similarity"] < 0.85:
            return await ctx.send(":x: 對不起！我找不到截圖的來源！><", ephemeral=True)
        async with aiohttp.ClientSession() as s, s.post(
            "https://trace.moe/anilist/",
            json={
                "query": "query ($id: Int) {Media (id: $id, type: ANIME) {id\nsiteUrl\ntitle {native}}}",
                "variables": {"id": url["result"][0]["anilist"]},
            },
        ) as r:
            resp = await r.json()
        async with aiohttp.ClientSession() as s, s.get(f"{url['result'][0]['image']}&size=l") as r:
            preview = BytesIO(await r.content.read())
        await ctx.send(
            embeds=Embed(
                title=f"{resp['data']['Media']['title']['native']}",
                description=f"中文標題: {resp['data']['Media']['title']['chinese'] or '未知'}{newline}集數: {url['result'][0]['episode'] or '未知/無'}{newline}時間: {timedelta(seconds=int(url['result'][0]['from']))} - {timedelta(seconds=int(url['result'][0]['to']))}{newline}相似度: {url['result'][0]['similarity'] * 100:.2f}%",
                image=EmbedImageStruct(url="attachment://preview.jpg"),
                footer=EmbedFooter(text="資料由 trace.moe 提供"),
                url=resp["data"]["Media"]["siteUrl"],
                color=randint(0, 0xFFFFFF),
            ),
            files=File(filename="preview.jpg", fp=preview),
        )

    @extension_command(name="8ball")
    @option("你想問的問題")
    async def _8ball(self, ctx: CommandContext, question: str):
        """問問神奇8號球的答案？"""
        await ctx.defer()
        resp = eval(
            choice(
                [
                    '"是？"',
                    '"我覺得是了啦"',
                    '"我覺得毫無疑問肯定是！"',
                    'f"我感覺應該 {randint(0,100)}% 是"',
                    '"我也不太清楚"',
                    '"不是？"',
                    '"我覺得不是欸"',
                    '"我覺得完全不是"',
                    'f"我覺得 {randint(0,100)}% 不是"',
                ]
            )
        )
        await ctx.send(embeds=raweb(f"問題: {question}", f"{resp}"))

    @extension_command()
    @option("搜尋的內容", required=True)
    async def lmgtfy(self, ctx: CommandContext, search: str):
        """Let me Google that for you."""
        await ctx.send(f"Google搜尋: [連結](<https://letmegooglethat.com/?q={search}>)")

    @extension_command()
    @option("從", min_value=0)
    @option("到", min_value=0)
    async def random(self, ctx: CommandContext, min: int, max: int):
        """隨機產生一個數字"""
        await ctx.defer()
        if min == max:
            return await ctx.send(":x: baka 只有一個數字要我怎麼選！", ephemeral=True)
        if min > max:
            min, max = max, min
        result = randint(min, max)
        await ctx.send(embeds=raweb(f"你要我選一個 {min} 到 {max} 的數字嗎？", f"那... 我選 **{result}**！"))

    @extension_command()
    async def unknown(self, ctx: CommandContext):
        """一個野生的指令出現了！"""
        await ctx.send(
            embeds=raweb(
                desc="這個指令不存在喔！",
                image=EmbedImageStruct(
                    url="https://media.tenor.com/x8v1oNUOmg4AAAAM/rickroll-roll.gif"
                ),
            ),
            ephemeral=True,
        )

    @extension_command()
    @option("要我說的話")
    @option("要回覆的訊息ID")
    async def say(self, ctx: CommandContext, text: str, reply: str = None):
        """讓我代替你說一句話吧！"""
        if reply:
            try:
                ref = await get(
                    self.client, Message, object_id=int(reply), parent_id=ctx.channel_id
                )
            except Exception:
                return await ctx.send(":x: 我找不到要回覆的訊息喔！", ephemeral=True)
            msg = await ref.reply(
                embeds=raweb(
                    "那我要說出來了！",
                    text,
                    footer=EmbedFooter(text="這句話不是我要說的喔！管理員可以使用 /whosay 來查看要我說的人！"),
                ),
                allowed_mentions=AllowedMentions(everyone=False, roles=False, users=False),
            )
        else:
            msg = await ctx.channel.send(
                embeds=raweb(
                    "那我要說出來了！",
                    text,
                    footer=EmbedFooter(text="這句話不是我要說的喔！管理員可以使用 /whosay 來查看要我說的人！"),
                ),
                allowed_mentions=AllowedMentions(everyone=False, roles=False, users=False),
            )
        await ctx.send("好了~", ephemeral=True)
        await self._say.insert_one(
            {
                "_id": int(msg.id),
                "user": int(ctx.user.id),
                "guild": int(ctx.guild.id),
                "expires": datetime.now(timezone.utc) + timedelta(days=7),
            }
        )

    @extension_command(dm_permission=False, default_member_permissions=Permissions.ADMINISTRATOR)
    @option("要查詢的訊息 ID")
    async def whosay(self, ctx: CommandContext, msg_id: int):
        """查詢是誰讓我說話"""
        await ctx.defer(ephemeral=True)
        data = await self._say.find_one({"_id": msg_id})
        if not data:
            return await ctx.send(":x: 這句話不是別人要我說的喔！又或者我已經忘掉了(只能尋找7天以內的訊息)...")
        elif data["guild"] != int(ctx.guild.id):
            return await ctx.send(":x: 這句話不是在這個伺服器說的喔！")
        user = await get(self.client, User, object_id=data["user"])
        await ctx.send(f"這句話是 {user.username}#{user.discriminator} 要我說的喔！")

    @extension_command(name="google-tutorial")
    @option(
        "選擇文件語言",
        choices=[
            Choice(name="中文（繁體）", value="zh-Hant"),
            Choice(name="中文（简体）", value="zh-Hans"),
            Choice(name="English", value="en"),
            Choice(name="日本語", value="ja"),
        ],
    )
    async def googletutorial(self, ctx: CommandContext, language: str = "zh-Hant"):
        """我來教你怎麼用Google！"""
        if language not in ["zh-Hant", "zh-Hans", "en", "ja"]:
            language = "zh-Hant"
        await ctx.send(
            f"Google搜尋教學: [連結](https://support.google.com/websearch/answer/134479?hl={language})"
        )

    @extension_autocomplete(command="translate", name="target")
    async def _target(self, ctx: CommandContext, target: str = ""):
        langs = list(target_lang.keys())
        if not (letters := list(target) if target != "" else []):

            await ctx.populate(
                [
                    Choice(name=i, value=target_lang[i])
                    for i in (langs[:24] if len(langs) > 25 else langs)
                ]
            )
        else:
            choices: list = []
            focus: str = "".join(letters)
            for i in langs:
                if focus.lower() in i.lower() and len(choices) < 26:
                    choices.append(Choice(name=i, value=target_lang[i]))
                elif len(choices) >= 26:
                    break
            await ctx.populate(choices)

    @extension_autocomplete(command="translate", name="original")
    async def _original(self, ctx: CommandContext, target: str = ""):
        langs = list(original_lang.keys())
        if not (letters := list(target) if target != "" else []):

            await ctx.populate(
                [
                    Choice(name=i, value=original_lang[i])
                    for i in (langs[:24] if len(langs) > 25 else langs)
                ]
            )
        else:
            choices: list = []
            focus: str = "".join(letters)
            for i in langs:
                if focus.lower() in i.lower() and len(choices) < 26:
                    choices.append(Choice(name=i, value=original_lang[i]))
                elif len(choices) >= 26:
                    break
            await ctx.populate(choices)


def setup(client, **kwargs):
    fun(client, **kwargs)
