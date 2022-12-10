from typing import List, Optional
from pydantic import BaseSettings


class Config(BaseSettings):
    miniflux_api_endpoint: str
    miniflux_api_token: str
    miniflux_trace_feeds: Optional[List[int]] = None
    miniflux_trace_categories: Optional[List[int]] = None
