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


driver = get_driver()
REMIND_DELTA = timedelta(minutes=30)
last_job = None

async def callback(desc, date, user_id, **kwargs):
    bot = get_bot()
    msg = '予定事项提醒，请留意\n【%s】%s' % (desc, date.strftime(r'%m-%d %H:%M'))
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

    await m.send('【{}】{}\n事项已录入，将准时提醒'.format(
        desc, date.strftime('%m-%d %H:%M')
    ))

    global last_job
    last_job = scheduler.add_job(
        callback,
        trigger='date',
        kwargs={
            'desc': desc,
            'date': date,
            'user_id': e.get_user_id()
        },
        run_date=date,
    )


m = on_command('ahead')

@m.handle()
async def ahead(msg=CommandArg()):
    global last_job
    if last_job is None:
        await m.finish('没有上一条事项')

    msg = str(msg)
    try:
        result = extract_time(msg)[0]
    except IndexError:
        # 无事发生
        return

    if result['type'] != 'time_delta':
        await m.finish('意义不明，若希望变更提醒时间，请描述一个时间差')
    else:
        job = last_job
        # hour -> hours
        delta = timedelta(**{k+'s': v for k, v in result['detail']['time'].items()})
        new_date = job.kwargs['date'] - delta
        if datetime.now() > new_date:
            await m.finish('指定了过去的时间，提醒时间未变更')
        scheduler.reschedule_job(job.id, run_date=new_date)
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
        await m.send('暂无予定事项，辛苦了')
    else:
        msg = '目前的予定事项：'

        for job in sorted(jobs, key=lambda j: j.kwargs['date']):
            kw = job['kwargs']
            msg += '\n%s\n · %s' % (
                kw['date'].strftime(r'%m-%d %H:%M'),
                kw['desc']
            )
        await m.send(msg)
