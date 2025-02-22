from dataclasses import dataclass

@dataclass(init=True, eq=True, frozen=True)
class Song:
    title: str
    artists: str
    album: str
    cover: str
    link: str
    track_number: int

    # def __eq__(self, other):
    #     if not isinstance(other, Song):
    #         return False
    #     return self.title == other.title and self.artists == other.artists and self.album == other.album
    
    # def __hash__(self):
    #     print("Hello 2")
    #     return hash((self.title, self.artists, self.album))