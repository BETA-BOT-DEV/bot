import math
import os
from datetime import datetime, timezone

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
from tetry import api as tetrAPI

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
        try:
            user = await tetrAPI.getUser(name=name.lower())
            await ctx.defer(ephemeral=True)
        except Exception as e:
            if (
                e.args[0]
                != "No such user! | Either you mistyped something, or the account no longer exists."
            ):
                raise e
            else:
                user = None
        if not user:
            return await ctx.send(f":x: baka 我找不到 {name} 啦！", ephemeral=True)

        embed = Embed(
            title="TETR.IO 玩家查詢結果",
            description=f"以下是 TETR.IO 玩家 {name.upper()} 的相關資訊喔！",
            author=EmbedAuthor(
                name=f"{name.upper()}",
                icon_url=f"https://tetr.io/user-content/avatars/{user.id}.jpg?rv={user.avatarRevision}"
                if user.avatarRevision
                else "https://pbs.twimg.com/profile_images/1286993509573169153/pN9ULwc6_400x400.jpg",
                url=f"https://ch.tetr.io/u/{user.username}",
            ),
            thumbnail=EmbedImageStruct(
                url=f"https://tetr.io/user-content/avatars/{user.id}.jpg?rv={user.avatarRevision}"
            )
            if user.avatarRevision
            else None,
            color=0x985FE2,
            fields=[EmbedField(name="玩家簡介", value=user.data["bio"])] if "bio" in user.data else [],
        )

        embed.add_field(
            "玩家資料",
            value=f"""創建時間: {f"<t:{math.trunc(datetime.strptime(user.data['ts'][:-5], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc).timestamp())}:F>" if 'ts' in user.data else '未知'}\n身份組: {({'banned': "被封禁玩家", 'bot': "機器人", 'anon': "匿名玩家", "user": "玩家"})[(role:=user.data['role'])]}{f'{_skipline}擁有者: {user.data["botmaster"]}' if role == 'bot' else ""}{f'{_skipline}地區: {user.data["country"]}' if 'country' in user.data and user.data['country'] else ""}{f"{_skipline}Supporter: {'是' if 'supporter' in user.data and user.data['supporter'] else '否'}" if role not in ['bot', 'banned', 'anon'] else ""}{f"{_skipline}已驗證: {'是' if 'verified' in user.data and user.data['verified'] else '否'}" if role not in ['bot', 'banned', 'anon'] else ""}""",
        )

        if role not in ["banned"]:
            embed.add_field(
                f"基本資料 | {user.data['xp']} XP",
                value=f"""遊玩時數: {math.trunc(user.data['gametime']/3600) if user.data['gametime'] != -1 else "*隱藏*"}\n多人遊玩次數: {user.data['gamesplayed'] if user.data['gamesplayed'] != -1 else "*隱藏*"}\n多人獲勝次數: {user.data['gameswon'] if user.data['gameswon'] != -1 else "*隱藏*"}\n好友: {user.data['friend_count']}""",
            )

            if role not in ["bot", "anon"]:
                rc = await tetrAPI.getRecords(name=name.lower())
                embed.add_field(
                    f"""TETRA LEAGUE | {f"{league['rank'].upper() if league['rank'].lower() != 'z' else 'Unranked'} {round(league['rating'], 2)}" if (league:=user.data['league'])['rating'] != -1 else "Unknown"} TR""",
                    value=f"""獲勝次數: {league["gameswon"]}/{league["gamesplayed"]} ({round((league["gameswon"]/league["gamesplayed"])*100, 2)}%)\n世界排行: {league["standing"] if league["standing"] != -1 else "N/A"} | 地區排名: {league["standing_local"] if league["standing_local"] != -1 else "N/A"}{f"{_skipline}Glicko: {round(league['glicko'], 2)}±{round(league['rd'], 2)}" if 'glicko' in league and 'rd' in league else ""}{f"{_skipline}apm: {league['apm']} | pps: {league['pps']} | vs: {league['vs']}" if 'apm' in league and 'pps' in league and 'vs' in league else ""}""",
                )

                embed.add_field(
                    "其他紀錄",
                    value=f"""40L: {f"{math.trunc(rc._40l['record']['endcontext']['finalTime'] / 3600000)}:{'%02d' % math.trunc(rc._40l['record']['endcontext']['finalTime'] % 3600000 / 60000)}:{'%02d' % (rc._40l['record']['endcontext']['finalTime'] / 1000 % 60)} {f'''(世界排行: {rc._40l['rank'] or '不適用'})''' if rc._40l['record'] else ''}" if rc._40l else "沒有紀錄"}\nBlitz: {f"{rc.blitz['record']['endcontext']['score']} {f'''(世界排行: {rc.blitz['rank'] or '不適用'})'''}" if rc.blitz['record'] else "沒有紀錄"}\nzen: {rc.zen['score']} (等級 {rc.zen['level']})""",
                )

        await ctx.send(embeds=embed)


def setup(client, **kwargs):
    Tetrio(client, **kwargs)
