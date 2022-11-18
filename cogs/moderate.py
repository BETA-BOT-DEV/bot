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
from random import randint

from interactions import (
    ActionRow,
    AuditLogEvents,
    Button,
    ButtonStyle,
    Choice,
    Client,
    CommandContext,
    ComponentContext,
    Embed,
    Guild,
    GuildMember,
    LibraryException,
    Member,
    Message,
    Modal,
    Permissions,
    SelectMenu,
    SelectOption,
    TextInput,
    TextStyleType,
    extension_command,
    extension_component,
    extension_listener,
    extension_modal,
    extension_user_command,
    get,
    option,
)
from interactions.ext.persistence import (
    PersistenceExtension,
    PersistentCustomID,
    extension_persistent_component,
)
from loguru._logger import Logger

newline = "\n"


class moderate(PersistenceExtension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.db = kwargs.get("db")
        self.logger: Logger = kwargs.get("logger")
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

    @extension_listener()
    async def on_guild_member_update(self, before: GuildMember, after: GuildMember):
        if not before or before.name != after.name:
            guild = await get(self.client, Guild, object_id=after.guild_id)
            if after.id == guild.owner_id:
                return
            log = await guild.get_latest_audit_log_action(AuditLogEvents.MEMBER_UPDATE)
            if log.audit_log_entries[0].user_id == self.client.me.id:
                return
            document = await self.db.nick.find_one({"_id": int(after.guild_id)})
            if document:
                if document.get("regex", None):
                    if re.search(document["regex"], after.name):
                        await after.modify(nick="")
                        return
                if document.get("custom", None):
                    for i in document["custom"].splitlines():
                        if i in after.name:
                            await after.modify(nick="")
                            return

    # TODO: consider adding user interactions + rework content
    @extension_command(default_member_permissions=Permissions.ADMINISTRATOR, dm_permission=False)
    async def moderation(self, *args, **kwargs):
        ...

    @moderation.subcommand()
    @option("要刪除的訊息數量", min_value=1)
    async def purge(self, ctx: CommandContext, limit: int):
        """清除訊息"""
        await ctx.defer(ephemeral=True)
        await ctx.get_channel()
        try:
            deleted = await ctx.channel.purge(amount=limit)
        except LibraryException:
            await ctx.send(":x: 有些訊息我刪不掉 ;-;", ephemeral=True)
        else:
            await ctx.send(f"我清除了 {len(deleted)} 條訊息！不過14天之前的訊息我動不了。", ephemeral=True)

    @moderation.subcommand()
    @option("要踢的人")
    @option("原因")
    async def kick(self, ctx: CommandContext, member: Member, reason: str = None):
        """踢出成員"""
        await ctx.defer(ephemeral=True)
        if not ctx.app_permissions.KICK_MEMBERS:
            return await ctx.send(":x: 我沒權限踢人 ;-;", ephemeral=True)
        try:
            await member.kick(ctx.guild_id, reason)
        except LibraryException:
            return await ctx.send(f":x: 我踢不動 {member.mention} ;-;", ephemeral=True)
        else:
            await ctx.send(
                f"我把 {member.user.username}#{member.user.discriminator} 踢出去了！再見！", ephemeral=True
            )

    @extension_user_command(
        name="踢出成員", dm_permission=False, default_member_permissions=Permissions.KICK_MEMBERS
    )
    async def _user_kick(self, ctx: CommandContext):
        await ctx.defer(ephemeral=True)
        if not ctx.app_permissions.KICK_MEMBERS:
            return await ctx.send(":x: 我沒權限踢人 ;-;", ephemeral=True)
        try:
            await ctx.target.kick(ctx.guild_id)
        except LibraryException:
            return await ctx.send(f":x: 我踢不動 {ctx.target.mention} ;-;", ephemeral=True)
        else:
            await ctx.send(
                f"我把 {ctx.target.user.username}#{ctx.target.user.discriminator} 踢出去了！再見！",
                ephemeral=True,
            )

    @moderation.subcommand()
    @option("要封鎖的人")
    @option("原因")
    async def ban(self, ctx: CommandContext, member: Member, reason: str = None):
        """封鎖成員"""
        await ctx.defer(ephemeral=True)
        if not ctx.app_permissions.BAN_MEMBERS:
            return await ctx.send(":x: 我沒權限封鎖其他人 ;-;", ephemeral=True)
        try:
            await member.ban(ctx.guild_id, reason)
        except LibraryException:
            return await ctx.send(f":x: 我封鎖不了 {member.mention} ;-;", ephemeral=True)
        else:
            await ctx.send(
                f"我把 {member.user.username}#{member.user.discriminator} 封鎖了！再見！", ephemeral=True
            )

    @moderation.subcommand()
    @option("要禁言的人")
    @option(
        "禁言時間",
        choices=[
            Choice(name="60秒", value=0),
            Choice(name="5分鐘", value=1),
            Choice(name="10分鐘", value=2),
            Choice(name="1小時", value=3),
            Choice(name="1天", value=4),
            Choice(name="1週", value=5),
        ],
    )
    @option("原因")
    async def timeout(self, ctx: CommandContext, member: Member, time: int, reason: str = None):
        """禁言成員"""
        await ctx.defer(ephemeral=True)
        if not ctx.app_permissions.MODERATE_MEMBERS:
            return await ctx.send(":x: 我沒權限禁言 ;-;", ephemeral=True)
        match time:
            case 0:
                length = timedelta(seconds=60)
            case 1:
                length = timedelta(minutes=5)
            case 2:
                length = timedelta(minutes=10)
            case 3:
                length = timedelta(hours=1)
            case 4:
                length = timedelta(days=1)
            case 5:
                length = timedelta(days=7)
            case _:
                return await ctx.send(":x: baka 你到底要禁言多久啊？", ephemeral=True)
        try:
            await member.modify(
                ctx.guild_id,
                reason=reason,
                communication_disabled_until=(datetime.now(timezone.utc) + length).isoformat(),
            )
        except LibraryException:
            return await ctx.send(f":x: 我禁言不了 {member.mention} ;-;", ephemeral=True)
        else:
            await ctx.send(f"我把 {member.mention} 禁言了！", ephemeral=True)

    @moderation.group()
    async def automod(self, *args, **kwargs):
        """自動化管理"""
        ...

    @automod.subcommand()
    async def nick(self, ctx: CommandContext):
        """自動化管理暱稱"""
        if not ctx.app_permissions.MANAGE_NICKNAMES:
            return await ctx.send(":x: 我沒權限管理暱稱 ;-;", ephemeral=True)

        await ctx.defer()

        document = await self.db.nick.find_one({"_id": int(ctx.guild_id)})
        if document:
            regex = document["regex"] if "regex" in document and document["regex"] else "*沒有設定*"
            custom = document["custom"] if "custom" in document and document["custom"] else "*沒有設定*"
        else:
            regex = "*沒有設定*"
            custom = "*沒有設定*"

        components = [
            ActionRow(
                components=[
                    SelectMenu(
                        custom_id="autonick_setting",
                        placeholder="請選擇要設定的項目",
                        max_value=1,
                        min_value=1,
                        options=[
                            SelectOption(
                                label="Regex 過濾器設定",
                                value="regex",
                                description="",
                            ),
                            SelectOption(
                                label="自訂字詞過濾器設定",
                                value="custom",
                                description="",
                            ),
                        ],
                    )
                ]
            ),
            ActionRow(
                components=[
                    Button(
                        label="儲存設定", style=ButtonStyle.SUCCESS, custom_id="autonick_setting_save"
                    ),
                    Button(
                        label="重設設定", style=ButtonStyle.DANGER, custom_id="autonick_setting_reset"
                    ),
                    Button(
                        label="取消", style=ButtonStyle.DANGER, custom_id="autonick_setting_cancel"
                    ),
                ]
            ),
        ]

        embed = Embed(
            title="自動化管理暱稱",
            description="如果有人的暱稱不符合規範，我會自動把他的暱稱改成合適的暱稱！\n請選擇要設定的項目，記得保存喔！\n以下是目前的設定：",
            color=randint(0, 0xFFFFFF),
        )
        embed.add_field("Regex 過濾器", regex)
        embed.add_field("自訂字詞過濾器", custom)

        await ctx.send(embeds=embed, components=components)

    @extension_component("autonick_setting")
    async def _autonick_setting(self, ctx: ComponentContext, selected):
        match selected[0]:
            case "regex":
                modal = Modal(
                    title="Regex 過濾器設定",
                    custom_id="autonick_setting_regex",
                    components=[
                        TextInput(
                            style=TextStyleType.PARAGRAPH,
                            label="過濾器",
                            value=ctx.message.embeds[0].fields[0].value
                            if ctx.message.embeds[0].fields[0].value != "*沒有設定*"
                            else "",
                            placeholder="請輸入有效的 Regex 過濾器",
                            max_length=256,
                            required=False,
                            custom_id="content",
                        ),
                    ],
                )
                await ctx.popup(modal)
            case "custom":
                modal = Modal(
                    title="自訂字詞過濾器設定",
                    custom_id="autonick_setting_custom",
                    components=[
                        TextInput(
                            style=TextStyleType.PARAGRAPH,
                            label="過濾器",
                            value=ctx.message.embeds[0].fields[1].value
                            if ctx.message.embeds[0].fields[1].value != "*沒有設定*"
                            else "",
                            placeholder="請輸入自訂字詞過濾器 (每行一個, 最多 10 個)",
                            max_length=256,
                            required=False,
                            custom_id="content",
                        ),
                    ],
                )
                await ctx.popup(modal)

    @extension_modal("autonick_setting_regex")
    async def _autonick_setting_regex(self, ctx: CommandContext, content):
        await ctx.defer(ephemeral=True)
        if not content:
            msg = ctx.message
            msg.embeds[0].fields[0].value = "*沒有設定*"
            await ctx.message.edit(embeds=msg.embeds, components=msg.components)
            await ctx.send("我會把設定記住的！")
            return

        try:
            re.compile(content)
        except Exception:
            return await ctx.send(":x: 這不是有效的 Regex 過濾器！")
        else:
            msg = ctx.message
            msg.embeds[0].fields[0].value = content
            await ctx.message.edit(embeds=msg.embeds, components=msg.components)
            await ctx.send("我會把設定記住的！")

    @extension_modal("autonick_setting_custom")
    async def _autonick_setting_custom(self, ctx: CommandContext, content):
        await ctx.defer(ephemeral=True)
        msg = ctx.message
        if not content:
            msg.embeds[0].fields[1].value = "*沒有設定*"
        else:
            if len(content.splitlines()) > 10:
                content = "\n".join(content.split("\n")[:10])
            msg.embeds[0].fields[1].value = content
        await ctx.message.edit(embeds=msg.embeds, components=msg.components)
        await ctx.send("我會把設定記住的！")

    @extension_component("autonick_setting_save")
    async def _autonick_setting_save(self, ctx: ComponentContext):
        if ctx.author.id != ctx.message.interaction.user.id:
            return await ctx.send(":x: baka 這不是你的訊息啦！", ephemeral=True)
        data = ctx.message.embeds[0].fields
        if not (data[0].value == "*沒有設定*" and data[1].value == "*沒有設定*"):
            await self.db.nick.replace_one(
                {"_id": int(ctx.guild_id)},
                {
                    "regex": data[0].value if data[0].value != "*沒有設定*" else None,
                    "custom": data[1].value if data[1].value != "*沒有設定*" else None,
                },
                upsert=True,
            )
        else:
            await self.db.nick.delete_one({"_id": int(ctx.guild_id)})
        await ctx.message.delete()
        await ctx.send(
            f"我會把設定記住的！\n你可以隨時用 </moderation automod nick:{self.client._find_command('moderation').id}> 回來查看設定喔！",
            ephemeral=True,
        )

    @extension_component("autonick_setting_reset")
    async def _autonick_settings_reset(self, ctx: ComponentContext):
        if ctx.author.id != ctx.message.interaction.user.id:
            return await ctx.send(":x: baka 這不是你的訊息啦！", ephemeral=True)
        await ctx.send(
            "你確定要重設設定嗎？包括現有的設定也會被刪除喔！",
            components=[
                Button(
                    label="確定",
                    style=ButtonStyle.DANGER,
                    custom_id=str(
                        PersistentCustomID(
                            self.client, "autonick_setting_reset_confirm", int(ctx.message.id)
                        )
                    ),
                ),
                Button(
                    label="取消",
                    style=ButtonStyle.SECONDARY,
                    custom_id="autonick_setting_reset_cancel",
                ),
            ],
            ephemeral=True,
        )

    @extension_persistent_component("autonick_setting_reset_confirm")
    async def _autonick_settings_reset_confirm(self, ctx: ComponentContext, package):
        await ctx.defer(edit_origin=True)
        msg = await get(self.client, Message, object_id=package, parent_id=ctx.channel_id)
        msg.embeds[0].fields[0].value = "*沒有設定*"
        msg.embeds[0].fields[1].value = "*沒有設定*"
        await msg.edit(embeds=msg.embeds, components=msg.components)
        await self.db.nick.delete_one({"_id": int(ctx.guild_id)})
        await ctx.edit("我幫你把設定重設了！", components=[])

    @extension_component("autonick_settings_reset_cancel")
    async def _autonick_settings_reset_cancel(self, ctx: ComponentContext):
        await ctx.defer(edit_origin=True)
        await ctx.edit("好的！", components=[])

    @extension_component("autonick_setting_cancel")
    async def _autonick_setting_cancel(self, ctx: ComponentContext):
        if ctx.author.id != ctx.message.interaction.user.id:
            return await ctx.send(":x: baka 這不是你的訊息啦！", ephemeral=True)
        await ctx.send(
            "你確定要取消設定嗎？未保存的設定會消失喔！",
            components=[
                Button(
                    label="是！",
                    style=ButtonStyle.DANGER,
                    custom_id=str(
                        PersistentCustomID(
                            self.client, "autonick_setting_cancel_confirm", int(ctx.message.id)
                        )
                    ),
                ),
                Button(
                    label="不要!",
                    style=ButtonStyle.SECONDARY,
                    custom_id="autonick_setting_cancel_cancel",
                ),
            ],
            ephemeral=True,
        )

    @extension_persistent_component("autonick_setting_cancel_confirm")
    async def _autonick_setting_cancel_confirm(self, ctx: ComponentContext, package):
        await ctx.defer(edit_origin=True)
        msg = await get(self.client, Message, object_id=package, parent_id=ctx.channel_id)
        await msg.delete()
        await ctx.edit(
            f"好的！\n你可以隨時用 </moderation automod nick:{self.client._find_command('moderation').id}> 回來查看設定喔！",
            components=[],
        )

    @extension_component("autonick_setting_cancel_cancel")
    async def _autonick_setting_cancel_cancel(self, ctx: ComponentContext):
        await ctx.defer(edit_origin=True)
        await ctx.edit("好的！", components=[])


def setup(client, **kwargs):
    moderate(client, **kwargs)
