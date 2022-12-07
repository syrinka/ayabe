from nonebot import on_command
from nonebot.params import Received, T_State
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import (
    PRIVATE_FRIEND,
    MessageEvent,
    Message
)


__plugin_meta__ = PluginMetadata(
    name='combiner',
    description='合并不同类型的消息段，例如文字+图',
    usage='''
使用 combine 命令触发，接着发送希望合并的消息，以三个换行作为停止信号'''
)


m = on_command('combine', permission=PRIVATE_FRIEND)
m.__help_name__ = 'extract'
m.__doc__ = 'combine, end with a \\n'


@m.handle()
async def notice(s: T_State):
    s['msg'] = Message()
    await m.send('准备完毕')


@m.receive('e')
async def save(s: T_State, e: MessageEvent = Received('e')):
    if e.get_plaintext() == '\n\n\n':
        await m.finish(s['msg'])
    else:
        s['msg'] += e.get_message()
        await m.reject('got')
