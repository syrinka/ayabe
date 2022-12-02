from nonebot import get_driver, Bot, logger

driver = get_driver()


@driver.on_bot_connect
async def online(bot: Bot):
    logger.info('发送上线通知')
    msg = 'Bot 已上线'
    for uid in driver.config.superusers:
        await bot.send_msg(user_id=uid, message=msg, message_type='private')
