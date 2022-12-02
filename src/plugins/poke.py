from nonebot import on_notice
from nonebot import get_bot
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11.event import PokeNotifyEvent

m = on_notice()
m.__help_name__ = '*poke'
m.__doc__ = '戳一戳'

@m.handle()
async def nope(e: Event):
    msg = 'ちょっと'
    if isinstance(e, PokeNotifyEvent):
        if e.group_id is None:
            bot = get_bot()
            await bot.send_msg(message=msg, user_id=e.user_id)
        else:
            await m.send(msg)
