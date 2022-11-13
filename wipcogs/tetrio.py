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

import tetr_emoji

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

        user_url = f"https://ch.tetr.io/u/{name.lower()}"
        data = resp["data"]["user"]
        join = (
            math.trunc(
                datetime.strptime(data["ts"][:-5], "%Y-%m-%dT%H:%M:%S")
                .replace(tzinfo=timezone.utc)
                .timestamp()
            )
            if "ts" in data
            else None
        )
        flags = f":flag_{data['country'].lower()}:" if data["country"] else ""
        role = data["role"]
        avatar = (
            f"https://tetr.io/user-content/avatars/{data['_id']}.jpg?rv={data['avatar_revision']}"
            if "avatar_revision" in data
            else "https://tetr.io/res/avatar.png"
        )

        title = f"{flags} {name.upper()}"
        if data.get("verified", None):
            title += " <:verified:1041078930184085605>"
        if data.get("supporter", None):
            for _ in range(data["supporter_tier"]):
                title += " <:support:104107892853992253>"

        badges = tetr_emoji.badges(data["badges"]) if data["badges"] else ""

        embed = Embed(
            title=title,
            description=f"以下是 TETR.IO 玩家 {name.upper()} 的相關資訊喔！",
            url=user_url,
            author=EmbedAuthor(
                name="TETR.IO 玩家查詢結果",
                icon_url="https://pbs.twimg.com/profile_images/1286993509573169153/pN9ULwc6_400x400.jpg",
            ),
            thumbnail=EmbedImageStruct(url=avatar),
            color=0x985FE2,
            fields=[EmbedField(name="玩家簡介", value=data["bio"])] if "bio" in data else [],
        )

        if role not in ["banned"]:
            embed.add_field(
                f"基本資料 | {data['xp']} XP",
                value=f"""遊玩時數: {math.trunc(data['gametime']/3600) if data['gametime'] != -1 else "*隱藏*"}\n多人遊玩次數: {data['gamesplayed'] if data['gamesplayed'] != -1 else "*隱藏*"}\n多人獲勝次數: {data['gameswon'] if data['gameswon'] != -1 else "*隱藏*"}\n好友: {data['friend_count']}""",
            )

            if role not in ["bot", "anon"]:
                league = data["league"]
                embed.add_field(
                    "TETRA LEAGUE",
                    value=f"""{tetr_emoji.rank(league['rank'])} ({int(league['rating'])} TR) :globe_with_meridians: {league["standing"] if league["standing"] != -1 else "N/A"} / {flags} {league["standing_local"] if league["standing_local"] != -1 else "N/A"}\n獲勝次數: {league["gameswon"]}/{league["gamesplayed"]} ({round((league["gameswon"]/league["gamesplayed"])*100, 2)}%){f"{_skipline}Glicko: {round(league['glicko'], 2)}±{round(league['rd'], 2)}" if 'glicko' in league and 'rd' in league else ""}{f"{_skipline}apm: {league['apm']} | pps: {league['pps']} | vs: {league['vs']}" if 'apm' in league and 'pps' in league and 'vs' in league else ""}""",
                )

                async with aiohttp.ClientSession() as s, s.get(
                    f"https://ch.tetr.io/api/users/{name.lower()}/records"
                ) as r:
                    resp = await r.json()
                    _40l = resp["data"]["records"]["40l"]
                    blitz = resp["data"]["records"]["blitz"]
                    zen = resp["data"]["zen"]

                embed.add_field(
                    "個人紀錄",
                    value=f"""40L: {f"{math.trunc(_40l['record']['endcontext']['finalTime'] / 3600000)}:{'%02d' % math.trunc(_40l['record']['endcontext']['finalTime'] % 3600000 / 60000)}:{'%02d' % (_40l['record']['endcontext']['finalTime'] / 1000 % 60)} {f'''(世界排行: {_40l['rank'] or '不適用'})''' if _40l['record'] else ''}" if _40l else "沒有紀錄"}\nBlitz: {f"{blitz['record']['endcontext']['score']} {f'''(世界排行: {blitz['rank'] or '不適用'})'''}" if blitz['record'] else "沒有紀錄"}\nzen: {zen['score']} (等級 {zen['level']})\n{badges}""",
                )

        embed.add_field(
            "其他資料",
            value=f"""創建時間: {f"<t:{join}:F>" if 'ts' in data else '未知'}{f'{_skipline}擁有者: {data["botmaster"]}' if role == 'bot' else ""}""",
        )

        await ctx.send(embeds=embed)


def setup(client, **kwargs):
    Tetrio(client, **kwargs)
