from nonebot import on_notice, get_bot
from nonebot.rule import to_me
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11.event import PokeNotifyEvent

m = on_notice(to_me)
m.__help_name__ = '*poke'
m.__doc__ = '戳一戳'

@m.handle()
async def nope(e: Event):
    msg = '……唔'
    if isinstance(e, PokeNotifyEvent):
        if e.group_id is None:
            bot = get_bot()
            await bot.send_msg(message=msg, user_id=e.user_id)
        else:
            await m.send(msg)
