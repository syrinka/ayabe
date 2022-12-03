import time
from datetime import datetime, timedelta

from nonebot import on_command, require, get_bot
from nonebot.log import logger
from nonebot.params import CommandArg, Event, Arg, T_State
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
    '''
)


REMIND_DELTA = timedelta(minutes=-30)

async def callback(msg, user_id):
    bot = get_bot()
    await bot.send_msg(message=msg, user_id=user_id)


m = on_command('remind', aliases={'r'}, block=False)

@m.handle()
async def remind(state: T_State, e: Event, msg=CommandArg()):
    msg = str(msg)
    try:
        result = extract_time(msg, time_base=time.time())[0]
    except IndexError:
        await m.reject('理解不能')

    if result['type'] == 'time_point':
        span = result['detail']['time']
    elif result['type'] == 'time_period':
        span = result['detail']['time']['point']['time']
    else:
        await m.reject('未能找到时间点或时间周期\n解析结果为：\ntext: %s\ntype: %s\n请据此调整输入' % (result['text'], result['type']))

    # 当天
    if span[0].endswith('00:00:00') and span[1].endswith('23:59:59'):
        span[0] = span[0].removesuffix('00:00:00') + '07:30:00'

    date = datetime.strptime(span[0], r'%Y-%m-%d %H:%M:%S')

    offset = result['offset']
    msg = (msg[:offset[0]] + msg[offset[1]:]).strip(' \r\n\t，。,.、')

    resp = '%s\n%s' % (msg, span[0])
    job = scheduler.add_job(
        callback,
        trigger='date',
        name=msg,
        args=[msg, e.get_user_id()],
        run_date=date + REMIND_DELTA,
    )
    state['job_id'] = job.id
    state['date'] = date
    await m.send(
        '【{}】{}\n事项已录入，将提前半小时提醒'.format(
            msg, date.strftime('%m-%d %H:%M')
        )
    )


@m.got('before')
async def remind(state: T_State, msg=Arg('before')):
    try:
        result = extract_time(str(msg))[0]
    except IndexError:
        # 无事发生
        return

    if result['type'] != 'time_delta':
        await m.reject('意义不明，若希望更改提醒时间，请描述一个时间差')
    else:
        # hour -> hours
        delta = timedelta(**{k+'s': v for k, v in result['detail']['time'].items()})
        new_date = state['date'] - delta
        scheduler.reschedule_job(state['job_id'], run_date=new_date)
        await m.finish('了解，那么将提前到 {} 进行提醒'.format(new_date.strftime(r'%m-%d %H:%M')))


m = on_command('memo', priority=5)

@m.handle()
async def memo():
    jobs = scheduler.get_jobs()

    if not jobs:
        await m.send('已经没有计划事项了')
    else:
        msg = '当前尚有以下的事项：'
        for job in sorted(jobs, key=lambda j: j.next_run_time):
            msg += '\n%s\n · %s' % (job.next_run_time.strftime(r'%m-%d %H:%M'), job.name)
        await m.send(msg)


m = on_command('memo clear', priority=5)

@m.got('sure', '确定吗？这是不可逆的 [y/N]')
async def clear(sure=Arg('sure')):
    if str(sure).lower() != 'y':
        await m.finish('（什么都没做）')
    else:
        scheduler.remove_all_jobs()
        await m.finish('清理完毕')

