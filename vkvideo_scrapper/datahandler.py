import json

from datetime import datetime
from dataprovider import get_titles


def write_last_shows_to_memory():

    show_album = {'ДаМы': (-217878975, 10),
                  'Подружки': (-217878975, 8),
                  'Быстрые свидания': (-217878975, 9),
                  'Натальная карта': (-211232966, 15), 
                  'Что о тебе думают': (-212451998, 9),
                  'Контакты': (-213802301, 1), 
                  'Контакты игра': (-213802301, 7),
                  'Among us': (-67771885, 7),
                  'Женский Форум': (-211229778, 1),
                  'Это логично': (-127553155, 11),
                }

    raw_data = {name: get_titles(ids[0], ids[1]) for name, ids in show_album.items()}
    
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

    with open('memory.json', 'w', encoding='utf-8') as f:
        json.dump(data_to_dump, f, ensure_ascii=False, indent=4)


def read_last_shows_from_memory():
    with open('memory.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data