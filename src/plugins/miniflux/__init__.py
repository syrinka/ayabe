from datetime import datetime
from nonebot import require, get_driver, get_bot, logger
require('nonebot_plugin_apscheduler')
from nonebot_plugin_apscheduler import scheduler

from .config import Config
from .utils import get
from .models import Entries

driver = get_driver()
config = Config.parse_obj(driver.config)
last_check_time: datetime = datetime.now()


async def check():
    global last_check_time
    since = last_check_time
    last_check_time = datetime.now()

    entries = Entries()
    if config.miniflux_trace_categories is not None:
        for ca_id in config.miniflux_trace_categories:
            entries += await get.category_entries(ca_id, since)
    if config.miniflux_trace_feeds is not None:
        for feed_id in config.miniflux_trace_feeds:
            entries += await get.feed_entries(feed_id, since)

    if not entries:
        entries = await get.all_entries(since)

    return entries
    

cron_kw = dict(zip(
    ('minute', 'hour', 'day', 'month', 'day_of_week'),
    config.miniflux_check_cron.split()
))
@scheduler.scheduled_job(trigger='cron', **cron_kw)
async def callback():
    logger.info('cron check')
    entries = await check()
    if not entries:
        logger.info('no new entry')
        return
    else:
        logger.info(f'{entries.total} new entries found')

    crop = config.miniflux_crop_length
    if entries.total > crop:
        excess = entries.total - crop
        entries = entries[:crop]
    else:
        excess = 0

    msg = f'收到 Miniflux 方面的新文章：\n{str(entries)}'
    if excess:
        msg += f'\n...(+{excess})'

    bot = get_bot()
    for uid in config.superusers:
        await bot.send_msg(user_id=uid, message=msg, message_type='private')
