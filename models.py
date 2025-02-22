from dataclasses import dataclass

@dataclass(init=True, eq=True, frozen=True)
class Song:
    title: str
    artists: str
    album: str
    cover: str
    link: str
    track_number: int