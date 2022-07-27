from nonebot import on_command
from nonebot.params import EventParam

from datetime import datetime


class Rand(object):
    def __init__(self, seed):
        self._seed = seed

    def _rand(self) -> int:
        self._seed = (25214903917 * self._seed) & ((1 << 48) - 1)
        return self._seed

    def __call__(self, min, max) -> int:
        return min + (self._rand() % (max - min + 1))


m = on_command('ys', aliases={'运势','今日运势'})
m.__help_name__ = 'ys'
m.__doc__ = '''
roll 一下今日的运势
'''

@m.handle()
async def luck(e = EventParam()):
    uid: str = e.get_user_id()
    date: str = datetime.now().strftime(r'%Y-%m-%d')
    seed = int.from_bytes((uid + '#' + date).encode(), byteorder='big')

    msg = '今日运势：{}'.format(
        Rand(seed)(1, 100)
    )

    await m.send(msg)
