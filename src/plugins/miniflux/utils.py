from typing import Optional
from datetime import datetime
from urllib.parse import urljoin

import httpx
from nonebot import get_driver

from .config import Config
from .models import *


config = Config.parse_obj(get_driver().config)


def session():
    return httpx.AsyncClient(headers={
        'X-Auth-Token': config.miniflux_api_token
    })


async def get_unreads_count():
    url = urljoin(config.miniflux_api_endpoint, 'feeds/counters')
    async with session() as sess:
        resp = await sess.get(url)
        return {int(k): v for k, v in resp.json()['unreads'].items()}


class get(object):
    def ts(date: datetime):
        return (date or datetime.now()).timestamp()


    @classmethod
    async def feed_entries(cls, feed_id: int, since: Optional[datetime] = None) -> Entries:
        url = urljoin(
            config.miniflux_api_endpoint,
            'feeds/%d/entries?status=unread&after=%d' % (feed_id, cls.ts(since))
        )
        async with session() as sess:
            resp = await sess.get(url)
            return Entries.parse_obj(resp.json())


    @classmethod
    async def category_entries(cls, ca_id: int, since: Optional[datetime] = None) -> Entries:
        url = urljoin(
            config.miniflux_api_endpoint,
            'categories/%d/entries?status=unread&after=%d' % (ca_id, cls.ts(since))
        )
        async with session() as sess:
            resp = await sess.get(url)
            return Entries.parse_obj(resp.json())


    @classmethod
    async def all_entries(cls, since: Optional[datetime] = None) -> Entries:
        url = urljoin(
            config.miniflux_api_endpoint,
            'entries?status=unread&after=%d' % cls.ts(since)
        )
        async with session() as sess:
            resp = await sess.get(url)
            return Entries.parse_obj(resp.json())
