import requests

from tokenprovider import get_token

cache = {}

def get_titles(owner_id, album_id, limit=3):
    if 'token' in cache:
        token = cache['token']
    else:
        token = get_token()
        cache['token'] = token
        
    url = "https://api.vkvideo.ru/method/video.getFromAlbum"
    
    params = {
        "v": "5.275",
        "client_id": "52461373"
    }
    
    data = {
        "album_id": album_id,
        "count": 25,
        "extended": 1,
        "fields": "is_esia_verified,is_sber_verified,is_tinkoff_verified,photo_50,verified",
        "offset": 0,
        "owner_id": owner_id,
        "sort_album": 0,
        "access_token": token
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, params=params, data=data, headers=headers)
    response.raise_for_status()
    
    data = response.json()

    items = data.get('response', {}).get('items', [])
    items_sorted = sorted(items, key=lambda x: x['video']['date'], reverse=True)

    titles = []
    
    for item in items_sorted:
        video = item['video']
        title = video['title']
        url = video.get("direct_url")
        titles.append({"date": video['date'], "title": title, 'url': url})

    return titles[:limit]
