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

from interactions import (
    ActionRow,
    Button,
    ButtonStyle,
    Client,
    CommandContext,
    ComponentContext,
    Extension,
    SelectMenu,
    SelectOption,
    extension_command,
    extension_component,
)
from loguru._logger import Logger

from utils import raweb

newline = "\n"

maineb = raweb(
    "看來你需要一點幫助呢！", "我來告訴你我可以做什麼吧！\n你可以使用下面的選單來瀏覽幫助頁面。\n\n如果你想提出建議或是回報問題，請使用 `/feedback` 指令。"
)

general_option = SelectOption(  # help, info, whopinged, feedback, legal
    label="一般",
    description="一般/資訊指令",
    value="general",
)
image_option = SelectOption(  # image, reaction, generate
    label="圖片",
    description="圖片相關指令",
    value="image",
)
fun_option = SelectOption(  # twitter, typing, say, 8ball, google-tutorial, lengthen, lmgtfy, translate, random, unknown, whatanime, temp
    label="有趣",
    description="各種有趣的指令",
    value="fun",
)
nsfw_option = SelectOption(  # nsfw, hentai
    label="NSFW",
    description="可以色色的指令",
    value="nsfw",
)
admin_option = SelectOption(  # welcome, farewell, moderation, whosay, steal, dvc, safety, thread
    label="管理",
    description="管理指令",
    value="admin",
)


_select = ActionRow(
    components=[
        SelectMenu(
            custom_id="help_select",
            placeholder="選擇一個類別",
            options=[general_option, image_option, fun_option, nsfw_option, admin_option],
            min_values=1,
            max_values=1,
        )
    ]
)


general_select = ActionRow(
    components=[
        SelectMenu(
            custom_id="help_command_select",
            placeholder="選擇一個指令",
            options=[
                SelectOption(label=i, value=i)
                for i in ["help", "info", "whopinged", "feedback", "legal"]
            ],
            min_values=1,
            max_values=1,
        )
    ]
)
general_embed = raweb(
    "一般指令", "這裡是一般/資訊指令的說明。\n你可以使用下面的選單來瀏覽幫助頁面。\n\n如果你想提出建議或是回報問題，請使用 `/feedback` 指令。"
)
image_select = ActionRow(
    components=[
        SelectMenu(
            custom_id="help_command_select",
            placeholder="選擇一個指令",
            options=[SelectOption(label=i, value=i) for i in ["image", "reaction", "generate"]],
            min_values=1,
            max_values=1,
        )
    ]
)
image_embed = raweb(
    "圖片指令", "這裡是圖片相關指令的說明。\n你可以使用下面的選單來瀏覽幫助頁面。\n\n如果你想提出建議或是回報問題，請使用 `/feedback` 指令。"
)
fun_select = ActionRow(
    components=[
        SelectMenu(
            custom_id="help_command_select",
            placeholder="選擇一個指令",
            options=[
                SelectOption(label=i, value=i)
                for i in [
                    "tictactoe",
                    "say",
                    "8ball",
                    "google-tutorial",
                    "lengthen",
                    "lmgtfy",
                    "translate",
                    "random",
                    "unknown",
                    "whatanime",
                    "twitter",
                    "typing",
                    "temp",
                ]
            ],
            min_values=1,
            max_values=1,
        )
    ]
)
fun_embed = raweb(
    "有趣指令", "這裡是各種有趣的指令的說明。\n你可以使用下面的選單來瀏覽幫助頁面。\n\n如果你想提出建議或是回報問題，請使用 `/feedback` 指令。"
)
nsfw_select = ActionRow(
    components=[
        SelectMenu(
            custom_id="help_command_select",
            placeholder="選擇一個指令",
            options=[SelectOption(label=i, value=i) for i in ["nsfw", "hentai"]],
            min_values=1,
            max_values=1,
        )
    ]
)
nsfw_embed = raweb(
    "NSFW指令",
    "這裡是可以色色的指令的說明。\n你可以使用下面的選單來瀏覽幫助頁面。\n\n**注意：** 這些指令只能在 NSFW 頻道使用。如果你看不到這些指令，請前往 **設定 --> 私隱 & 安全** 打開 顯示限制級指令 選項。同時，管理員可以前往 **伺服器設定 -> 整合-> BETA BOT** 中設定使用權限。\n\n如果你想提出建議或是回報問題，請使用 `/feedback` 指令。",
)
admin_select = ActionRow(
    components=[
        SelectMenu(
            custom_id="help_command_select",
            placeholder="選擇一個指令",
            options=[
                SelectOption(label=i, value=i)
                for i in [
                    "welcome",
                    "farewell",
                    "moderation",
                    "whosay",
                    "steal",
                    "dvc",
                    "safety",
                    "thread",
                ]
            ],
            min_values=1,
            max_values=1,
        )
    ]
)
admin_embed = raweb("管理指令", "這裡是管理指令的說明。\n你可以使用下面的選單來瀏覽幫助頁面。\n\n如果你想提出建議或是回報問題，請使用 `/feedback` 指令。")


def _command(name, description: str = "", usage: str = "", example: str = "", nsfw: bool = False):
    if not description:
        description = "我的主人很懶，沒有留下說明。"
    if not usage:
        usage = "我的主人很懶，沒有留下使用方法。"
    if not example:
        example = "我的主人很懶，沒有留下使用範例。"
    return raweb(
        name,
        f"{description}\n\n**使用方法**\n```{usage}```\n\n**範例**\n```{example}```\n\n{'⚠️ 這個指令可能會有成人內容，請注意。' if nsfw else ''}",
    )


invite = Button(
    style=ButtonStyle.LINK,
    label="邀請我",
    url="https://discord.com/oauth2/authorize?client_id=1030626357669011557&permissions=8&scope=bot&applications.commands",
)
goback = Button(style=ButtonStyle.SECONDARY, label="⬅️ 返回主頁", custom_id="help_goback")


class help(Extension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.logger: Logger = kwargs.get("logger")
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

    @extension_command()
    async def help(self, ctx: CommandContext):
        """需要一點幫助嗎？"""
        await ctx.get_channel()
        await ctx.send(
            embeds=maineb,
            components=[_select, ActionRow(components=[invite])],
            ephemeral=True,
        )

    @extension_component("help_goback")
    async def _help_goback(self, ctx: ComponentContext):
        await ctx.defer(edit_origin=True)
        await ctx.edit(embeds=maineb, components=[_select, ActionRow(components=[invite])])

    @extension_component("help_select")
    async def _help_select(self, ctx: ComponentContext, selected=None):
        await ctx.defer(edit_origin=True)
        match selected[0]:
            case "general":
                menu = general_select
                eb = general_embed
            case "image":
                menu = image_select
                eb = image_embed
            case "fun":
                menu = fun_select
                eb = fun_embed
            case "nsfw":
                menu = nsfw_select
                eb = nsfw_embed
            case "admin":
                menu = admin_select
                eb = admin_embed
            case _:
                raise ValueError("Invalid selection.")
        await ctx.edit(embeds=eb, components=[menu, ActionRow(components=[invite, goback])])

    @extension_component("help_command_select")
    async def _help_command_select(self, ctx: ComponentContext, selected=None):
        await ctx.defer(edit_origin=True)
        cmds = {
            "help": ["顯示幫助訊息。", "/help", "/help", False],
            "info": ["顯示各種資訊。", "/info <子指令> <參數>", f"/info user @{ctx.author.name}", False],
            "whopinged": ["找出過去12小時內最後在這個伺服器@你的人。", "/whopinged", "/whopinged", False],
            "feedback": ["回報問題或是提出建議。", "/feedback", "/feedback", False],
            "image": ["隨機發送各種圖片 (safe for work)。", "/image <圖片類別>", "/image cat", False],
            "reaction": ["以圖片做出回應。", "/reaction <回應類別>", "/reaction sleepy", False],
            "generate": ["隨機生成各種圖片。", "/generate <生成類別> <參數>", "/generate qr hello", False],
            "twitter": ["搜尋Twitter", "/twitter <子指令> <搜尋>", "/twitter user @itsrqtl", False],
            "typing": ["讓我不斷輸入中...", "/typing <子指令>", "/typing start", False],
            "tictactoe": ["和我來玩一場井字遊戲！", "/tictactoe", "", False],
            "say": ["讓我說話。", "/say <內容>", "/say hello", False],
            "8ball": ["問問神奇8號球的答案？", "/8ball <問題>", "/8ball 今天天氣好嗎？", False],
            "google-tutorial": [
                "讓我教你如何使用Google。",
                "/google-tutorial [語言]",
                "/google-tutorial",
                False,
            ],
            "lengthen": ["幫你把網址變長。", "/lengthen <網址>", "/lengthen https://google.com", False],
            "lmgtfy": ["不會google嗎...", "/lmgtfy <搜尋>", "/lmgtfy how to use google", False],
            "translate": [
                "翻譯文字。",
                "/translate <內容> <語言> [原始語言]",
                "/translate hello zh-hant",
                False,
            ],
            "random": ["隨機選擇一個數字。", "/random <min> <max>", "/random 1 100", False],
            "unknown": ["一個野生的指令出現了！", "/unknown", "/unknown", False],
            "whatanime": ["搜尋截圖來源。", "/whatanime <圖片>", "", False],
            "nsfw": ["隨機發送各種NSFW (現實) 圖片。", "/nsfw <圖片類別>", "", True],
            "hentai": ["隨機發送各種Hentai (非現實) 圖片。", "/hentai <圖片類別>", "", True],
            "welcome": ["設定歡迎訊息。", "/welcome", "/welcome", False],
            "farewell": ["設定離開訊息。", "/farewell", "/farewell", False],
            "moderation": [
                "管理使用者。",
                "/moderation <行動> <使用者> [原因]",
                f"/moderation ban @{ctx.author.name}",
                False,
            ],
            "whosay": [
                "根據訊息ID尋找使用 /say 的使用者。",
                "/whosay <訊息ID>",
                f"/whosay {ctx.message.id}",
                False,
            ],
            "steal": ["偷取其他伺服器的表情符號。", "/steal <表情符號>", "/steal <a:cat:123456789>", False],
            "dvc": ["管理動態語音頻道設定。", "/dvc <子指令>", "/dvc settings", False],
            "thread": ["管理貼文或討論串。", "/thread <子指令>", "/thread archive", False],
            "safety": ["伺服器安全指令。", "/safety <子指令>", "/safety check", False],
            "legal": ["查看法律文件。", "/legal <子指令>", "/legal terms", False],
            "temp": ["幫你轉換溫度單位。", "/temp <數值> <原始單位> <目標單位>", "/temp 10 c f", False],
        }
        cmd = cmds[selected[0]]
        eb = _command(selected[0], cmd[0], cmd[1], cmd[2], cmd[3])
        await ctx.edit(embeds=eb, components=ctx.message.components)


def setup(client, **kwargs):
    help(client, **kwargs)
