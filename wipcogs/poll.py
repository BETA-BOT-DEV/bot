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

import asyncio
import os
from contextlib import suppress
from random import randint
from typing import List

from interactions import (
    ActionRow,
    Attachment,
    Button,
    ButtonStyle,
    Client,
    CommandContext,
    ComponentContext,
    ComponentType,
    Embed,
    EmbedField,
    EmbedFooter,
    LibraryException,
    Message,
    Modal,
    Role,
    SelectMenu,
    SelectOption,
    TextInput,
    TextStyleType,
    extension_command,
    extension_component,
    extension_modal,
    get,
    option,
)
from interactions.ext.persistence import (
    PersistenceExtension,
    PersistentCustomID,
    extension_persistent_component,
    extension_persistent_modal,
)
from loguru._logger import Logger

newline = "\n"

setting = [
    ActionRow(
        components=[
            SelectMenu(
                custom_id="poll_config",
                placeholder="修改投票設定",
                options=[
                    SelectOption(label="基礎設定", value="type", description="更改投票問題、描述或選項"),
                    SelectOption(label="身份組設定", value="role", description="更改身份組限制、提及身份組"),
                    SelectOption(label="其他設定", value="other", description="更改公開投票、每個用戶可選項數"),
                ],
            )
        ]
    ),
    ActionRow(
        components=[
            Button(style=ButtonStyle.PRIMARY, label="確認", custom_id="poll_confirm"),
            Button(style=ButtonStyle.DANGER, label="取消", custom_id="poll_cancel"),
        ]
    ),
]


class poll(PersistenceExtension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.logger: Logger = kwargs.get("logger")
        self.db = kwargs.get("db")
        self._poll = self.db.poll
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

    @extension_command(dm_permission=False)
    async def poll(self, *args, **kwargs):
        """投票指令"""
        ...

    @poll.subcommand()
    @option("投票問題", max_length=256)
    @option("問題描述")
    @option("選項 (以逗號分隔)", max_length=1024)
    @option("圖片")
    @option("限制身份組")
    @option("提及身份組")
    @option("公開投票")
    @option("每個用戶可選項數")
    async def create(
        self,
        ctx: CommandContext,
        question: str,
        description: str = "",
        options: str = "",
        image: Attachment = None,
        limit: Role = None,
        mention: Role = None,
        public: bool = False,
        multiple: int = 1,
    ):
        """發起投票"""
        await ctx.defer()
        oplist = options.split(",") if options and "," in options else ["是", "否"]
        embed = Embed(
            title="投票設定",
            description="請確認以下設定是否正確",
            fields=[
                EmbedField(name="問題", value=question, inline=False),
                EmbedField(
                    name="描述", value=description if description else "*[沒有填寫]*", inline=False
                ),
                EmbedField(
                    name="選項",
                    value="".join([f"{i+1}. {v}\n" for i, v in enumerate(oplist)]),
                    inline=False,
                ),
                EmbedField(name="限制身份組", value=limit.mention if limit else "沒有身份組限制", inline=False),
                EmbedField(
                    name="提及身份組", value=mention.mention if mention else "沒有提及身份組", inline=False
                ),
                EmbedField(name="公開投票", value="是" if public else "否", inline=False),
                EmbedField(
                    name="每個用戶可選項數", value=multiple if multiple <= len(oplist) else 1, inline=False
                ),
                EmbedField(
                    name="圖片",
                    value=image.url if image and "image" in image.content_type else "*[沒有填寫]*",
                    inline=False,
                ),
            ],
            color=randint(0, 0xFFFFFF),
            footer=EmbedFooter(text="如需修改圖片，請取消並重新發起投票。"),
        )
        await ctx.send(embeds=embed, components=setting)

    @extension_component("poll_confirm")
    async def _poll_confirm(self, ctx: ComponentContext):  # TODO: Not implemented
        ...

    @extension_component("poll_cancel")
    async def _poll_cancel(self, ctx: ComponentContext):
        if ctx.author.id != ctx.message.interaction.user.id:
            return await ctx.send(":x: baka 你不是這個投票的發起人！", ephemeral=True)
        await ctx.message.edit("我幫你取消了這次的投票！", embeds=[], components=[])
        await asyncio.sleep(3)
        with suppress(LibraryException):
            await ctx.message.delete()

    @extension_component("poll_config")
    async def _poll_config(self, ctx: ComponentContext, selected: List[str]):
        if ctx.author.id != ctx.message.interaction.user.id:
            return await ctx.send(":x: baka 你不是這個投票的發起人！", ephemeral=True)
        match selected:
            case "type":
                modal = Modal(
                    custom_id="poll_config_type",
                    title="基礎設定",
                    components=[
                        TextInput(
                            style=TextStyleType.SHORT,
                            label="問題",
                            custom_id="question",
                            placeholder="請輸入投票問題",
                            max_length=256,
                            value=ctx.message.embeds[0].fields[0].value,
                        ),
                        TextInput(
                            style=TextStyleType.PARAGRAPH,
                            label="描述",
                            custom_id="description",
                            placeholder="請輸入投票描述",
                            max_length=1024,
                            value=""
                            if ctx.message.embeds[0].fields[1].value == "*[沒有填寫]*"
                            else ctx.message.embeds[0].fields[1].value,
                            required=False,
                        ),
                        TextInput(
                            style=TextStyleType.SHORT,
                            label="選項 (以逗號分隔)",
                            custom_id="options",
                            placeholder="請輸入投票選項",
                            max_length=1024,
                            value=",".join(
                                [
                                    v.split(". ")[1]
                                    for v in ctx.message.embeds[0].fields[2].value.split("\n")
                                ]
                            ),
                            required=False,
                        ),
                    ],
                )
                await ctx.popup(modal)
            case "role":
                components = [
                    ActionRow(
                        components=[
                            SelectMenu(
                                type=ComponentType.ROLE_SELECT,
                                custom_id=str(
                                    PersistentCustomID(
                                        self.client, "poll_config_role_limit", int(ctx.message.id)
                                    )
                                ),
                                placeholder="限制身份組",
                                max_values=1,
                                min_values=0,
                            )
                        ]
                    ),
                    ActionRow(
                        components=[
                            SelectMenu(
                                type=ComponentType.ROLE_SELECT,
                                custom_id=str(
                                    PersistentCustomID(
                                        self.client, "poll_config_role_mention", int(ctx.message.id)
                                    )
                                ),
                                placeholder="提及身份組",
                                max_values=1,
                                min_values=0,
                            )
                        ]
                    ),
                    ActionRow(
                        components=[
                            Button(
                                style=ButtonStyle.PRIMARY,
                                label="清除選擇",
                                custom_id=str(
                                    PersistentCustomID(
                                        self.client, "poll_config_role_clear", int(ctx.message.id)
                                    )
                                ),
                            )
                        ]
                    ),
                ]
                await ctx.send("身份組設定 (上: 限制 | 下: 提及)", components=components, ephemeral=True)
            case "other":
                components = [
                    ActionRow(
                        components=[
                            SelectMenu(
                                custom_id=str(
                                    PersistentCustomID(
                                        self.client, "poll_config_other_public", int(ctx.message.id)
                                    )
                                ),
                                placeholder="公開投票",
                                max_values=1,
                                min_values=1,
                                options=[
                                    SelectOption(label="公開投票: 是", value="True"),
                                    SelectOption(label="公開投票: 否", value="False"),
                                ],
                            )
                        ]
                    ),
                    ActionRow(
                        components=[
                            Button(
                                style=ButtonStyle.PRIMARY,
                                label="修改每個用戶可選項數",
                                custom_id=str(
                                    PersistentCustomID(
                                        self.client,
                                        "poll_config_other_multiple",
                                        int(ctx.message.id),
                                    )
                                ),
                            )
                        ]
                    ),
                ]
                await ctx.send(
                    "其他設定 (上: 公開投票 | 下: 每個用戶可選項數)", components=components, ephemeral=True
                )

    @extension_modal("poll_config_type")
    async def _poll_config_type(
        self, ctx: ComponentContext, question: str, description: str, options: str
    ):
        oplist = options.split(",") if options and "," in options else ["是", "否"]
        ctx.message.embeds[0].fields[0].value = question
        ctx.message.embeds[0].fields[1].value = description if description else "*[沒有填寫]*"
        ctx.message.embeds[0].fields[2].value = "".join(
            [f"{i+1}. {v}\n" for i, v in enumerate(oplist)]
        )
        embed = Embed(**ctx.message.embeds[0]._json)
        await ctx.message.edit(embeds=embed, components=setting)
        await ctx.send("我記住了新的投票設定！", ephemeral=True)

    @extension_persistent_component("poll_config_role_limit")
    async def _poll_config_role_limit(self, ctx: ComponentContext, package):
        await ctx.defer(edit_origin=True)
        message = await get(self.client, Message, object_id=package, parent_id=ctx.channel_id)
        message.embeds[0].fields[3].value = (
            "沒有身份組限制" if len(ctx.data.values) == 0 else f"<@&{ctx.data.values[0]}>"
        )
        embed = Embed(**message.embeds[0]._json)
        await message.edit(embeds=embed, components=setting)
        await ctx.edit("我記住了新的投票設定！\n身份組設定 (上: 限制 | 下: 提及)")

    @extension_persistent_component("poll_config_role_mention")
    async def _poll_config_role_mention(self, ctx: ComponentContext, package):
        await ctx.defer(edit_origin=True)
        message = await get(self.client, Message, object_id=package, parent_id=ctx.channel_id)
        message.embeds[0].fields[4].value = (
            "沒有提及身份組" if len(ctx.data.values) == 0 else f"<@&{ctx.data.values[0]}>"
        )
        embed = Embed(**message.embeds[0]._json)
        await message.edit(embeds=embed, components=setting)
        await ctx.edit("我記住了新的投票設定！\n身份組設定 (上: 限制 | 下: 提及)")

    @extension_persistent_component("poll_config_role_clear")
    async def _poll_config_role_clear(self, ctx: ComponentContext, package):
        await ctx.defer(edit_origin=True)
        message = await get(self.client, Message, object_id=package, parent_id=ctx.channel_id)
        message.embeds[0].fields[3].value = "沒有身份組限制"
        message.embeds[0].fields[4].value = "沒有提及身份組"
        embed = Embed(**message.embeds[0]._json)
        await message.edit(embeds=embed, components=setting)
        await ctx.edit("我記住了新的投票設定！\n身份組設定 (上: 限制 | 下: 提及)")

    @extension_persistent_component("poll_config_other_public")
    async def _poll_config_other_public(self, ctx: ComponentContext, package):
        await ctx.defer(edit_origin=True)
        message = await get(self.client, Message, object_id=package, parent_id=ctx.channel_id)
        message.embeds[0].fields[5].value = "是" if ctx.data.values[0] == "True" else "否"
        embed = Embed(**message.embeds[0]._json)
        await message.edit(embeds=embed, components=setting)
        await ctx.edit("我記住了新的投票設定！\n其他設定 (上: 公開投票 | 下: 每個用戶可選項數)")

    @extension_persistent_component("poll_config_other_multiple")
    async def _poll_config_other_multiple(self, ctx: ComponentContext, package):
        modal = Modal(
            title="修改每個用戶可選項數",
            components=[
                TextInput(
                    style=TextStyleType.SHORT,
                    label="每個用戶可選項數",
                    custom_id=str(PersistentCustomID(self.client, "multiple", int(ctx.message.id))),
                )
            ],
            custom_id=str(
                PersistentCustomID(self.client, "poll_config_other_multiple_modal", int(package))
            ),
        )
        await ctx.popup(modal)

    @extension_persistent_modal("poll_config_other_multiple_modal")
    async def _poll_config_other_multiple_modal(self, ctx: CommandContext, package, multiple: str):
        message = await get(self.client, Message, object_id=package, parent_id=ctx.channel_id)
        if not multiple.isdigit() or int(multiple) > len(
            message.embeds[0].fields[2].value.split("\n")
        ):
            multiple = 1
            content = "baka 請輸入有效的數字！"
        else:
            content = "我記住了新的投票設定！"
        message.embeds[0].fields[6] = multiple
        embed = Embed(**message.embeds[0]._json)
        await message.edit(embeds=embed, components=setting)
        await ctx.send(content, ephemeral=True)


def setup(client, **kwargs):
    poll(client, **kwargs)
