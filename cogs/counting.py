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

import ast
import operator as op
import os

import aiosqlite
from interactions import (
    ActionRow,
    Button,
    ButtonStyle,
    Channel,
    Client,
    CommandContext,
    ComponentContext,
    Message,
    Permissions,
    extension_command,
    extension_component,
    extension_listener,
    get,
    option,
)
from interactions.ext.persistence import (
    PersistenceExtension,
    PersistentCustomID,
    extension_persistent_component,
)
from loguru._logger import Logger

from utils import raweb

newline = "\n"

operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.BitXor: op.xor,
    ast.USub: op.neg,
}


def eval_expr(expr):
    return _eval_expr(ast.parse(expr, mode="eval").body)


def _eval_expr(node):
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        return operators[type(node.op)](_eval_expr(node.left), _eval_expr(node.right))
    elif isinstance(node, ast.UnaryOp):
        return operators[type(node.op)](_eval_expr(node.operand))
    else:
        raise TypeError(node)


class counting(PersistenceExtension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.logger: Logger = kwargs.get("logger")
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

    @extension_listener()
    async def on_message_create(self, msg: Message):
        if not msg.content or (msg.author and msg.author.bot):
            return
        for i in msg.content:
            if i not in "0123456789+-*/^":
                return
        async with aiosqlite.connect("./storage/storage.db") as db:
            async with db.execute(
                f"SELECT * FROM counting WHERE channel={msg.channel_id}"
            ) as cursor:
                data = [i async for i in cursor]
            if not data or data[0][1] != msg.channel_id:
                return
            try:
                value = eval_expr(msg.content)
            except (TypeError, ZeroDivisionError):
                return
            if data[0][3] != 0 and data[0][2] and data[0][2] == msg.author.id:
                await msg.create_reaction("❌")
                await msg.reply("錯了！你不能連續數兩次！從 **1** 開始吧！")
                value = 0
            elif round(value) != data[0][3] + 1:
                await msg.create_reaction("❌")
                if data[0][3] == 0:
                    await msg.reply("請從 **1** 開始數數字!")
                else:
                    await msg.reply(f"錯了！下個數字是 **{data[0][3] + 1}**！從 **1** 開始吧！")
                value = 0
            else:
                await msg.create_reaction("✅")
            await db.execute(
                f"UPDATE counting SET user={int(msg.author.id)}, count={value} WHERE channel={msg.channel_id}"
            )
            await db.commit()

    @extension_listener()
    async def on_message_delete(self, msg: Message):
        if not msg.content or (msg.author and msg.author.bot):
            return
        for i in msg.content:
            if i not in "0123456789+-*/^":
                return
        async with aiosqlite.connect("./storage/storage.db") as db:
            async with db.execute(
                f"SELECT * FROM counting WHERE channel={msg.channel_id}"
            ) as cursor:
                data = [i async for i in cursor]
            if not data or data[0][1] != msg.channel_id:
                return
            try:
                value = eval_expr(msg.content)
            except (TypeError, ZeroDivisionError):
                return
            if round(value) == data[0][3]:
                await (await msg.get_channel()).send(
                    embeds=raweb(
                        "抓到了喔！", f"{msg.author.mention} 還想刪訊息害人喔...\n下個數字是 **{data[0][3] + 1}** 啦！"
                    )
                )

    @extension_command(dm_permission=False)
    async def counting(self, *args, **kwargs):
        ...

    @counting.subcommand()
    @option("要設定的頻道")
    async def settings(self, ctx: CommandContext, channel: Channel = None):
        """數數字遊戲的設定"""
        if not channel:
            channel = await ctx.get_channel()
        if not await ctx.has_permissions(Permissions.MANAGE_CHANNELS):
            return await ctx.send(":x: baka 你沒有權限使用這個指令喔！", ephemeral=True)
        async with aiosqlite.connect("./storage/storage.db") as db:
            async with db.execute(f"SELECT * FROM counting WHERE guild={ctx.guild_id}") as cursor:
                data = [i async for i in cursor]
            if data:
                components = [
                    ActionRow(
                        components=[
                            Button(
                                label="確定",
                                custom_id=str(
                                    PersistentCustomID(
                                        self.client, "overwrite_confirm", str(channel.id)
                                    )
                                ),
                                style=ButtonStyle.DANGER,
                            ),
                            Button(
                                label="取消", custom_id="counting_cancel", style=ButtonStyle.SECONDARY
                            ),
                        ]
                    )
                ]
                return await ctx.send(
                    "我幫這個伺服器設定過數數字遊戲了！\n要覆蓋設定嗎？現時的進度會消失喔。", components=components, ephemeral=True
                )
            await db.execute(
                f"INSERT OR IGNORE INTO counting VALUES ({ctx.guild_id}, {channel.id}, null, 0)"
            )
            await db.execute(
                f"UPDATE counting SET channel={channel.id}, user=null, count=0 WHERE guild={ctx.guild_id}"
            )
            await db.commit()
            await ctx.send(f"數數字遊戲的設定已經完成了喔！請在 {channel.mention} 頻道裡面開始數數字吧！", ephemeral=True)

    @counting.subcommand()
    async def stop(self, ctx: CommandContext):
        """停止數數字遊戲"""
        if not await ctx.has_permissions(Permissions.MANAGE_CHANNELS):
            return await ctx.send(":x: baka 你沒有權限使用這個指令喔！", ephemeral=True)
        async with aiosqlite.connect("./storage/storage.db") as db:
            async with db.execute(f"SELECT * FROM counting WHERE guild={ctx.guild_id}") as cursor:
                data = [i async for i in cursor]
            if not data:
                return await ctx.send(
                    f":x: baka 我印象中好像還沒有幫這個伺服器設定 數數字遊戲 喔！\n請用 </counting settings:{self.client._find_command('counting').id}> 來設定 數數字遊戲。",
                    ephemeral=True,
                )
        components = [
            ActionRow(
                components=[
                    Button(label="確定", custom_id="stop_confirm", style=ButtonStyle.DANGER),
                    Button(label="取消", custom_id="counting_cancel", style=ButtonStyle.SECONDARY),
                ]
            )
        ]
        await ctx.send("你確定要停止數數字遊戲嗎？現時的進度會消失喔。", components=components, ephemeral=True)

    @counting.subcommand()
    async def current(self, ctx: CommandContext):
        """查看目前的數字"""
        async with aiosqlite.connect("./storage/storage.db") as db:
            async with db.execute(f"SELECT * FROM counting WHERE guild={ctx.guild_id}") as cursor:
                data = [i async for i in cursor]
            if not data:
                return await ctx.send(
                    f"baka 我印象中好像還沒有幫這個伺服器設定 數數字遊戲 喔！\n請用 </counting settings:{self.client._find_command('counting').id}> 來設定 數數字遊戲。",
                    ephemeral=True,
                )
            await ctx.send(embeds=raweb("忘記了嗎？", f"下個數字是 **{data[0][3] + 1}** 啦！"))

    @extension_persistent_component("overwrite_confirm")
    async def _overwrite_confirm(self, ctx: ComponentContext, package):
        channel = await get(self.client, Channel, object_id=int(package))
        async with aiosqlite.connect("./storage/storage.db") as db:
            await db.execute(
                f"INSERT OR IGNORE INTO counting VALUES ({ctx.guild_id}, {channel.id}, null, 0)"
            )
            await db.execute(
                f"UPDATE counting SET channel={channel.id}, user=null, count=0 WHERE guild={ctx.guild_id}"
            )
            await db.commit()
            await ctx.send(f"數數字遊戲的設定已經完成了喔！請在 {channel.mention} 頻道裡面開始數數字吧！", ephemeral=True)

    @extension_component("stop_confirm")
    async def _stop_confirm(self, ctx: ComponentContext):
        await ctx.defer(edit_origin=True)
        async with aiosqlite.connect("./storage/storage.db") as db:
            await db.execute(f"DELETE FROM counting WHERE guild={ctx.guild_id}")
            await db.commit()
        await ctx.edit(
            f"我幫你停止了 數數字遊戲。\n你可以用 </counting settings:{self.client._find_command('counting').id}> 來再次設定 數數字遊戲。",
            components=[],
        )

    @extension_component("counting_cancel")
    async def _counting_cancel(self, ctx: ComponentContext):
        await ctx.defer(edit_origin=True)
        await ctx.edit("好的！", components=[])


def setup(client, **kwargs):
    counting(client, **kwargs)
