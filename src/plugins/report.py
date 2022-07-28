import nonebot
from nonebot.plugin import PluginMetadata
from nonebot.log import logger

from pydantic import BaseModel, Extra
from flask import Flask, request
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


app = Flask(__name__)

@app.route('/')
async def report():
    token = request.args.get('token')
    if token is None or token != config.report_token:
        return 'bad token', 401

    title = request.args.get('title')
    msg = request.args.get('msg')
    text = f'[report] {title or ""}\n{msg}'    

    bot = nonebot.get_bot()
    await bot.send_msg(
        message=text,
        user_id='1580422201'
    )
    return 'ok', 200


def main():
    app.run(host='0.0.0.0', port=8081,  debug=False)


if config.environment == 'prod':
    Thread(target=main, daemon=True).start()

