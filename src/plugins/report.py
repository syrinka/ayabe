import nonebot
from nonebot.plugin import PluginMetadata
from nonebot.log import logger

import uvicorn
from urllib.parse import parse_qs
from pydantic import BaseModel, Extra
from threading import Thread

__plugin_meta__ = PluginMetadata(
    name='report',
    description='webhook 信息上报',
    usage='访问接口，传入 token，title，msg 字段'
)


class Config(BaseModel, extra=Extra.ignore):
    environment: str
    report_token: str = None

config = Config.parse_obj(nonebot.get_driver().config)


async def app(scope, receive, send):
    q = parse_qs(scope['query_string'].decode())
    try:
        token = q['token'][0]

        if token is None or token != config.report_token:
            code = 403 # Unauthorized
        else:
            title = q['title'][0]
            content = q['content'][0]
            msg = f'[report] {title or ""}\n{content}'

            bot = nonebot.get_bot()
            await bot.send_msg(
                message=msg,
                user_id='1580422201'
            )
            code = 200 # Ok
    except (KeyError, IndexError):
        code = 400 # Bad Request

    await send({
        'type': 'http.response.start',
        'status': code
    })


def main():
    uvicorn.run(app, host='0.0.0.0', port=8081)


if config.environment == 'prod':
    Thread(target=main, daemon=True).start()
