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

import binascii
import contextlib
import os
import re
from base64 import b64decode
from datetime import datetime, timezone
from enum import Enum

import aiohttp
import decouple
from interactions import (
    ChannelType,
    Client,
    CommandContext,
    Embed,
    EmbedField,
    EmbedFooter,
    Extension,
    LibraryException,
    Message,
    Permissions,
    Role,
    extension_command,
    extension_listener,
    get,
)
from loguru._logger import Logger

from utils import raweb

newline = "\n"

url_regex = re.compile(
    r"(http|https)(:\/\/)([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"
)


class threatType(Enum):
    THREAT_TYPE_UNSPECIFIED = "未知"
    MALWARE = "惡意程式"
    SOCIAL_ENGINEERING = "社會工程"
    UNWANTED_SOFTWARE = "潛在附加軟件"
    POTENTIALLY_HARMFUL_APPLICATION = "潛在有害程式"


class platformType(Enum):
    PLATFORM_TYPE_UNSPECIFIED = "未知"
    WINDOWS = "Windows"
    LINUX = "Linux"
    ANDROID = "Android"
    OSX = "MacOS X"
    IOS = "iOS"
    ANY_PLATFORM = "所有平台"
    ALL_PLATFORM = "所有平台"
    CHROME = "Chrome"


class protect(Extension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.logger: Logger = kwargs.get("logger")
        self.version = kwargs.get("version")
        self.db = kwargs.get("db")
        self._ping = self.db.ping
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

    # TEST: http://malware.testing.google.test/testing/malware/*
    @extension_listener(name="on_message_create")
    async def link_check(self, message: Message):
        if (await message.get_channel()).type == ChannelType.DM:
            return
        if message.content:
            if linklist := url_regex.findall(message.content):
                # api lookup
                async with aiohttp.ClientSession() as s, s.post(
                    f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={decouple.config('googleapi')}",
                    headers={"Content-Type": "application/json"},
                    data=str(
                        {
                            "client": {"clientId": "BETA BOT", "clientVersion": self.version},
                            "threatInfo": {
                                "threatTypes": [
                                    "MALWARE",
                                    "SOCIAL_ENGINEERING",
                                    "UNWANTED_SOFTWARE",
                                    "POTENTIALLY_HARMFUL_APPLICATION",
                                ],
                                "platformTypes": ["ANY_PLATFORM"],
                                "threatEntryTypes": ["URL"],
                                "threatEntries": [
                                    {"url": i} for i in [*{"".join(i) for i in linklist}]
                                ],
                            },
                        }
                    ),
                ) as r:
                    resp = await r.json()
                if "matches" in resp:
                    await message.reply(
                        embeds=Embed(
                            title="找到可能有害的連結了！",
                            description="資料僅供參考，未必完全準確，請自行注意連結是否安全喔！",
                            fields=[
                                EmbedField(
                                    name=f"url: ||<{i['threat']['url']}>||",
                                    value=f"威脅類別: {threatType[i['threatType']].value}\n受影響範圍: {platformType[i['platformType']].value}",
                                    inline=False,
                                )
                                for i in resp["matches"]
                            ],
                            footer=EmbedFooter(text="Google Safe Browsing API"),
                            timestamp=datetime.now(timezone.utc),
                        )
                    )

    @extension_listener(name="on_message_create")
    async def token_check(self, message: Message):
        if (await message.get_channel()).type == ChannelType.DM:
            return
        possible = list(
            re.findall(
                r"[a-zA-Z0-9_-]{23,28}\.[a-zA-Z0-9_-]{6,7}\.[a-zA-Z0-9_-]{27,}", message.content
            )
        )

        for token in possible:
            try:
                validate = b64decode(token.split(".")[0] + "==", validate=True)
            except binascii.Error:
                continue
            else:
                if validate.isdigit():
                    try:
                        await message.delete()
                    except LibraryException:
                        with contextlib.suppress(LibraryException):
                            await message.reply(
                                message.author.mention,
                                embeds=raweb(
                                    "發現TOKEN！",
                                    "你的訊息包含了Discord的TOKEN，但我沒有適當的權限為你刪除!\n為安全起見請前往 [Discord Developer Portal](<https://discord.com/developers/applications>) 進行重設。",
                                ),
                            )
                    else:
                        with contextlib.suppress(LibraryException):
                            await (await message.get_channel()).send(
                                message.author.mention,
                                embeds=raweb(
                                    "發現TOKEN！",
                                    "你的訊息包含了Discord的TOKEN，我已經為你刪除了!\n為安全起見請前往 [Discord Developer Portal](<https://discord.com/developers/applications>) 進行重設。",
                                ),
                            )
                    finally:
                        break

    @extension_listener(name="on_message_create")
    async def ping_check(self, message: Message):
        if (await message.get_channel()).type == ChannelType.DM:
            return
        if not (message.mention_everyone or message.mentions):
            return
        try:
            guild = await message.get_guild()
            channel = await message.get_channel()
            permissions = await channel.get_permissions_for(message.member)
        except Exception:
            return
        if channel.type == ChannelType.DM:
            return
        pinged = []
        if message.mention_everyone and (
            Permissions.MENTION_EVERYONE in permissions or message.author.id == guild.owner_id
        ):
            for i in guild.members:
                if not i.user.bot and i.user.id != message.author.id and int(i.id) not in pinged:
                    pinged.append(int(i.id))
        if message.mentions:
            for i in message.mentions:
                if (
                    ("bot" not in i or not i["bot"])
                    and int(i["id"]) not in pinged
                    and i["id"] != str(message.author.id)
                ):
                    pinged.append(int(i["id"]))
        for i in pinged:
            await self._ping.replace_one(
                {"user_id": i, "guild_id": int(guild.id)},
                {
                    "user_id": int(i),
                    "guild_id": int(guild.id),
                    "author": int(message.author.id),
                    "create": datetime.now(timezone.utc),
                },
                upsert=True,
            )

    @extension_command(dm_permission=False)
    async def whopinged(self, ctx: CommandContext):
        """尋找12小時內最後在這個伺服器@你的人"""
        await ctx.defer(ephemeral=True)
        doc = await self._ping.find_one(
            {"user_id": int(ctx.author.id), "guild_id": int(ctx.guild_id)},
            {"_id": 0, "author": 1, "create": 1},
        )
        if not doc:
            return await ctx.send(":x: baka 最近12小時沒有人在這個伺服器@過你 (@role 暫不適用)")
        author = "我啦" if doc["author"] == int(self.client.me.id) else f" <@{doc['author']}>"
        await ctx.send(
            embeds=raweb(
                "找到了！",
                f"最後一次在這個伺服器@你的人是{author}\nUTC時間是 {doc['create'].strftime('%Y-%m-%d %H:%M:%S')}",
            )
        )

    @extension_listener()
    async def on_message_delete(self, message: Message):
        if (
            not message.author
            or message.author.id == self.client.me.id
            or (not message.mentions and not message.mention_everyone and not message.mention_roles)
            or (await message.get_channel()).type == ChannelType.DM
        ):
            return
        roles = []
        victims = []
        everyone = bool(
            message.mention_everyone
            and await message.member.has_permissions(Permissions.MENTION_EVERYONE)
        )
        if message.mention_roles:
            for i in message.mention_roles:
                role = await get(self.client, Role, object_id=int(i), parent_id=message.guild_id)
                if not role.managed:
                    roles.append(f"<@&{i}>")
        if message.mentions:
            victims.extend(
                f"<@{i['id']}>"
                for i in message.mentions
                if ("bot" not in i or not i["bot"]) and i["id"] != str(message.author.id)
            )
        if not victims and not roles and not everyone:
            return
        content = ""
        if everyone:
            content = "@everyone"
        else:
            content = ""
            if roles:
                content += "身份組: \n"
                content += "\n".join(roles)
            if victims:
                if content != "":
                    content += "\n\n"
                content += "成員: \n"
                content += "\n".join(victims)
        channel = await message.get_channel()
        with contextlib.suppress(LibraryException):
            await channel.send(
                embeds=raweb(
                    "抓到 Ghost Ping 了！",
                    desc=f"{message.author.mention} 這樣可不行喔！\n以下的受害者被Ghost ping了...\n\n{content}",
                )
            )

    @extension_command(default_member_permissions=Permissions.ADMINISTRATOR, dm_permission=False)
    async def safety(self, *args, **kwargs):
        ...

    @safety.subcommand()
    async def check(self, ctx: CommandContext):
        """進行伺服器安全性檢查"""
        await ctx.defer()
        await ctx.get_guild()
        everyone = await ctx.guild.get_role(ctx.guild_id)
        admin = (
            ":warning: 預設身份組擁有管理員權限 (建議：停用相關權限)"
            if int(everyone.permissions) & Permissions.ADMINISTRATOR
            else ":ballot_box_with_check: 預設身份組權限 (管理員)"
        )
        mention = (
            ":warning: 預設身份組擁有提及全部人的權限 (建議：停用相關權限)"
            if int(everyone.permissions) & Permissions.MENTION_EVERYONE
            else ":ballot_box_with_check: 預設身份組權限 (提及全部人)"
        )
        verify = (
            ":warning: 伺服器驗證等級為無 (建議：中 或以上)"
            if ctx.guild.verification_level == 0
            else "伺服器驗證等級過低 (建議：中 或以上)"
            if ctx.guild.verification_level == 1
            else ":ballot_box_with_check: 伺服器驗證等級設定"
        )
        mfa = (
            ":warning: 伺服器未啟用兩步驗證 (建議：啟用兩步驗證)"
            if ctx.guild.mfa_level == 0
            else ":ballot_box_with_check: 伺服器兩步驗證設定"
        )
        filters = (
            ":warning: 伺服器未啟用內容過濾 (建議：掃描來自所有使用者的訊息)"
            if ctx.guild.explicit_content_filter == 0
            else ":ballot_box_with_check: 伺服器內容過濾器設定"
        )
        await ctx.send(
            embeds=raweb(
                "伺服器安全性檢查結果",
                f"好了～檢查完了！讓我們繼續一起保持安全的環境吧！\n\n檢查項目：\n{newline.join([admin, mention, verify, mfa, filters])}",
            )
        )


def setup(client, **kwargs):
    protect(client, **kwargs)
