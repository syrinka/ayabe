from pydantic import BaseModel
from typing import List


class Feed(BaseModel):
    id: int
    title: str
    site_url: str
    feed_url: str
    etag_header: str


class Entry(BaseModel):
    id: int
    feed_id: int
    feed: Feed
    title: str
    url: str


class Entries(BaseModel):
    total: int
    entries: List[Entry]

    def __add__(self, other: "Entries"):
        return Entries(
            self.total + other.total,
            self.entries + other.entries
        )
