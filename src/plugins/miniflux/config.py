from typing import List, Optional
from pydantic import BaseModel


class Config(BaseModel):
    miniflux_api_endpoint: str
    miniflux_api_token: str
    miniflux_check_cron: str = '0 * * * *'
    miniflux_crop_length: int = 10
    miniflux_trace_feeds: Optional[List[int]] = None
    miniflux_trace_categories: Optional[List[int]] = None
    superusers: List[str]
