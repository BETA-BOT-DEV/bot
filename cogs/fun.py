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
from datetime import datetime, timedelta
from io import BytesIO
from random import choice, randint
from urllib.parse import quote_plus

import aiohttp
from interactions import (
    AllowedMentions,
    Attachment,
    Channel,
    ChannelType,
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

from utils import api_request, lengthen_url, raweb, requset_raw_img, translate

newline = "\n"

# https://gist.github.com/GeneralSadaf/42d91a2b6a93a7db7a39208f2d8b53ad
free_activity = {
    "Watch Together": 880218394199220334,
    "Betrayal.io": 773336526917861400,
    "Fishington.io": 814288819477020702,
    "Sketch Heads": 902271654783242291,
    "Word Snacks": 879863976006127627,
}

activities = {
    "Watch Together": 880218394199220334,
    "Betrayal.io": 773336526917861400,
    "Fishington.io": 814288819477020702,
    "Sketch Heads": 902271654783242291,
    "Word Snacks": 879863976006127627,
    "Poker Night": 755827207812677713,
    "Chess in the Park": 832012774040141894,
    "Letter League": 879863686565621790,
    "SpellCast": 852509694341283871,
    "Checkers In The Park": 832013003968348200,
    "Blazing 8s": 832025144389533716,
    "Putt Party": 945737671223947305,
    "Land-io": 903769130790969345,
    "Booble League": 947957217959759964,
    "Ask Away": 976052223358406656,
    "Know What I Meme": 950505761862189096,
    "Bash Out": 1006584476094177371,
}

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


class fun(PersistenceExtension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.logger: Logger = kwargs.get("logger")
        self.db = kwargs.get("db")
        self._say = self.db.say
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

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
        id = int(match[0][2])
        if id in [int(e.id) for e in ctx.guild.emojis]:
            return await ctx.send(":x: baka 這個伺服器已經有這個表情符號了啦！")
        url = f"https://cdn.discordapp.com/emojis/{id}.{ext}"
        img = await requset_raw_img(url)
        if not img:
            return await ctx.send(":x: baka 這個表情符號不存在啦！")
        result = await ctx.guild.create_emoji(image=Image(file=f"{name}.{ext}", fp=img), name=name)
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
        resp, lang = await translate(text, target, original)
        if resp == 429:
            return await ctx.send(":x: 對不起！我被伺服器限制速率啦！ ><", ephemeral=True)
        elif resp == 456:
            return await ctx.send(":x: 對不起！我這個月的翻譯限額用盡了！ ><", ephemeral=True)
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
                            value=resp if len(resp) <= 1024 else resp[:1021] + "...",
                            inline=False,
                        ),
                    ],
                    color=randint(0, 0xFFFFFF),
                    footer=EmbedFooter(
                        text=f"DeepL 翻譯 {[k for k, v in original_lang.items() if v == lang][0] if original_lang != '' else '自動偵測'} → {[k for k, v in target_lang.items() if v == target][0]}"
                    ),
                )
            )

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
                            value=resp if len(resp) <= 1024 else resp[:1021] + "...",
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
                description=f"中文標題: {resp['data']['Media']['title']['chinese'] if resp['data']['Media']['title']['chinese'] else '未知'}{newline}集數: {url['result'][0]['episode'] if url['result'][0]['episode'] else '未知/無'}{newline}時間: {timedelta(seconds=int(url['result'][0]['from']))} - {timedelta(seconds=int(url['result'][0]['to']))}{newline}相似度: {url['result'][0]['similarity'] * 100:.2f}%",
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
            except:  # noqa: E722
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
                "expires": datetime.utcnow() + timedelta(days=7),
            }
        )

    @extension_command(dm_permission=False, default_member_permissions=Permissions.ADMINISTRATOR)
    @option("要查詢的訊息 ID")
    async def whosay(self, ctx: CommandContext, msg_id: str):
        """查詢是誰讓我說話"""
        await ctx.defer(ephemeral=True)
        data = await self._say.find_one({"_id": int(msg_id)})
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

    @extension_command(dm_permission=False)
    @option("要開始活動的頻道", channel_types=[ChannelType.GUILD_VOICE])
    @option("要開始的活動", autocomplete=True)
    async def together(self, ctx: CommandContext, channel: Channel, activity: str):
        if activity not in activities:
            return await ctx.send(":x: baka 這個活動不存在！", ephemeral=True)
        await ctx.get_guild()
        if not (
            await channel.get_permissions_for(ctx.guild.get_member(self.client.me.id))
        ).CREATE_INSTANT_INVITE:
            return await ctx.send(":x: 我沒有權限在這個頻道開始活動 ;-;", ephemeral=True)
        await ctx.send(
            embeds=raweb(
                desc="我已經忘掉這個技能了！\n(這個功能已停用: [Discord 已正式發布此功能](<https://discord.com/blog/server-activities-games-voice-watch-together>))"
            )
        )

    @extension_autocomplete(command="together", name="activity")
    async def _together(self, ctx: CommandContext, activity: str = ""):
        a = (
            list(free_activity.keys())
            if not ctx.guild or ctx.guild.premium_tier == 0
            else list(activities.keys())
        )
        if not (letters := list(activity) if activity != "" else []):
            await ctx.populate([Choice(name=i, value=i) for i in (a[:24] if len(a) > 25 else a)])
        else:
            choices: list = []
            focus: str = "".join(letters)
            for i in a:
                if focus.lower() in i.lower() and len(choices) < 26:
                    choices.append(Choice(name=i, value=i))
                elif len(choices) >= 26:
                    break
            await ctx.populate(choices)

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
