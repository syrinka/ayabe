import openai
from nonebot import on_command, logger, get_driver
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from nonebot.adapters import Event
try:
    from nonebot.adapters.onebot.v11 import (
        MessageSegment as OnebotMessageSegment,
        MessageEvent as OnebotMessageEvent
    )
    _onebot_adapter = True
except ImportError:
    _onebot_adapter = False

from .config import Config


driver = get_driver()
config = Config.parse_obj(driver.config)

openai.api_key = config.openai_api_key
preset = ''


m = on_command('chat', permission=SUPERUSER)

@m.handle()
async def ai_chat(e: Event, arg=CommandArg()) -> None:
    text = str(arg).strip()
    logger.info('openai completion for: %s' % text)
    try:
        # https://beta.openai.com/docs/api-reference/completions/create
        global preset
        resp = openai.Completion.create(
            model=config.chatgpt_model,
            prompt=preset + '\n\n' + text,
            max_tokens=config.chatgpt_max_tokens,
            temperature=config.chatgpt_temperature,
            request_timeout=30
        )
        msg = resp.choices[0]['text']
        msg = msg.split('\n\n', 1)[-1]
    except Exception as e:
        await m.send('错误发生：%s' % str(e), at_sender=True)
        raise e
    logger.info('get completion: %s' % msg)
    try:
        if _onebot_adapter and isinstance(e, OnebotMessageEvent):
            e: OnebotMessageEvent = e
            msg = OnebotMessageSegment.reply(e.message_id) \
                + OnebotMessageSegment.text(msg)
            await m.send(msg)
        else:
            await m.send(msg)
    except:
        await m.send('回答已获取，但是发送失败', at_sender=True)


m = on_command('preset', permission=SUPERUSER)

@m.handle()
async def chat_preset(arg=CommandArg()) -> None:
    text = str(arg)
    global preset
    if text:
        preset = text
        logger.success('set preset to: %s' % preset)
        await m.send('新预设已加载')
    else:
        await m.send('当前预设：\n%s' % preset)


m = on_command('reset preset', permission=SUPERUSER)

@m.handle()
async def chat_preset_reset() -> None:
    global preset
    preset = ''
    await m.finish('预设已重置')
