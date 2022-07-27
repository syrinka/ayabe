from nonebot import on_command, get_bot
from nonebot.log import logger
from nonebot.params import Received
from nonebot.adapters.onebot.v11 import PRIVATE_FRIEND

m = on_command('extract', permission=PRIVATE_FRIEND)
m.__help_name__ = 'extract'
m.__doc__ = '''
提取合并转发消息中的所有图片链接
首先触发该命令，待 bot 回复“准备完毕”后，转发消息给 bot
bot 仅提取消息中的原始链接，不保证链接的可用性'''

def resolve(data):
    urls = []
    for node in data:
        try:
            urls.extend(resolve(node['content']))
        except:
            if node['type'] == 'image':
                urls.append(node['data']['url'])
    
    return urls


@m.handle()
async def notice():
    await m.send('准备完毕')


@m.receive('e')
async def save(e = Received('e')):
    await m.send('收到消息，开始提取')
    urls = []
    bot = get_bot()
    for seg in e.get_message():
        if seg.type == 'forward':
            id = seg.data['id']
            logger.debug(f'获取合并转发消息 id={id}')
            try:
                data = await bot.get_forward_msg(id=id)
            except Exception as e:
                await m.reject(f'[!] 内部错误\n{e}')
                
            data = data['messages']
            urls = resolve(data)

    if not urls:
        await m.finish('未能提取到链接！')
    else:
        await m.send(f'提取完毕，计 {len(urls)} 条链接')
        await m.finish('\n'.join(urls))
