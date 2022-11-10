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
from typing import List

from interactions import (
    Channel,
    ChannelType,
    CommandContext,
    Guild,
    LibraryException,
    Modal,
    Permissions,
    TextInput,
    TextStyleType,
    extension_command,
    extension_listener,
    get,
    option,
)
from interactions.ext.lavalink import VoiceClient, VoiceState
from interactions.ext.persistence import (
    PersistenceExtension,
    PersistentCustomID,
    extension_persistent_modal,
)
from loguru._logger import Logger

newline = "\n"


class dvc(PersistenceExtension):
    def __init__(self, client, **kwargs):
        self.client: VoiceClient = client
        self.logger: Logger = kwargs.get("logger")
        self.db = kwargs.get("db")
        self._dvc = self.db.dvc
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

    # TODO: Consider rework (setup)
    @extension_listener()
    async def on_voice_state_update(self, before: VoiceState, after: VoiceState):
        if after.joined:
            document = await self._dvc.find_one({"_id": int(after.guild_id)})
            if document and int(after.channel_id) == document["lobby"]:
                g = await get(self.client, Guild, object_id=after.guild_id)
                name = document["format"].replace("{{MEMBER}}", after.member.name)
                c = await g.create_channel(
                    name if len(name) <= 32 else f"{name[:29]}...",
                    type=ChannelType.GUILD_VOICE,
                    parent_id=int(document["category"]),
                )
                try:
                    await self.client._http.modify_member(
                        int(after.member.id), int(after.guild_id), {"channel_id": int(c.id)}
                    )
                except LibraryException:
                    await c.delete()
        if before:
            voice_states = self.client.get_channel_voice_states(before.channel_id)
            if not voice_states or len(voice_states) == 0:
                document = await self._dvc.find_one({"_id": int(before.guild_id)})
                if document and before.channel_id:
                    if "keep" in document and int(before.channel_id) in document["keep"]:
                        return
                    channel = await before.get_channel()
                    if (
                        channel.parent_id
                        and int(channel.parent_id) == document["category"]
                        and int(channel.id) != document["lobby"]
                    ):
                        await channel.delete()

    @extension_command(dm_permission=False, default_member_permissions=Permissions.MANAGE_CHANNELS)
    async def dvc(self, *args, **kwargs):
        """Dynamic Voice Channel"""
        ...

    @dvc.subcommand()
    @option("動態語音大廳", channel_types=[ChannelType.GUILD_VOICE])
    @option("動態語音分類", channel_types=[ChannelType.GUILD_CATEGORY])
    async def settings(self, ctx: CommandContext, lobby: Channel, category: Channel):
        """設定動態語音頻道"""
        if not ctx.app_permissions.MANAGE_CHANNELS:
            return await ctx.send(":x: 我沒權限管理頻道 ;-;", ephemeral=True)
        modal = Modal(
            title="設定動態語音",
            custom_id=str(
                PersistentCustomID(self.client, "dvc_settings", [int(lobby.id), int(category.id)])
            ),
            components=[
                TextInput(
                    style=TextStyleType.SHORT,
                    custom_id="dvc_settings_name",
                    label="頻道名稱格式",
                    required=True,
                    placeholder="請輸入頻道名稱格式\n可用參數: {{MEMBER}} 使用者名稱",
                    value="{{MEMBER}} 的語音頻道",
                )
            ],
        )
        await ctx.popup(modal)

    @dvc.subcommand()
    async def reset(self, ctx: CommandContext):
        """重置動態語音"""
        await ctx.defer(ephemeral=True)
        if not await self._dvc.find_one({"_id": int(ctx.guild_id)}, {"_id": 1}):
            return await ctx.send(
                f":x: baka 我印象中好像還沒有幫這個伺服器設定 動態語音 喔！\n請用 </dvc settings:{self.client._find_command('dvc').id}> 來設定 動態語音",
                ephemeral=True,
            )
        await self._dvc.delete_one({"_id": int(ctx.guild_id)})
        await ctx.send(
            f":white_check_mark: 我幫你重置了 動態語音 設定！你可以用 </dvc settings:{self.client._find_command('dvc').id}> 來再次設定 動態語音。",
            ephemeral=True,
        )

    @dvc.subcommand()
    @option("要保留的語音頻道", channel_types=[ChannelType.GUILD_VOICE])
    async def keep(self, ctx: CommandContext, channel: Channel):
        """保留語音頻道 (防止被刪除)"""
        document = await self._dvc.find_one({"_id": int(ctx.guild_id)}, {"keep": 1, "_id": 1})
        if not document:
            return await ctx.send(
                f":x: baka 我印象中好像還沒有幫這個伺服器設定 動態語音 喔！\n請用 </dvc settings:{self.client._find_command('dvc').id}> 來設定 動態語音。",
                ephemeral=True,
            )
        if "keep" in document:
            if int(channel.id) in document["keep"]:
                return await ctx.send(":x: baka 這個語音頻道已經被保留了喔！", ephemeral=True)
            else:
                document["keep"].append(int(channel.id))
        else:
            document["keep"] = [int(channel.id)]
        await self._dvc.update_one(
            {"_id": int(ctx.guild_id)}, {"$set": {"keep": document["keep"]}}, upsert=True
        )
        await ctx.send(
            f":white_check_mark: 我幫你保留了 {channel.mention} 這個語音頻道！現在它不會被我不小心刪除了！", ephemeral=True
        )

    @extension_persistent_modal("dvc_settings")
    async def _dvc_settings(self, ctx: CommandContext, package: List[int], dvc_settings_name: str):
        await ctx.send(
            f"我會把設定記住的！\n你可以隨時用 </dvc settings:{self.client._find_command('dvc').id}> 回來修改設定喔！",
            ephemeral=True,
        )
        await self._dvc.replace_one(
            {"_id": int(ctx.guild_id)},
            {"lobby": package[0], "category": package[1], "format": dvc_settings_name},
            upsert=True,
        )


def setup(client, **kwargs):
    dvc(client, **kwargs)
