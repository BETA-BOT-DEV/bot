import math
import os
from datetime import datetime, timezone

import aiohttp
from interactions import (
    CommandContext,
    Embed,
    EmbedAuthor,
    EmbedField,
    EmbedImageStruct,
    Extension,
    extension_command,
    option,
)
from loguru._logger import Logger

_skipline = "\n"


class Tetrio(Extension):
    def __init__(self, client, **kwargs):
        self.client = client
        self.logger: Logger = kwargs.get("logger")
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

    @extension_command()
    async def tetrio(self, *args, **kwargs):
        ...

    @tetrio.subcommand()
    @option(description="玩家名稱")
    async def user(self, ctx: CommandContext, name: str):
        """查詢TETR.IO玩家資訊"""
        async with aiohttp.ClientSession() as s, s.get(
            f"https://ch.tetr.io/api/users/{name.lower()}"
        ) as r:
            resp = await r.json()
            if not resp["success"]:
                return await ctx.send(f":x: baka 我找不到 {name} 啦！", ephemeral=True)
            data = resp["data"]["user"]
            avatarRevision = data.get("avatar_revision", None)

        embed = Embed(
            title="TETR.IO 玩家查詢結果",
            description=f"以下是 TETR.IO 玩家 {name.upper()} 的相關資訊喔！",
            author=EmbedAuthor(
                name=f"{name.upper()}",
                icon_url=f"https://tetr.io/user-content/avatars/{data['_id']}.jpg?rv={avatarRevision}"
                if avatarRevision
                else "https://pbs.twimg.com/profile_images/1286993509573169153/pN9ULwc6_400x400.jpg",
                url=f"https://ch.tetr.io/u/{data['username']}",
            ),
            thumbnail=EmbedImageStruct(
                url=f"https://tetr.io/user-content/avatars/{data['_id']}.jpg?rv={avatarRevision}"
            )
            if avatarRevision
            else None,
            color=0x985FE2,
            fields=[EmbedField(name="玩家簡介", value=data["bio"])] if "bio" in data else [],
        )

        embed.add_field(
            "玩家資料",
            value=f"""創建時間: {f"<t:{math.trunc(datetime.strptime(data['ts'][:-5], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc).timestamp())}:F>" if 'ts' in data else '未知'}\n身份組: {({'banned': "被封禁玩家", 'bot': "機器人", 'anon': "匿名玩家", "user": "玩家"})[(role:=data['role'])]}{f'{_skipline}擁有者: {data["botmaster"]}' if role == 'bot' else ""}{f'{_skipline}地區: {data["country"]}' if 'country' in data and data['country'] else ""}{f"{_skipline}Supporter: {'是' if 'supporter' in data and data['supporter'] else '否'}" if role not in ['bot', 'banned', 'anon'] else ""}{f"{_skipline}已驗證: {'是' if 'verified' in data and data['verified'] else '否'}" if role not in ['bot', 'banned', 'anon'] else ""}""",
        )

        if role not in ["banned"]:
            embed.add_field(
                f"基本資料 | {data['xp']} XP",
                value=f"""遊玩時數: {math.trunc(data['gametime']/3600) if data['gametime'] != -1 else "*隱藏*"}\n多人遊玩次數: {data['gamesplayed'] if data['gamesplayed'] != -1 else "*隱藏*"}\n多人獲勝次數: {data['gameswon'] if data['gameswon'] != -1 else "*隱藏*"}\n好友: {data['friend_count']}""",
            )

            if role not in ["bot", "anon"]:
                async with aiohttp.ClientSession() as s, s.get(
                    f"https://ch.tetr.io/api/users/{name.lower()}/records"
                ) as r:
                    resp = await r.json()
                    _40l = resp["data"]["records"]["40l"]
                    blitz = resp["data"]["records"]["blitz"]
                    zen = resp["data"]["zen"]

                embed.add_field(
                    f"""TETRA LEAGUE | {f"{league['rank'].upper() if league['rank'].lower() != 'z' else 'Unranked'} {round(league['rating'], 2)}" if (league:=data['league'])['rating'] != -1 else "Unknown"} TR""",
                    value=f"""獲勝次數: {league["gameswon"]}/{league["gamesplayed"]} ({round((league["gameswon"]/league["gamesplayed"])*100, 2)}%)\n世界排行: {league["standing"] if league["standing"] != -1 else "N/A"} | 地區排名: {league["standing_local"] if league["standing_local"] != -1 else "N/A"}{f"{_skipline}Glicko: {round(league['glicko'], 2)}±{round(league['rd'], 2)}" if 'glicko' in league and 'rd' in league else ""}{f"{_skipline}apm: {league['apm']} | pps: {league['pps']} | vs: {league['vs']}" if 'apm' in league and 'pps' in league and 'vs' in league else ""}""",
                )

                embed.add_field(
                    "其他紀錄",
                    value=f"""40L: {f"{math.trunc(_40l['record']['endcontext']['finalTime'] / 3600000)}:{'%02d' % math.trunc(_40l['record']['endcontext']['finalTime'] % 3600000 / 60000)}:{'%02d' % (_40l['record']['endcontext']['finalTime'] / 1000 % 60)} {f'''(世界排行: {_40l['rank'] or '不適用'})''' if _40l['record'] else ''}" if _40l else "沒有紀錄"}\nBlitz: {f"{blitz['record']['endcontext']['score']} {f'''(世界排行: {blitz['rank'] or '不適用'})'''}" if blitz['record'] else "沒有紀錄"}\nzen: {zen['score']} (等級 {zen['level']})""",
                )

        await ctx.send(embeds=embed)


def setup(client, **kwargs):
    Tetrio(client, **kwargs)
