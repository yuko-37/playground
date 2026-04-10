import json
import logging
import os

from datetime import datetime
from dataprovider import get_titles

_SHOWS_PATH = os.path.join(os.path.dirname(__file__), "shows.json")
_MEMORY_PATH = os.path.join(os.path.dirname(__file__), "memory.json")

logger = logging.getLogger(__name__)


def write_last_shows_to_memory():
    with open(_SHOWS_PATH, encoding="utf-8") as f:
        show_album = json.load(f)

    raw_data = {}
    for name, ids in show_album.items():
        try:
            raw_data[name] = get_titles(ids["owner_id"], ids["album_id"])
        except Exception as e:
            logger.error("Failed to fetch show '%s': %s", name, e)

    sorted_shows = sorted(
        [item for item in raw_data.items() if item[1]], 
        key=lambda x: x[1][0]['date'], 
        reverse=True
    )

    data_to_dump = {
        name: [
            {
                "title": v["title"], 
                "date": datetime.fromtimestamp(v["date"]).strftime("%d.%m.%Y"),
                "date_num": v["date"],
                "url": v["url"]
            } for v in releases
        ] for name, releases in sorted_shows
    }

    with open(_MEMORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(data_to_dump, f, ensure_ascii=False, indent=4)
    logger.info("memory.json written with %d shows", len(data_to_dump))


def read_last_shows_from_memory():
    with open(_MEMORY_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data