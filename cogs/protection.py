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

from interactions import (
    ChannelType,
    Client,
    CommandContext,
    Extension,
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


class protect(Extension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.logger: Logger = kwargs.get("logger")
        self.db = kwargs.get("db")
        self._ping = self.db.ping
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

    @extension_listener()
    async def on_message_create(self, message: Message):
        if not (message.mention_everyone or message.mentions):
            return
        try:
            guild = await message.get_guild()
            channel = await message.get_channel()
            permissions = await channel.get_permissions_for(message.member)
        except:  # noqa: E722
            return
        if channel.type == ChannelType.DM:
            return
        pinged = []
        if message.mention_everyone and (
            Permissions.MENTION_EVERYONE in permissions or message.author.id == guild.owner_id
        ):
            for i in guild.members:
                if not i.user.bot and i.user.id != message.author.id:
                    if int(i.id) not in pinged:
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
                    "create": datetime.utcnow(),
                },
                upsert=True,
            )

    @extension_command()
    async def whopinged(self, ctx: CommandContext):
        """尋找12小時內最後在這個伺服器@你的人"""
        await ctx.defer(ephemeral=True)
        doc = await self._ping.find_one(
            {"user_id": int(ctx.author.id), "guild_id": int(ctx.guild_id)},
            {"_id": 0, "author": 1, "create": 1},
        )
        if not doc:
            return await ctx.send(":x: baka 最近12小時沒有人在這個伺服器@過你 (@role 暫不適用)")
        await ctx.send(
            embeds=raweb(
                "找到了！",
                f"最後一次在這個伺服器@你的人是 <@{doc['author']}>\nUTC時間是 {doc['create'].strftime('%Y-%m-%d %H:%M:%S')}",
            )
        )

    @extension_listener()
    async def on_message_delete(self, message: Message):
        if not message.mentions and not message.mention_everyone and not message.mention_roles:
            return
        everyone = False
        roles = []
        victims = []
        if message.mention_everyone:
            everyone = True
        if message.mention_roles:
            for i in message.mention_roles:
                role = await get(self.client, Role, object_id=int(i), parent_id=message.guild_id)
                if not role.managed:
                    roles.append(f"<@&{i}>")
        if message.mentions:
            for i in message.mentions:
                if ("bot" not in i or not i["bot"]) and i["id"] != str(message.author.id):
                    victims.append(f"<@{i['id']}>")
        if len(victims) == 0 and len(roles) == 0 and not everyone:
            return
        content = ""
        if everyone:
            content = "@everyone"
        else:
            content = ""
            if len(roles) > 0:
                content += "身份組: \n"
                content += "\n".join(roles)
            if len(victims) > 0:
                if content != "":
                    content += "\n\n"
                content += "成員: \n"
                content += "\n".join(victims)
        channel = await message.get_channel()
        await channel.send(
            embeds=raweb(
                "抓到 Ghost Ping 了！",
                desc=f"{message.author.mention} 這樣可不行喔！\n以下的受害者被Ghost ping了...\n\n{content}",
            )
        )


def setup(client, **kwargs):
    protect(client, **kwargs)
