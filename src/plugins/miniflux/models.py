from pydantic import BaseModel, Field
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
    
    def __str__(self):
        return f'· {self.title}'

class Entries(BaseModel):
    total: int = 0
    entries: List[Entry] = Field(default_factory=list)

    def __add__(self, other: "Entries"):
        return Entries(
            self.total + other.total,
            self.entries + other.entries
        )

    def __bool__(self):
        return bool(self.total)

    def __getitem__(self, item):
        if isinstance(item, slice):
            crop = self.entries[item]
            return Entries(len(crop), crop)
        else:
            return self.entries[item]

    def __str__(self):
        return '\n'.join(str(e) for e in self.entries)
