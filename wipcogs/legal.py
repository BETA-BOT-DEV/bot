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
    Client,
    CommandContext,
    Embed,
    EmbedField,
    Extension,
    extension_command,
)
from loguru._logger import Logger

newline = "\n"


class legal(Extension):
    def __init__(self, client, **kwargs):
        self.client: Client = client
        self.logger: Logger = kwargs.get("logger")
        self.logger.info(
            f"Client extension cogs.{os.path.basename(__file__)[:-3]} has been loaded."
        )

    @extension_command()
    async def legal(self, *args, **kwargs):
        ...

    @legal.subcommand()
    async def privacy(self, ctx: CommandContext):
        ...

    @legal.subcommand()
    async def terms(self, ctx: CommandContext):
        await ctx.send(
            embeds=Embed(
                title="使用條款",
                description="最後修改日期：2022年11月2日\n\n感謝您使用「BETA BOT」，為了讓您能夠安心的使用，請您詳閱使用條款。",
                fields=[
                    EmbedField(
                        name="一、使用協議",
                        value="• 邀請 BETA BOT（「機器人」）或使用其提供之服務即表示同意使用條款及隱私權保護政策。\n• 您有權在與機器人共享的任何Discord伺服器上自由使用本服務，您亦可將其邀請到您擁有「管理伺服器」權限的任何伺服器。\n• 如果您違反此機器人的條款和/或政策，或Discord Inc的服務條款、隱私權保護政策和/或社區準則，則上述權利可能被移除。",
                        inline=False,
                    ),
                    EmbedField(
                        name="二、與Discord Inc.的關聯",
                        value="本服務不隸屬於、支持或由Discord Inc.所製作，如與Discord或其任何商標、功能、訊息內容、圖片等任何直接關聯皆純屬巧合。我們不聲稱擁有Discord的任何資產、商標或其他知識產權的版權所有權。",
                        inline=False,
                    ),
                    EmbedField(
                        name="三、免責條款",
                        value="若使用機器人進行違法事項或遭其他使用者檢舉，則責任自負，BETA BOT 開發者（「開發者」、「我們」）一律不負責，且有權力移除發布的內容。",
                        inline=False,
                    ),
                    EmbedField(
                        name="四、條款增修",
                        value="我們保留自行增修條款的權力，因應需求隨時進行修正，修正後的條款將刊登於機器人網站上。如有任何問題，請透過機器人或下方聯絡方式反映。",
                        inline=False,
                    ),
                    EmbedField(
                        name="五、聯絡我們",
                        value="您可以透過電子郵件 contact@itsrqtl.me 或機器人聯絡我們。",
                    ),
                ],
                color=randint(0, 0xFFFFFF),
            )
        )


def setup(client, **kwargs):
    legal(client, **kwargs)
