# TODO blur 时间处理，数据存储
import time
from datetime import datetime, timedelta

from nonebot import on_command, require, get_bot, get_driver
from nonebot.log import logger
from nonebot.params import CommandArg, Event, Arg
from nonebot.plugin import PluginMetadata
require('nonebot_plugin_apscheduler')
from nonebot_plugin_apscheduler import scheduler

from .utils import extract_time


__plugin_meta__ = PluginMetadata(
    name='Reminder',
    description='',
    usage='''
    remind ACT
        录入事项
    memo
        列出未来事项
    memo clear
        清空事项
    '''
)


last_added = None


driver = get_driver()
REMIND_DELTA = timedelta(minutes=30)

async def callback(desc, date_str, user_id):
    bot = get_bot()
    msg = '予定事项提醒，请留意\n【%s】%s' % (desc, date_str)
    await bot.send_msg(message=msg, user_id=user_id)


m = on_command('remind', aliases={'r'})

@m.handle()
async def remind(e: Event, msg=CommandArg()):
    msg = str(msg)
    try:
        result = extract_time(msg, time_base=time.time())[0]
    except IndexError:
        await m.finish('理解不能')

    if result['type'] == 'time_point':
        span = result['detail']['time']
    elif result['type'] == 'time_period':
        span = result['detail']['time']['point']['time']
    else:
        await m.finish('未能找到时间点或时间周期\n解析结果为：\ntext: %s\ntype: %s\n请据此调整输入' % (result['text'], result['type']))

    # 当天
    if span[0].endswith('00:00:00') and span[1].endswith('23:59:59'):
        span[0] = span[0].removesuffix('00:00:00') + '07:30:00'

    date = datetime.strptime(span[0], r'%Y-%m-%d %H:%M:%S')

    offset = result['offset']
    desc = (msg[:offset[0]] + msg[offset[1]:]).strip(' \r\n\t，。,.、')
    date_str = date.strftime('%m-%d %H:%M')

    now = datetime.now()
    if date < now:
        await m.finish('似乎是过去的时间，未录入')
    elif date - now <= REMIND_DELTA * 1.5:
        # 若事件发生时间足够近，则准点提醒
        await m.send('【{}】{}\n事项已录入，将准点提醒'.format(desc, date_str))
        run_date = date
    else:
        await m.send('【{}】{}\n事项已录入，将提前半小时提醒'.format(desc, date_str))
        run_date = date - REMIND_DELTA

    job = scheduler.add_job(
        callback,
        trigger='date',
        name='\x00'.join([date_str, desc]), # 用于获取事件真实时间
        args=[desc, date_str, e.get_user_id()],
        run_date=run_date,
    )
    global last_added
    last_added = (job.id, date)


m = on_command('ahead')

@m.handle()
async def ahead(msg=CommandArg()):
    if last_added is None:
        return

    msg = str(msg)
    try:
        result = extract_time(msg)[0]
    except IndexError:
        # 无事发生
        return

    if result['type'] != 'time_delta':
        await m.finish('意义不明，若希望更改提醒时间，请描述一个时间差')
    else:
        job_id, date = last_added
        # hour -> hours
        delta = timedelta(**{k+'s': v for k, v in result['detail']['time'].items()})
        new_date = date - delta
        scheduler.reschedule_job(job_id, run_date=new_date)
        await m.finish('了解，那么将提前到 {} 进行提醒'.format(new_date.strftime(r'%m-%d %H:%M')))


m = on_command(('memo', 'clear'))

@m.got('sure', '确定吗？这是不可逆的 [y/N]')
async def clear(sure=Arg('sure')):
    if str(sure).lower() != 'y':
        await m.finish('（什么都没有做）')
    else:
        scheduler.remove_all_jobs()
        await m.finish('清理完毕')


m = on_command('memo')

@m.handle()
async def memo():
    jobs = scheduler.get_jobs()

    if not jobs:
        await m.send('已经没有计划事项了')
    else:
        msg = '目前有以下的事项：'

        # name = date_str + '\x00' + desc
        for job in sorted(jobs, key=lambda j: j.name):
            date_str, desc = job.name.split('\x00')
            msg += '\n%s\n · %s' % (date_str, desc)
        await m.send(msg)
