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
    @option("????????????????????????", min_value=1)
    async def purge(self, ctx: CommandContext, limit: int):
        """????????????"""
        await ctx.defer(ephemeral=True)
        await ctx.get_channel()
        try:
            deleted = await ctx.channel.purge(amount=limit)
        except LibraryException:
            await ctx.send(":x: ???????????????????????? ;-;", ephemeral=True)
        else:
            await ctx.send(f"???????????? {len(deleted)} ??????????????????14?????????????????????????????????", ephemeral=True)

    @moderation.subcommand()
    @option("????????????")
    @option("??????")
    async def kick(self, ctx: CommandContext, member: Member, reason: str = None):
        """????????????"""
        await ctx.defer(ephemeral=True)
        if not ctx.app_permissions.KICK_MEMBERS:
            return await ctx.send(":x: ?????????????????? ;-;", ephemeral=True)
        try:
            await member.kick(ctx.guild_id, reason)
        except LibraryException:
            return await ctx.send(f":x: ???????????? {member.mention} ;-;", ephemeral=True)
        else:
            await ctx.send(
                f"?????? {member.user.username}#{member.user.discriminator} ????????????????????????", ephemeral=True
            )

    @extension_user_command(
        name="????????????", dm_permission=False, default_member_permissions=Permissions.KICK_MEMBERS
    )
    async def _user_kick(self, ctx: CommandContext):
        await ctx.defer(ephemeral=True)
        if not ctx.app_permissions.KICK_MEMBERS:
            return await ctx.send(":x: ?????????????????? ;-;", ephemeral=True)
        try:
            await ctx.target.kick(ctx.guild_id)
        except LibraryException:
            return await ctx.send(f":x: ???????????? {ctx.target.mention} ;-;", ephemeral=True)
        else:
            await ctx.send(
                f"?????? {ctx.target.user.username}#{ctx.target.user.discriminator} ????????????????????????",
                ephemeral=True,
            )

    @moderation.subcommand()
    @option("???????????????")
    @option("??????")
    async def ban(self, ctx: CommandContext, member: Member, reason: str = None):
        """????????????"""
        await ctx.defer(ephemeral=True)
        if not ctx.app_permissions.BAN_MEMBERS:
            return await ctx.send(":x: ??????????????????????????? ;-;", ephemeral=True)
        try:
            await member.ban(ctx.guild_id, reason)
        except LibraryException:
            return await ctx.send(f":x: ??????????????? {member.mention} ;-;", ephemeral=True)
        else:
            await ctx.send(
                f"?????? {member.user.username}#{member.user.discriminator} ?????????????????????", ephemeral=True
            )

    @moderation.subcommand()
    @option("???????????????")
    @option(
        "????????????",
        choices=[
            Choice(name="60???", value=0),
            Choice(name="5??????", value=1),
            Choice(name="10??????", value=2),
            Choice(name="1??????", value=3),
            Choice(name="1???", value=4),
            Choice(name="1???", value=5),
        ],
    )
    @option("??????")
    async def timeout(self, ctx: CommandContext, member: Member, time: int, reason: str = None):
        """????????????"""
        await ctx.defer(ephemeral=True)
        if not ctx.app_permissions.MODERATE_MEMBERS:
            return await ctx.send(":x: ?????????????????? ;-;", ephemeral=True)
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
                return await ctx.send(":x: baka ??????????????????????????????", ephemeral=True)
        try:
            await member.modify(
                ctx.guild_id,
                reason=reason,
                communication_disabled_until=(datetime.now(timezone.utc) + length).isoformat(),
            )
        except LibraryException:
            return await ctx.send(f":x: ??????????????? {member.mention} ;-;", ephemeral=True)
        else:
            await ctx.send(f"?????? {member.mention} ????????????", ephemeral=True)

    @moderation.group()
    async def automod(self, *args, **kwargs):
        """???????????????"""
        ...

    @automod.subcommand()
    async def nick(self, ctx: CommandContext):
        """?????????????????????"""
        if not ctx.app_permissions.MANAGE_NICKNAMES:
            return await ctx.send(":x: ???????????????????????? ;-;", ephemeral=True)

        await ctx.defer()

        document = await self.db.nick.find_one({"_id": int(ctx.guild_id)})
        if document:
            regex = document["regex"] if "regex" in document and document["regex"] else "*????????????*"
            custom = document["custom"] if "custom" in document and document["custom"] else "*????????????*"
        else:
            regex = "*????????????*"
            custom = "*????????????*"

        components = [
            ActionRow(
                components=[
                    SelectMenu(
                        custom_id="autonick_setting",
                        placeholder="???????????????????????????",
                        max_value=1,
                        min_value=1,
                        options=[
                            SelectOption(
                                label="Regex ???????????????",
                                value="regex",
                                description="",
                            ),
                            SelectOption(
                                label="???????????????????????????",
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
                        label="????????????", style=ButtonStyle.SUCCESS, custom_id="autonick_setting_save"
                    ),
                    Button(
                        label="????????????", style=ButtonStyle.DANGER, custom_id="autonick_setting_reset"
                    ),
                    Button(
                        label="??????", style=ButtonStyle.DANGER, custom_id="autonick_setting_cancel"
                    ),
                ]
            ),
        ]

        embed = Embed(
            title="?????????????????????",
            description="??????????????????????????????????????????????????????????????????????????????????????????\n????????????????????????????????????????????????\n???????????????????????????",
            color=randint(0, 0xFFFFFF),
        )
        embed.add_field("Regex ?????????", regex)
        embed.add_field("?????????????????????", custom)

        await ctx.send(embeds=embed, components=components)

    @extension_component("autonick_setting")
    async def _autonick_setting(self, ctx: ComponentContext, selected):
        match selected[0]:
            case "regex":
                modal = Modal(
                    title="Regex ???????????????",
                    custom_id="autonick_setting_regex",
                    components=[
                        TextInput(
                            style=TextStyleType.PARAGRAPH,
                            label="?????????",
                            value=ctx.message.embeds[0].fields[0].value
                            if ctx.message.embeds[0].fields[0].value != "*????????????*"
                            else "",
                            placeholder="?????????????????? Regex ?????????",
                            max_length=256,
                            required=False,
                            custom_id="content",
                        ),
                    ],
                )
                await ctx.popup(modal)
            case "custom":
                modal = Modal(
                    title="???????????????????????????",
                    custom_id="autonick_setting_custom",
                    components=[
                        TextInput(
                            style=TextStyleType.PARAGRAPH,
                            label="?????????",
                            value=ctx.message.embeds[0].fields[1].value
                            if ctx.message.embeds[0].fields[1].value != "*????????????*"
                            else "",
                            placeholder="?????????????????????????????? (????????????, ?????? 10 ???)",
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
            msg.embeds[0].fields[0].value = "*????????????*"
            await ctx.message.edit(embeds=msg.embeds, components=msg.components)
            await ctx.send("???????????????????????????")
            return

        try:
            re.compile(content)
        except Exception:
            return await ctx.send(":x: ?????????????????? Regex ????????????")
        else:
            msg = ctx.message
            msg.embeds[0].fields[0].value = content
            await ctx.message.edit(embeds=msg.embeds, components=msg.components)
            await ctx.send("???????????????????????????")

    @extension_modal("autonick_setting_custom")
    async def _autonick_setting_custom(self, ctx: CommandContext, content):
        await ctx.defer(ephemeral=True)
        msg = ctx.message
        if not content:
            msg.embeds[0].fields[1].value = "*????????????*"
        else:
            if len(content.splitlines()) > 10:
                content = "\n".join(content.split("\n")[:10])
            msg.embeds[0].fields[1].value = content
        await ctx.message.edit(embeds=msg.embeds, components=msg.components)
        await ctx.send("???????????????????????????")

    @extension_component("autonick_setting_save")
    async def _autonick_setting_save(self, ctx: ComponentContext):
        if ctx.author.id != ctx.message.interaction.user.id:
            return await ctx.send(":x: baka ???????????????????????????", ephemeral=True)
        data = ctx.message.embeds[0].fields
        if not (data[0].value == "*????????????*" and data[1].value == "*????????????*"):
            await self.db.nick.replace_one(
                {"_id": int(ctx.guild_id)},
                {
                    "regex": data[0].value if data[0].value != "*????????????*" else None,
                    "custom": data[1].value if data[1].value != "*????????????*" else None,
                },
                upsert=True,
            )
        else:
            await self.db.nick.delete_one({"_id": int(ctx.guild_id)})
        await ctx.message.delete()
        await ctx.send(
            f"???????????????????????????\n?????????????????? </moderation automod nick:{self.client._find_command('moderation').id}> ????????????????????????",
            ephemeral=True,
        )

    @extension_component("autonick_setting_reset")
    async def _autonick_settings_reset(self, ctx: ComponentContext):
        if ctx.author.id != ctx.message.interaction.user.id:
            return await ctx.send(":x: baka ???????????????????????????", ephemeral=True)
        await ctx.send(
            "????????????????????????????????????????????????????????????????????????",
            components=[
                Button(
                    label="??????",
                    style=ButtonStyle.DANGER,
                    custom_id=str(
                        PersistentCustomID(
                            self.client, "autonick_setting_reset_confirm", int(ctx.message.id)
                        )
                    ),
                ),
                Button(
                    label="??????",
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
        msg.embeds[0].fields[0].value = "*????????????*"
        msg.embeds[0].fields[1].value = "*????????????*"
        await msg.edit(embeds=msg.embeds, components=msg.components)
        await self.db.nick.delete_one({"_id": int(ctx.guild_id)})
        await ctx.edit("??????????????????????????????", components=[])

    @extension_component("autonick_settings_reset_cancel")
    async def _autonick_settings_reset_cancel(self, ctx: ComponentContext):
        await ctx.defer(edit_origin=True)
        await ctx.edit("?????????", components=[])

    @extension_component("autonick_setting_cancel")
    async def _autonick_setting_cancel(self, ctx: ComponentContext):
        if ctx.author.id != ctx.message.interaction.user.id:
            return await ctx.send(":x: baka ???????????????????????????", ephemeral=True)
        await ctx.send(
            "???????????????????????????????????????????????????????????????",
            components=[
                Button(
                    label="??????",
                    style=ButtonStyle.DANGER,
                    custom_id=str(
                        PersistentCustomID(
                            self.client, "autonick_setting_cancel_confirm", int(ctx.message.id)
                        )
                    ),
                ),
                Button(
                    label="??????!",
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
            f"?????????\n?????????????????? </moderation automod nick:{self.client._find_command('moderation').id}> ????????????????????????",
            components=[],
        )

    @extension_component("autonick_setting_cancel_cancel")
    async def _autonick_setting_cancel_cancel(self, ctx: ComponentContext):
        await ctx.defer(edit_origin=True)
        await ctx.edit("?????????", components=[])


def setup(client, **kwargs):
    moderate(client, **kwargs)
