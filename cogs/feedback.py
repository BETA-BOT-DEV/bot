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
from datetime import datetime

import aiosqlite
from interactions import (
    ActionRow,
    Button,
    ButtonStyle,
    Channel,
    Client,
    CommandContext,
    ComponentContext,
    Embed,
    EmbedField,
    EmbedFooter,
    Emoji,
    Message,
    MessageType,
    Modal,
    SelectMenu,
    SelectOption,
    TextInput,
    TextStyleType,
    extension_command,
    extension_component,
    extension_listener,
)
from interactions.ext.persistence import (
    PersistenceExtension,
    PersistentCustomID,
    extension_persistent_component,
    extension_persistent_modal,
)
from loguru._logger import Logger

from utils import raweb

newline = "\n"

feedback_select = [
    ActionRow(
        components=[
            SelectMenu(
                custom_id="feedback",
                placeholder="請選擇回饋類別",
                min_values=1,
                max_values=1,
                options=[
                    SelectOption(
                        label="提出建議",
                        value="suggestion",
                        description="覺得我有什麼可以改進的嗎？",
                        emoji=Emoji(name="📝"),
                    ),
                    SelectOption(
                        label="錯誤回報",
                        value="bugreport",
                        description="我做錯了什麼嗎？",
                        emoji=Emoji(name="🐛"),
                    ),
                    SelectOption(
                        label="使用心得", value="rep", description="我陪著你開心嗎？", emoji=Emoji(name="⭐")
                    ),
                    SelectOption(
                        label="取消", value="cancel", description="真的不要留句話嗎？", emoji=Emoji(name="❌")
                    ),
                ],
            )
        ]
    )
]


class feedback(PersistenceExtension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.logger: Logger = kwargs.get("logger")
        self.db = kwargs.get("db")
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

    @extension_command()
    async def feedback(self, ctx: CommandContext):
        """想對我的開發者說些什麼嗎？"""
        await ctx.defer(ephemeral=True)
        async with aiosqlite.connect("./storage/storage.db") as db, db.execute(
            f"SELECT * FROM feedback_blocked WHERE user={ctx.user.id}"
        ) as cursor:
            data = [i async for i in cursor]
        if data:
            return await ctx.send(":x: 你已被禁止使用回饋系統，如有疑問請聯絡開發者。")
        await ctx.send(
            embeds=raweb(
                "有什麼想對我的開發者說的嗎？",
                "你可以透過此系統提出建議、回報錯誤，或者告訴我們你的使用心得。",
                footer=EmbedFooter(text="濫用表單可能導致你被開發者禁止使用此系統"),
            ),
            components=feedback_select,
        )

    @extension_component("feedback")
    async def _feedback_select(self, ctx: ComponentContext, selected):
        async with aiosqlite.connect("./storage/storage.db") as db, db.execute(
            f"SELECT * FROM feedback_blocked WHERE user={ctx.user.id}"
        ) as cursor:
            data = [i async for i in cursor]
        if data:
            await ctx.defer(edit_origin=True)
            return await ctx.edit(":x: 你已被禁止使用回饋系統，如有疑問請聯絡開發者。", embeds=[], components=[])
        match selected[0]:
            case "suggestion":
                await ctx.popup(
                    modal=Modal(
                        title="提出建議",
                        custom_id=str(
                            PersistentCustomID(self.client, "feedback_modal", "suggestion")
                        ),
                        components=[
                            TextInput(
                                style=TextStyleType.PARAGRAPH,
                                label="建議",
                                placeholder="請輸入你的建議",
                                custom_id="content",
                                min_length=1,
                                max_length=2000,
                                required=True,
                            )
                        ],
                    )
                )
            case "bugreport":
                await ctx.popup(
                    modal=Modal(
                        title="錯誤回報",
                        custom_id=str(
                            PersistentCustomID(self.client, "feedback_modal", "bugreport")
                        ),
                        components=[
                            TextInput(
                                style=TextStyleType.PARAGRAPH,
                                label="回報內容",
                                placeholder="請輸入詳細的錯誤",
                                custom_id="content",
                                min_length=1,
                                max_length=2000,
                            )
                        ],
                    )
                )
            case "rep":
                await ctx.popup(
                    modal=Modal(
                        title="使用心得",
                        custom_id=str(PersistentCustomID(self.client, "feedback_modal", "rep")),
                        components=[
                            TextInput(
                                style=TextStyleType.PARAGRAPH,
                                label="心得",
                                placeholder="請輸入你的心得",
                                custom_id="content",
                                min_length=1,
                                max_length=2000,
                            )
                        ],
                    )
                )
            case "cancel":
                await ctx.defer(edit_origin=True)
                await ctx.edit("取消成功！", embeds=[], components=[])

    @extension_persistent_modal("feedback_modal")
    async def _feedback_modal(self, ctx: CommandContext, package: str, content: str):
        await ctx.defer(ephemeral=True)
        match package:
            case "suggestion":
                category = "建議"
                color = 0x9BF6FF
                components = [
                    ActionRow(
                        components=[
                            Button(
                                style=ButtonStyle.PRIMARY,
                                label="釘選",
                                custom_id="feedback_pin",
                                emoji=Emoji(name="📌"),
                            ),
                            Button(
                                label="已處理",
                                custom_id="feedback_handled",
                                style=ButtonStyle.PRIMARY,
                                emoji=Emoji(name="📝"),
                            ),
                            Button(
                                label="忽略",
                                custom_id="feedback_ignore",
                                style=ButtonStyle.SECONDARY,
                                emoji=Emoji(name="❌"),
                            ),
                            Button(
                                label="封鎖",
                                custom_id=str(
                                    PersistentCustomID(
                                        self.client, "feedback_block", int(ctx.author.id)
                                    )
                                ),
                                style=ButtonStyle.DANGER,
                                emoji=Emoji(name="🚨"),
                            ),
                        ]
                    )
                ]
            case "bugreport":
                category = "錯誤回報"
                color = 0xFFADAD
                components = [
                    ActionRow(
                        components=[
                            Button(
                                style=ButtonStyle.PRIMARY,
                                label="釘選",
                                custom_id="feedback_pin",
                                emoji=Emoji(name="📌"),
                            ),
                            Button(
                                label="已處理",
                                custom_id="feedback_handled",
                                style=ButtonStyle.PRIMARY,
                                emoji=Emoji(name="📝"),
                            ),
                            Button(
                                label="忽略",
                                custom_id="feedback_ignore",
                                style=ButtonStyle.SECONDARY,
                                emoji=Emoji(name="❌"),
                            ),
                            Button(
                                label="封鎖",
                                custom_id=str(
                                    PersistentCustomID(
                                        self.client, "feedback_block", int(ctx.author.id)
                                    )
                                ),
                                style=ButtonStyle.DANGER,
                                emoji=Emoji(name="🚨"),
                            ),
                        ]
                    )
                ]
            case "rep":
                category = "使用心得"
                color = 0xFDFFB6
                components = [
                    ActionRow(
                        components=[
                            Button(
                                style=ButtonStyle.PRIMARY,
                                label="釘選",
                                custom_id="feedback_pin",
                                emoji=Emoji(name="📌"),
                            ),
                            Button(
                                label="封鎖",
                                custom_id=str(
                                    PersistentCustomID(
                                        self.client, "feedback_block", int(ctx.author.id)
                                    )
                                ),
                                style=ButtonStyle.DANGER,
                                emoji=Emoji(name="🚨"),
                            ),
                        ]
                    )
                ]
        await Channel(
            **await self.client._http.create_dm(recipient_id=int(self.client.me.owner.id)),
            _client=self.client._http,
        ).send(
            embeds=Embed(
                title="使用者回饋",
                description="收到新的使用者回饋了！",
                fields=[
                    EmbedField(
                        name="使用者",
                        value=f"{ctx.user.username}#{ctx.user.discriminator} ({ctx.user.id})",
                        inline=False,
                    ),
                    EmbedField(name="類別", value=category, inline=False),
                    EmbedField(name="內容", value=content, inline=False),
                ],
                color=color,
                timestamp=datetime.utcnow(),
            ),
            components=components,
        )

    # OWNER STUFF

    @extension_component("feedback_pin")
    async def _feedback_pin(self, ctx: ComponentContext):
        if ctx.user.id != self.client.me.owner.id:
            return await ctx.send(":x: 你不是我的開發者！你不可以使用此按鈕。", ephemeral=True)
        if not ctx.message.pinned:
            await ctx.message.pin()
        components = ctx.message.components
        components[0].components[0].label = "取消釘選"
        components[0].components[0].custom_id = "feedback_unpin"
        embed = ctx.message.embeds[0]
        embed.color = 0xFFFF00
        await ctx.message.edit(embeds=embed, components=components)
        await ctx.send("已釘選訊息！", ephemeral=True)

    @extension_component("feedback_unpin")
    async def _feedback_unpin(self, ctx: ComponentContext):
        if ctx.user.id != self.client.me.owner.id:
            return await ctx.send(":x: 你不是我的開發者！你不可以使用此按鈕。", ephemeral=True)
        if ctx.message.pinned:
            await ctx.message.unpin()
        components = ctx.message.components
        components[0].components[0].label = "釘選"
        components[0].components[0].custom_id = "feedback_pin"
        embed = ctx.message.embeds[0]
        embed.color = (
            0x9BF6FF
            if embed.fields[1].value == "建議"
            else 0xFFADAD
            if embed.fields[1].value == "錯誤回報"
            else 0xFDFFB6
        )
        await ctx.message.edit(components=components)
        await ctx.send("已取消釘選訊息！", ephemeral=True)

    @extension_component("feedback_handled")
    async def _feedback_handled(self, ctx: ComponentContext):
        if ctx.user.id != self.client.me.owner.id:
            return await ctx.send(":x: 你不是我的開發者！你不可以使用此按鈕。", ephemeral=True)
        if ctx.message.pinned:
            await ctx.message.unpin()
        embed = ctx.message.embeds[0]
        embed.description = "已處理的使用者回饋"
        embed.color = 0xBDB2FF
        await ctx.message.edit(embeds=embed, components=[])
        await ctx.send("已處理訊息！", ephemeral=True)

    @extension_component("feedback_ignore")
    async def _feedback_ignore(self, ctx: ComponentContext):
        if ctx.user.id != self.client.me.owner.id:
            return await ctx.send(":x: 你不是我的開發者！你不可以使用此按鈕。", ephemeral=True)
        if ctx.message.pinned:
            await ctx.message.unpin()
        embed = ctx.message.embeds[0]
        embed.description = "已略過的使用者回饋"
        embed.color = 0x000000
        await ctx.message.edit(embeds=embed, components=[])
        await ctx.send("已略過訊息！", ephemeral=True)

    @extension_persistent_component("feedback_block")
    async def _feedback_block(self, ctx: ComponentContext, package):
        if ctx.user.id != self.client.me.owner.id:
            return await ctx.send(":x: 你不是我的開發者！你不可以使用此按鈕。", ephemeral=True)
        await ctx.send(
            "你確定要封鎖這個使用者嗎？",
            components=[
                ActionRow(
                    components=[
                        Button(
                            label="確定",
                            custom_id=str(
                                PersistentCustomID(
                                    self.client,
                                    "feedback_block_confirm",
                                    [package, int(ctx.message.id)],
                                )
                            ),
                            style=ButtonStyle.DANGER,
                        ),
                        Button(
                            label="取消",
                            custom_id="feedback_block_cancel",
                            style=ButtonStyle.SECONDARY,
                        ),
                    ]
                )
            ],
            ephemeral=True,
        )

    @extension_component("feedback_block_cancel")
    async def _feedback_block_cancel(self, ctx: ComponentContext):
        if ctx.user.id != self.client.me.owner.id:
            return await ctx.send(":x: 你不是我的開發者！你不可以使用此按鈕。", ephemeral=True)
        await ctx.defer(edit_origin=True)
        await ctx.edit("已取消！", components=[])

    @extension_persistent_component("feedback_block_confirm")
    async def _feedback_block_confirm(self, ctx: ComponentContext, package):
        if ctx.user.id != self.client.me.owner.id:
            return await ctx.send(":x: 你不是我的開發者！你不可以使用此按鈕。", ephemeral=True)
        await ctx.defer(edit_origin=True)
        async with aiosqlite.connect("./storage/storage.db") as db:
            async with db.execute(
                f"SELECT * FROM feedback_blocked WHERE user={package[0]}"
            ) as cursor:
                data = [i async for i in cursor]
            if data:
                await ctx.edit("這個使用者已經被封鎖了！", components=[])
            else:
                await db.execute(
                    "INSERT INTO feedback_blocked (`user`, `time`) VALUES (?, ?)",
                    (package[0], datetime.utcnow()),
                )
                await db.commit()
                await ctx.edit("已封鎖使用者！", components=[])
        msg = Message(**await self.client._http.get_message(ctx.channel_id, package[1]))
        msg._client = self.client._http
        embed = msg.embeds[0]
        embed.description = "已被封鎖的使用者"
        embed.color = 0xFF0000
        components = [
            Button(
                label="解除封鎖",
                custom_id=str(PersistentCustomID(self.client, "feedback_unblock", package[0])),
                style=ButtonStyle.DANGER,
                emoji=Emoji(name="🚨"),
            )
        ]
        await msg.edit(embeds=embed, components=components)

    @extension_persistent_component("feedback_unblock")
    async def _feedback_unblock(self, ctx: ComponentContext, package):
        if ctx.user.id != self.client.me.owner.id:
            return await ctx.send(":x: 你不是我的開發者！你不可以使用此按鈕。", ephemeral=True)
        await ctx.send(
            "你確定要解除封鎖這個使用者嗎？",
            components=[
                ActionRow(
                    components=[
                        Button(
                            label="確定",
                            custom_id=str(
                                PersistentCustomID(
                                    self.client,
                                    "feedback_unblock_confirm",
                                    [package, int(ctx.message.id)],
                                )
                            ),
                            style=ButtonStyle.DANGER,
                        ),
                        Button(
                            label="取消",
                            custom_id="feedback_unblock_cancel",
                            style=ButtonStyle.SECONDARY,
                        ),
                    ]
                )
            ],
            ephemeral=True,
        )

    @extension_component("feedback_unblock_cancel")
    async def _feedback_unblock_cancel(self, ctx: ComponentContext):
        if ctx.user.id != self.client.me.owner.id:
            return await ctx.send(":x: 你不是我的開發者！你不可以使用此按鈕。", ephemeral=True)
        await ctx.defer(edit_origin=True)
        await ctx.edit("已取消！", components=[])

    @extension_persistent_component("feedback_unblock_confirm")
    async def _feedback_unblock_confirm(self, ctx: ComponentContext, package):
        if ctx.user.id != self.client.me.owner.id:
            return await ctx.send(":x: 你不是我的開發者！你不可以使用此按鈕。", ephemeral=True)
        await ctx.defer(edit_origin=True)
        async with aiosqlite.connect("./storage/storage.db") as db:
            async with db.execute(
                f"SELECT * FROM feedback_blocked WHERE user={package[0]}"
            ) as cursor:
                data = [i async for i in cursor]
            if not data:
                await ctx.edit("這個使用者沒有被封鎖！", components=[])
            else:
                await db.execute(f"DELETE FROM feedback_blocked WHERE user={package[0]}")
                await db.commit()
                await ctx.edit("已解除封鎖使用者！", components=[])
        msg = Message(**await self.client._http.get_message(ctx.channel_id, package[1]))
        msg._client = self.client._http
        embed = msg.embeds[0]
        embed.description = "已被解除封鎖的使用者"
        embed.color = 0x000000
        components = [
            Button(
                label="封鎖",
                custom_id=str(PersistentCustomID(self.client, "feedback_block", package[0])),
                style=ButtonStyle.DANGER,
                emoji=Emoji(name="🚨"),
            )
        ]
        await msg.edit(embeds=embed, components=components)

    @extension_listener()
    async def on_message_create(self, message: Message):
        if (
            message.type == MessageType.CHANNEL_PINNED_MESSAGE
            and message.channel_id == 1032089392333992047
            and message.author.id == self.client.me.id
        ):
            await message.delete()


def setup(client, **kwargs):
    feedback(client, **kwargs)
