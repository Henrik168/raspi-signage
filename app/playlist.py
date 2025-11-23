"""Module for managing the playlist data."""

from typing import List, Any, Optional
from dataclasses import dataclass, asdict, field
import json
from logging import getLogger

from .config import PLAYLIST_PATH

log = getLogger(__name__)


# app/items.py


@dataclass
class Item:
    uuid: str
    media_type: str
    file_name: str
    enabled: bool
    duration: Optional[int] = None  # in seconds, only for images
    poster: Optional[str] = None

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_jason_items(data: List[dict[str, Any]]) -> List[Item]:
    items = []
    for entry in data:
        item = Item(
            uuid=entry["uuid"],
            media_type=entry["media_type"],
            file_name=entry["file_name"],
            enabled=entry["enabled"],
            duration=entry.get("duration"),
            poster=entry.get("poster")
        )
        items.append(item)
    return items


@dataclass
class PlayListStore:
    _items: List[Item] = field(default_factory=list)

    def __post_init__(self):

        with PLAYLIST_PATH.open("r", encoding="utf-8") as f:
            self._items = load_jason_items(json.load(f))

    def all(self) -> List[dict[str, Any]]:
        return [item.to_dict() for item in self._items]

    def save(self) -> None:
        with PLAYLIST_PATH.open("w", encoding="utf-8") as f:
            json.dump(self.all(), f, indent=2)
        log.info("Playlist gespeichert mit %d Einträgen.", len(self._items))

    def add(self, uuid: str, media_type: str, file_name: str, enabled: bool, duration: Optional[int] = 0, poster: Optional[str] = None) -> Item:
        if uuid in [item.uuid for item in self._items]:
            raise ValueError(f"Item with uuid {uuid} already exists.")

        item = Item(
            uuid=uuid,
            media_type=media_type,
            file_name=file_name,
            enabled=enabled,
            duration=duration,
            poster=poster
        )

        self._items.append(item)

        self.save()

        return item

    def get(self, uuid: str) -> Optional[Item]:
        return next((i for i in self._items if i.uuid == uuid), None)

    def get_position(self, uuid: str) -> Optional[int]:
        for index, item in enumerate(self._items):
            if item.uuid == uuid:
                return index
        return None

    def toggle(self, uuid: str) -> Optional[Item]:
        item = self.get(uuid)
        if not item:
            return None
        item.enabled = not item.enabled
        self.save()
        return item

    def order(self, uuid_order: List[str]) -> None:

        order_map = {uuid: index for index, uuid in enumerate(uuid_order)}

        items_sorted = sorted(
            self._items, key=lambda item: order_map[item.uuid])

        self._items = items_sorted
        self.save()

    def move_by_idx(self, idx: int, offset: int) -> None:

        new_idx = idx + offset

        lst = self._items
        if 0 <= new_idx < len(lst):
            lst[idx], lst[new_idx] = lst[new_idx], lst[idx]

        self._items = lst
        self.save()

    def update_by_uuid(self, uuid: str, **kwargs) -> Optional[Item]:
        item = self.get(uuid)
        if not item:
            log.warning(
                "Item mit uuid %s nicht gefunden zum Aktualisieren.", uuid)
            return

        for key, value in kwargs.items():
            if hasattr(item, key):
                setattr(item, key, value)
            else:
                log.warning("Item hat kein Attribut '%s'.", key)
                return

        self.save()
        return item

    def remove(self, uuid: str) -> bool:
        item = self.get(uuid)
        if not item:
            return False
        self._items.remove(item)
        self.save()
        return True


# eine globale Instanz, die du überall verwenden kannst
playlist = PlayListStore()
