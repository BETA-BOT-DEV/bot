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
    ActionRow,
    Button,
    ButtonStyle,
    Channel,
    ChannelType,
    Client,
    CommandContext,
    ComponentContext,
    ComponentType,
    Embed,
    EmbedField,
    EmbedFooter,
    Emoji,
    Guild,
    GuildMember,
    Message,
    Modal,
    Permissions,
    Role,
    SelectMenu,
    SelectOption,
    TextInput,
    TextStyleType,
    extension_command,
    extension_component,
    extension_listener,
    get,
)
from interactions.ext.persistence import (
    PersistenceExtension,
    PersistentCustomID,
    extension_persistent_component,
    extension_persistent_modal,
)
from loguru._logger import Logger


def parse_embed(embed: Embed, default="", mode="welcome"):
    channel = embed.fields[0].value if embed.fields[0].value != "*沒有設定*" else default
    content = embed.fields[1].value if embed.fields[1].value != "*沒有設定*" else default
    embed_title = embed.fields[2].value if embed.fields[2].value != "*沒有設定*" else default
    embed_description = embed.fields[3].value if embed.fields[3].value != "*沒有設定*" else default
    embed_footer = embed.fields[4].value if embed.fields[4].value != "*沒有設定*" else default
    embed_color = embed.fields[5].value if embed.fields[5].value != "*沒有設定*" else default
    if mode == "welcome":
        role = embed.fields[6].value if embed.fields[6].value != "*沒有設定*" else default
        return (channel, content, embed_title, embed_description, embed_footer, embed_color, role)
    elif mode == "farewell":
        return (channel, content, embed_title, embed_description, embed_footer, embed_color)


class welcomer(PersistenceExtension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.logger: Logger = kwargs.get("logger")
        self.db = kwargs.get("db")
        self._welcome = self.db.welcome
        self._farewell = self.db.farewell
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

    @extension_listener()
    async def on_guild_member_add(self, member: GuildMember):
        document = await self._welcome.find_one({"_id": int(member.guild_id)})
        if document:
            try:
                channel = await get(self.client, Channel, object_id=document["channel"])
                guild = await get(self.client, Guild, object_id=int(member.guild_id))
            except:  # noqa: E722
                return
            content, ebdesc = (
                i.replace("{mention}", member.mention)
                .replace("{user}", member.user.username)
                .replace("{#}", member.user.discriminator)
                .replace("{server}", guild.name)
                .replace("{user#}", str(guild.member_count))
                if i is not None
                else None
                for i in [document["message"], document["embed_description"]]
            )
            ebtitle, ebfooter = (
                i.replace("{user}", member.user.username)
                .replace("{#}", member.user.discriminator)
                .replace("{server}", guild.name)
                .replace("{user#}", str(guild.member_count))
                if i is not None
                else None
                for i in [document["embed_title"], document["embed_footer"]]
            )
            ebcolor = int(document["embed_color"], 16) if document["embed_color"] else 0x000000
            await channel.send(
                content,
                embeds=Embed(
                    title=ebtitle,
                    description=ebdesc,
                    footer=EmbedFooter(text=ebfooter) if ebfooter else None,
                    color=ebcolor,
                )
                if ebtitle or ebdesc
                else None,
            )
            if document["role"] is not None:
                role = await get(self.client, Role, object_id=document["role"], parent_id=guild.id)
                try:
                    await member.add_role(role)
                except:  # noqa: E722
                    return

    @extension_listener()
    async def on_guild_member_remove(self, member: GuildMember):
        document = await self._farewell.find_one({"_id": int(member.guild_id)})
        if document:
            try:
                channel = await get(self.client, Channel, object_id=document["channel"])
                guild = await get(self.client, Guild, object_id=int(member.guild_id))
            except:  # noqa: E722
                return
            content, ebtitle, ebdesc, ebfooter = (
                i.replace("{user}", member.user.username)
                .replace("{#}", member.user.discriminator)
                .replace("{server}", guild.name)
                .replace("{user#}", str(guild.member_count))
                if i is not None
                else None
                for i in [
                    document["message"],
                    document["embed_title"],
                    document["embed_description"],
                    document["embed_footer"],
                ]
            )
            ebcolor = int(document["embed_color"], 16) if document["embed_color"] else 0x000000
            await channel.send(
                content,
                embeds=Embed(
                    title=ebtitle,
                    description=ebdesc,
                    footer=EmbedFooter(text=ebfooter) if ebfooter else None,
                    color=ebcolor,
                )
                if ebtitle or ebdesc
                else None,
            )

    @extension_command(default_member_permissions=Permissions.MANAGE_GUILD, dm_permission=False)
    async def welcome(self, ctx: CommandContext):
        """設定歡迎訊息"""
        document = await self._welcome.find_one({"_id": int(ctx.guild_id)})
        channel = (
            "*沒有設定*" if not (document and document["channel"]) else f"<#{document['channel']}>"
        )
        role = "*沒有設定*" if not (document and document["role"]) else f"<@&{document['role']}>"
        content = "*沒有設定*" if not (document and document["message"]) else document["message"]
        embed_title = (
            "*沒有設定*" if not (document and document["embed_title"]) else document["embed_title"]
        )
        embed_description = (
            "*沒有設定*"
            if not (document and document["embed_description"])
            else document["embed_description"]
        )
        embed_footer = (
            "*沒有設定*" if not (document and document["embed_footer"]) else document["embed_footer"]
        )
        embed_color = (
            "*沒有設定*" if not (document and document["embed_color"]) else document["embed_color"]
        )
        components = [
            ActionRow(
                components=[
                    SelectMenu(
                        custom_id="welcome_settings",
                        placeholder="請選擇要設定的項目",
                        max_value=1,
                        min_value=1,
                        options=[
                            SelectOption(
                                label="頻道設定",
                                value="channel",
                                description="",
                                emoji=Emoji(name="#️⃣"),
                            ),
                            SelectOption(
                                label="訊息設定", value="message", description="", emoji=Emoji(name="💬")
                            ),
                            SelectOption(
                                label="身份組設定", value="role", description="", emoji=Emoji(name="👥")
                            ),
                        ],
                    )
                ]
            ),
            ActionRow(
                components=[
                    Button(
                        label="預覽訊息",
                        style=ButtonStyle.PRIMARY,
                        custom_id="welcome_settings_preview",
                    ),
                    Button(
                        label="儲存設定", style=ButtonStyle.SUCCESS, custom_id="welcome_settings_save"
                    ),
                    Button(
                        label="重設設定", style=ButtonStyle.DANGER, custom_id="welcome_settings_reset"
                    ),
                    Button(
                        label="取消", style=ButtonStyle.DANGER, custom_id="welcome_settings_cancel"
                    ),
                ]
            ),
        ]
        embeds = [
            Embed(
                title="歡迎訊息設定",
                description="請選擇要設定的項目，記得保存喔！\n以下是目前的設定：",
                fields=[
                    EmbedField(name="發送頻道", value=channel, inline=False),
                    EmbedField(name="訊息內容", value=content, inline=False),
                    EmbedField(name="嵌入標題", value=embed_title, inline=False),
                    EmbedField(name="嵌入描述", value=embed_description, inline=False),
                    EmbedField(name="嵌入頁腳", value=embed_footer, inline=False),
                    EmbedField(name="嵌入顏色", value=embed_color, inline=False),
                    EmbedField(name="自動身份組", value=role, inline=False),
                ],
                color=randint(0, 0xFFFFFF),
            )
        ]
        await ctx.send(embeds=embeds, components=components)

    @extension_component("welcome_settings_preview")
    async def _welcome_settings_preview(self, ctx: ComponentContext):
        if ctx.author.id != ctx.message.interaction.user.id:
            return await ctx.send(":x: baka 這不是你的訊息啦！", ephemeral=True)
        settings = parse_embed(ctx.message.embeds[0])
        if not settings[1] and not settings[2] and not settings[3]:
            return await ctx.send(
                ":x: baka 你填少了必要的設定項目: [`訊息內容` / `嵌入標題` / `嵌入描述`]", ephemeral=True
            )
        await ctx.get_guild()
        content, ebdesc = (
            settings[i]
            .replace("{mention}", ctx.author.mention)
            .replace("{user}", ctx.user.username)
            .replace("{#}", ctx.user.discriminator)
            .replace("{server}", ctx.guild.name)
            .replace("{user#}", str(ctx.guild.member_count))
            for i in [1, 3]
        )
        ebtitle, ebfooter = (
            settings[i]
            .replace("{user}", ctx.user.username)
            .replace("{#}", ctx.user.discriminator)
            .replace("{server}", ctx.guild.name)
            .replace("{user#}", str(ctx.guild.member_count))
            for i in [2, 4]
        )
        await ctx.send(
            content=f"歡迎訊息的預覽來了！\n\n{content if content else ''}",
            embeds=[]
            if not (ebtitle or ebdesc)
            else [
                Embed(
                    title=ebtitle,
                    description=ebdesc,
                    footer=EmbedFooter(text=ebfooter) if ebfooter else None,
                    color=settings[5] if settings[5] else 0x000000,
                )
            ],
            ephemeral=True,
        )

    @extension_component("welcome_settings_save")
    async def _welcome_settings_save(self, ctx: ComponentContext):
        if ctx.author.id != ctx.message.interaction.user.id:
            return await ctx.send(":x: baka 這不是你的訊息啦！", ephemeral=True)
        settings = parse_embed(ctx.message.embeds[0], None)
        if not settings[0] or not (settings[1] or settings[2] or settings[3]):
            return await ctx.send(
                ":x: baka 你填少了必要的設定項目: `發送頻道` 或 [`訊息內容` / `嵌入標題` / `嵌入描述`]", ephemeral=True
            )
        await self._welcome.replace_one(
            {"_id": int(ctx.guild_id)},
            {
                "channel": int(settings[0][2:-1]),
                "message": settings[1],
                "embed_title": settings[2],
                "embed_description": settings[3],
                "embed_color": settings[4],
                "embed_footer": settings[5],
                "role": settings[6][3:-1] if settings[6] else None,
            },
            upsert=True,
        )
        await ctx.message.delete()
        await ctx.send(
            f"我會把設定記住的！\n你可以隨時用 </welcome settings:{self.client._find_command('welcome').id}> 回來查看設定喔！",
            ephemeral=True,
        )

    @extension_component("welcome_settings_reset")
    async def _welcome_settings_reset(self, ctx: ComponentContext):
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
                            self.client, "welcome_settings_reset_confirm", int(ctx.message.id)
                        )
                    ),
                ),
                Button(
                    label="取消",
                    style=ButtonStyle.SECONDARY,
                    custom_id="welcome_settings_reset_cancel",
                ),
            ],
            ephemeral=True,
        )

    @extension_persistent_component("welcome_settings_reset_confirm")
    async def _welcome_settings_reset_confirm(self, ctx: ComponentContext, package):
        await ctx.defer(edit_origin=True)
        msg = await get(self.client, Message, object_id=package, parent_id=ctx.channel_id)
        msg.embeds[0].fields[0].value = "*沒有設定*"
        msg.embeds[0].fields[1].value = "*沒有設定*"
        msg.embeds[0].fields[2].value = "*沒有設定*"
        msg.embeds[0].fields[3].value = "*沒有設定*"
        msg.embeds[0].fields[4].value = "*沒有設定*"
        msg.embeds[0].fields[5].value = "*沒有設定*"
        msg.embeds[0].fields[6].value = "*沒有設定*"
        await msg.edit(embeds=msg.embeds, components=msg.components)
        await self._welcome.delete_one({"_id": int(ctx.guild_id)})
        await ctx.edit("幫你把重設重設了！", components=[])

    @extension_component("welcome_settings_reset_cancel")
    async def _welcome_settings_reset_cancel(self, ctx: ComponentContext):
        await ctx.defer(edit_origin=True)
        await ctx.edit("好的！", components=[])

    @extension_component("welcome_settings_cancel")
    async def _welcome_settings_cancel(self, ctx: ComponentContext):
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
                            self.client, "welcome_settings_cancel_confirm", int(ctx.message.id)
                        )
                    ),
                ),
                Button(
                    label="不要!",
                    style=ButtonStyle.SECONDARY,
                    custom_id="welcome_settings_cancel_cancel",
                ),
            ],
            ephemeral=True,
        )

    @extension_persistent_component("welcome_settings_cancel_confirm")
    async def _welcome_settings_cancel_confirm(self, ctx: ComponentContext, package):
        await ctx.defer(edit_origin=True)
        msg = await get(self.client, Message, object_id=package, parent_id=ctx.channel_id)
        await msg.delete()
        await ctx.edit(
            f"好的！\n你可以隨時用 </welcome settings:{self.client._find_command('welcome').id}> 回來查看設定喔！",
            components=[],
        )

    @extension_component("welcome_settings_cancel_cancel")
    async def _welcome_settings_cancel_cancel(self, ctx: ComponentContext):
        await ctx.defer(edit_origin=True)
        await ctx.edit("好的！", components=[])

    @extension_component("welcome_settings")
    async def _welcome_settings_select(self, ctx: ComponentContext, selected):
        match selected[0]:
            case "channel":
                await ctx.send(
                    "請選擇要發送歡迎訊息的頻道",
                    components=[
                        SelectMenu(
                            type=ComponentType.CHANNEL_SELECT,
                            channel_types=[ChannelType.GUILD_TEXT],
                            custom_id=str(
                                PersistentCustomID(
                                    self.client, "welcome_settings_channel", int(ctx.message.id)
                                )
                            ),
                            placeholder="選擇頻道",
                            min_values=1,
                            max_values=1,
                        ),
                    ],
                    ephemeral=True,
                )
            case "message":
                settings = parse_embed(ctx.message.embeds[0], "")
                modal = Modal(
                    title="歡迎訊息",
                    custom_id=str(
                        PersistentCustomID(
                            self.client, "welcome_settings_message", int(ctx.message.id)
                        )
                    ),
                    components=[
                        TextInput(
                            style=TextStyleType.PARAGRAPH,
                            label="訊息內容",
                            value=settings[1],
                            placeholder="請輸入訊息內容\n可用參數: {mention} | {user} | {#} | {server} | {user#}",
                            max_length=1024,
                            required=False,
                            custom_id="content",
                        ),
                        TextInput(
                            style=TextStyleType.PARAGRAPH,
                            label="嵌入標題",
                            value=settings[2],
                            placeholder="請輸入嵌入標題\n可用參數: {user} | {#} | {server} | {user#}",
                            max_length=256,
                            required=False,
                            custom_id="embed_title",
                        ),
                        TextInput(
                            style=TextStyleType.PARAGRAPH,
                            label="嵌入描述",
                            value=settings[3],
                            placeholder="請輸入嵌入描述\n可用參數: {mention} | {user} | {#} | {server} | {user#}",
                            max_length=1024,
                            required=False,
                            custom_id="embed_description",
                        ),
                        TextInput(
                            style=TextStyleType.SHORT,
                            label="嵌入頁腳",
                            value=settings[4],
                            placeholder="請輸入嵌入頁腳\n可用參數: {user} | {#} | {server} | {user#}",
                            max_length=1024,
                            required=False,
                            custom_id="embed_footer",
                        ),
                        TextInput(
                            style=TextStyleType.SHORT,
                            label="嵌入顏色",
                            value=settings[5],
                            placeholder="請輸入嵌入顏色",
                            max_length=6,
                            min_length=6,
                            required=False,
                            custom_id="embed_color",
                        ),
                    ],
                )
                await ctx.popup(modal)
            case "role":
                await ctx.send(
                    "請選擇要自動給予的身份組 (可留空)",
                    components=[
                        SelectMenu(
                            type=ComponentType.ROLE_SELECT,
                            custom_id=str(
                                PersistentCustomID(
                                    self.client, "welcome_settings_role", int(ctx.message.id)
                                )
                            ),
                            placeholder="選擇身份組",
                            min_values=0,
                            max_values=1,
                        ),
                    ],
                    ephemeral=True,
                )

    @extension_persistent_component("welcome_settings_channel")
    async def _welcome_settings_channel(self, ctx: ComponentContext, package, selected=None):
        await ctx.defer(edit_origin=True)
        msg = await get(self.client, Message, object_id=package, parent_id=ctx.channel_id)
        msg.embeds[0].fields[0].value = f"<#{ctx.data.values[0]}>"
        await msg.edit(embeds=msg.embeds, components=msg.components)
        await ctx.edit("我會把設定記住的！")

    @extension_persistent_modal("welcome_settings_message")
    async def _welcome_settings_message(
        self,
        ctx: CommandContext,
        package,
        content,
        embed_title,
        embed_description,
        embed_footer,
        embed_color,
    ):
        if not (content or embed_title or embed_description):
            return await ctx.send(
                ":x: baka 你填少了必要的設定項目: [`訊息內容` / `嵌入標題` / `嵌入描述`]", ephemeral=True
            )
        if embed_color:
            try:
                i = int(f"0x{embed_color}", 16)
            except ValueError:
                return await ctx.send(":x: baka 你的嵌入顏色不正確喔！", ephemeral=True)
            if i > 0xFFFFFF or i < 0:
                return await ctx.send(":x: baka 你的嵌入顏色不正確喔！", ephemeral=True)
        msg = await get(self.client, Message, object_id=package, parent_id=ctx.channel_id)
        msg.embeds[0].fields[1].value = content if content else "*沒有設定*"
        msg.embeds[0].fields[2].value = embed_title if embed_title else "*沒有設定*"
        msg.embeds[0].fields[3].value = embed_description if embed_description else "*沒有設定*"
        msg.embeds[0].fields[4].value = embed_footer if embed_footer else "*沒有設定*"
        msg.embeds[0].fields[5].value = embed_color if embed_color else "*沒有設定*"
        await msg.edit(embeds=msg.embeds, components=msg.components)
        await ctx.send("我會把設定記住的！", ephemeral=True)

    @extension_persistent_component("welcome_settings_role")
    async def _welcome_settings_role(self, ctx: ComponentContext, package, selected=None):
        await ctx.defer(edit_origin=True)
        msg = await get(self.client, Message, object_id=package, parent_id=ctx.channel_id)
        if len(ctx.data.values) == 0:
            msg.embeds[0].fields[6].value = "*沒有設定*"
        else:
            msg.embeds[0].fields[6].value = f"<@&{ctx.data.values[0]}>"
        await msg.edit(embeds=msg.embeds, components=msg.components)
        await ctx.edit("我會把設定記住的！")

    @extension_command(default_member_permissions=Permissions.MANAGE_GUILD, dm_permission=False)
    async def farewell(self, ctx: CommandContext):
        """設定離開訊息"""
        document = await self._farewell.find_one({"_id": int(ctx.guild_id)})
        channel = (
            "*沒有設定*" if not (document and document["channel"]) else f"<#{document['channel']}>"
        )
        content = "*沒有設定*" if not (document and document["message"]) else document["message"]
        embed_title = (
            "*沒有設定*" if not (document and document["embed_title"]) else document["embed_title"]
        )
        embed_description = (
            "*沒有設定*"
            if not (document and document["embed_description"])
            else document["embed_description"]
        )
        embed_footer = (
            "*沒有設定*" if not (document and document["embed_footer"]) else document["embed_footer"]
        )
        embed_color = (
            "*沒有設定*" if not (document and document["embed_color"]) else document["embed_color"]
        )
        components = [
            ActionRow(
                components=[
                    SelectMenu(
                        custom_id="farewell_settings",
                        placeholder="請選擇要設定的項目",
                        max_value=1,
                        min_value=1,
                        options=[
                            SelectOption(
                                label="頻道設定",
                                value="channel",
                                description="",
                                emoji=Emoji(name="#️⃣"),
                            ),
                            SelectOption(
                                label="訊息設定", value="message", description="", emoji=Emoji(name="💬")
                            ),
                        ],
                    )
                ]
            ),
            ActionRow(
                components=[
                    Button(
                        label="預覽訊息",
                        style=ButtonStyle.PRIMARY,
                        custom_id="farewell_settings_preview",
                    ),
                    Button(
                        label="儲存設定", style=ButtonStyle.SUCCESS, custom_id="farewell_settings_save"
                    ),
                    Button(
                        label="重設設定", style=ButtonStyle.DANGER, custom_id="farewell_settings_reset"
                    ),
                    Button(
                        label="取消", style=ButtonStyle.DANGER, custom_id="farewell_settings_cancel"
                    ),
                ]
            ),
        ]
        embeds = [
            Embed(
                title="離開訊息設定",
                description="請選擇要設定的項目，記得保存喔！\n以下是目前的設定：",
                fields=[
                    EmbedField(name="發送頻道", value=channel, inline=False),
                    EmbedField(name="訊息內容", value=content, inline=False),
                    EmbedField(name="嵌入標題", value=embed_title, inline=False),
                    EmbedField(name="嵌入描述", value=embed_description, inline=False),
                    EmbedField(name="嵌入頁腳", value=embed_footer, inline=False),
                    EmbedField(name="嵌入顏色", value=embed_color, inline=False),
                ],
                color=randint(0, 0xFFFFFF),
            )
        ]
        await ctx.send(embeds=embeds, components=components)

    @extension_component("farewell_settings_preview")
    async def _farewell_settings_preview(self, ctx: ComponentContext):
        if ctx.author.id != ctx.message.interaction.user.id:
            return await ctx.send(":x: baka 這不是你的訊息啦！", ephemeral=True)
        settings = parse_embed(ctx.message.embeds[0], "", "farewell")
        if not settings[1] and not settings[2] and not settings[3]:
            return await ctx.send(
                ":x: baka 你填少了必要的設定項目: [`訊息內容` / `嵌入標題` / `嵌入描述`]", ephemeral=True
            )
        await ctx.get_guild()
        content, ebtitle, ebdesc, ebfooter = (
            settings[i]
            .replace("{user}", ctx.user.username)
            .replace("{#}", ctx.user.discriminator)
            .replace("{server}", ctx.guild.name)
            .replace("{user#}", str(ctx.guild.member_count))
            for i in [1, 2, 3, 4]
        )
        await ctx.send(
            content=f"離開訊息的預覽來了！\n\n{content if content else ''}",
            embeds=[]
            if not (ebtitle or ebdesc)
            else [
                Embed(
                    title=ebtitle,
                    description=ebdesc,
                    footer=EmbedFooter(text=ebfooter) if ebfooter else None,
                    color=settings[5] if settings[5] else 0x000000,
                )
            ],
            ephemeral=True,
        )

    @extension_component("farewell_settings_save")
    async def _farewell_settings_save(self, ctx: ComponentContext):
        if ctx.author.id != ctx.message.interaction.user.id:
            return await ctx.send(":x: baka 這不是你的訊息啦！", ephemeral=True)
        settings = parse_embed(ctx.message.embeds[0], None, "farewell")
        if not settings[0] or not (settings[1] or settings[2] or settings[3]):
            return await ctx.send(
                ":x: baka 你填少了必要的設定項目: `發送頻道` 或 [`訊息內容` / `嵌入標題` / `嵌入描述`]", ephemeral=True
            )
        await self._farewell.replace_one(
            {"_id": int(ctx.guild_id)},
            {
                "channel": int(settings[0][2:-1]),
                "message": settings[1],
                "embed_title": settings[2],
                "embed_description": settings[3],
                "embed_color": settings[4],
                "embed_footer": settings[5],
            },
            upsert=True,
        )
        await ctx.message.delete()
        await ctx.send(
            f"我會把設定記住的！\n你可以隨時用 </farewell settings:{self.client._find_command('farewell').id}> 回來查看設定喔！",
            ephemeral=True,
        )

    @extension_component("farewell_settings_reset")
    async def _farewell_settings_reset(self, ctx: ComponentContext):
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
                            self.client, "farewell_settings_reset_confirm", int(ctx.message.id)
                        )
                    ),
                ),
                Button(
                    label="取消",
                    style=ButtonStyle.SECONDARY,
                    custom_id="farewell_settings_reset_cancel",
                ),
            ],
            ephemeral=True,
        )

    @extension_persistent_component("farewell_settings_reset_confirm")
    async def _farewell_settings_reset_confirm(self, ctx: ComponentContext, package):
        await ctx.defer(edit_origin=True)
        msg = await get(self.client, Message, object_id=package, parent_id=ctx.channel_id)
        msg.embeds[0].fields[0].value = "*沒有設定*"
        msg.embeds[0].fields[1].value = "*沒有設定*"
        msg.embeds[0].fields[2].value = "*沒有設定*"
        msg.embeds[0].fields[3].value = "*沒有設定*"
        msg.embeds[0].fields[4].value = "*沒有設定*"
        msg.embeds[0].fields[5].value = "*沒有設定*"
        await msg.edit(embeds=msg.embeds, components=msg.components)
        await self._farewell.delete_one({"_id": int(ctx.guild_id)})
        await ctx.edit("幫你把重設重設了！", components=[])

    @extension_component("farewell_settings_reset_cancel")
    async def _farewell_settings_reset_cancel(self, ctx: ComponentContext):
        await ctx.defer(edit_origin=True)
        await ctx.edit("好的！", components=[])

    @extension_component("farewell_settings_cancel")
    async def _farewell_settings_cancel(self, ctx: ComponentContext):
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
                            self.client, "farewell_settings_cancel_confirm", int(ctx.message.id)
                        )
                    ),
                ),
                Button(
                    label="不要!",
                    style=ButtonStyle.SECONDARY,
                    custom_id="farewell_settings_cancel_cancel",
                ),
            ],
            ephemeral=True,
        )

    @extension_persistent_component("farewell_settings_cancel_confirm")
    async def _farewell_settings_cancel_confirm(self, ctx: ComponentContext, package):
        await ctx.defer(edit_origin=True)
        msg = await get(self.client, Message, object_id=package, parent_id=ctx.channel_id)
        await msg.delete()
        await ctx.edit(
            f"好的！\n你可以隨時用 </farewell settings:{self.client._find_command('farewell').id}> 回來查看設定喔！",
            components=[],
        )

    @extension_component("farewell_settings_cancel_cancel")
    async def _farewell_settings_cancel_cancel(self, ctx: ComponentContext):
        await ctx.defer(edit_origin=True)
        await ctx.edit("好的！", components=[])

    @extension_component("farewell_settings")
    async def _farewell_settings_select(self, ctx: ComponentContext, selected):
        match selected[0]:
            case "channel":
                await ctx.send(
                    "請選擇要發送離開訊息的頻道",
                    components=[
                        SelectMenu(
                            type=ComponentType.CHANNEL_SELECT,
                            channel_types=[ChannelType.GUILD_TEXT],
                            custom_id=str(
                                PersistentCustomID(
                                    self.client, "farewell_settings_channel", int(ctx.message.id)
                                )
                            ),
                            placeholder="選擇頻道",
                            min_values=1,
                            max_values=1,
                        ),
                    ],
                    ephemeral=True,
                )
            case "message":
                settings = parse_embed(ctx.message.embeds[0], "", "farewell")
                modal = Modal(
                    title="離開訊息",
                    custom_id=str(
                        PersistentCustomID(
                            self.client, "farewell_settings_message", int(ctx.message.id)
                        )
                    ),
                    components=[
                        TextInput(
                            style=TextStyleType.PARAGRAPH,
                            label="訊息內容",
                            value=settings[1],
                            placeholder="請輸入訊息內容\n可用參數: {user} | {#} | {server} | {user#}",
                            max_length=1024,
                            required=False,
                            custom_id="content",
                        ),
                        TextInput(
                            style=TextStyleType.PARAGRAPH,
                            label="嵌入標題",
                            value=settings[2],
                            placeholder="請輸入嵌入標題\n可用參數: {user} | {#} | {server} | {user#}",
                            max_length=256,
                            required=False,
                            custom_id="embed_title",
                        ),
                        TextInput(
                            style=TextStyleType.PARAGRAPH,
                            label="嵌入描述",
                            value=settings[3],
                            placeholder="請輸入嵌入描述\n可用參數: {user} | {#} | {server} | {user#}",
                            max_length=1024,
                            required=False,
                            custom_id="embed_description",
                        ),
                        TextInput(
                            style=TextStyleType.SHORT,
                            label="嵌入頁腳",
                            value=settings[4],
                            placeholder="請輸入嵌入頁腳\n可用參數: {user} | {#} | {server} | {user#}",
                            max_length=1024,
                            required=False,
                            custom_id="embed_footer",
                        ),
                        TextInput(
                            style=TextStyleType.SHORT,
                            label="嵌入顏色",
                            value=settings[5],
                            placeholder="請輸入嵌入顏色",
                            max_length=6,
                            min_length=6,
                            required=False,
                            custom_id="embed_color",
                        ),
                    ],
                )
                await ctx.popup(modal)

    @extension_persistent_component("farewell_settings_channel")
    async def _farewell_settings_channel(self, ctx: ComponentContext, package, selected=None):
        await ctx.defer(edit_origin=True)
        msg = await get(self.client, Message, object_id=package, parent_id=ctx.channel_id)
        msg.embeds[0].fields[0].value = f"<#{ctx.data.values[0]}>"
        await msg.edit(embeds=msg.embeds, components=msg.components)
        await ctx.edit("我會把設定記住的！")

    @extension_persistent_modal("farewell_settings_message")
    async def _farewell_settings_message(
        self,
        ctx: CommandContext,
        package,
        content,
        embed_title,
        embed_description,
        embed_footer,
        embed_color,
    ):
        if not (content or embed_title or embed_description):
            return await ctx.send(
                ":x: baka 你填少了必要的設定項目: [`訊息內容` / `嵌入標題` / `嵌入描述`]", ephemeral=True
            )
        if embed_color:
            try:
                i = int(f"0x{embed_color}", 16)
            except ValueError:
                return await ctx.send(":x: baka 你的嵌入顏色不正確喔！", ephemeral=True)
            if i > 0xFFFFFF or i < 0:
                return await ctx.send(":x: baka 你的嵌入顏色不正確喔！", ephemeral=True)
        msg = await get(self.client, Message, object_id=package, parent_id=ctx.channel_id)
        msg.embeds[0].fields[1].value = content if content else "*沒有設定*"
        msg.embeds[0].fields[2].value = embed_title if embed_title else "*沒有設定*"
        msg.embeds[0].fields[3].value = embed_description if embed_description else "*沒有設定*"
        msg.embeds[0].fields[4].value = embed_footer if embed_footer else "*沒有設定*"
        msg.embeds[0].fields[5].value = embed_color if embed_color else "*沒有設定*"
        await msg.edit(embeds=msg.embeds, components=msg.components)
        await ctx.send("我會把設定記住的！", ephemeral=True)


def setup(client, **kwargs):
    welcomer(client, **kwargs)
