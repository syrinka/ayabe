from random import randint

from nonebot import on_notice
from nonebot.rule import is_type
from nonebot.params import EventParam
from nonebot.adapters.onebot.v11.event import PokeNotifyEvent

m = on_notice(is_type(PokeNotifyEvent))
m.__help_name__ = '*poke'
m.__doc__ = '戳一戳'


selects = ('……唔。', '怎么了？', '哇……？！')

@m.handle()
async def nope(e = EventParam()):
    # 仅在戳自己时
    if e.target_id == e.self_id:
        msg = selects[randint(0, len(selects)-1)]
        await m.send(message=msg)
