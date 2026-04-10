import logging
import requests

from tokenprovider import get_token, clear_token_cache

logger = logging.getLogger(__name__)

_VK_AUTH_ERROR_CODE = 5  # "User authorization failed"


def get_titles(owner_id, album_id, limit=3):
    api_url = "https://api.vkvideo.ru/method/video.getFromAlbum"

    params = {
        "v": "5.275",
        "client_id": "52461373"
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    for attempt in range(2):
        token = get_token()

        body = {
            "album_id": album_id,
            "count": limit,
            "extended": 1,
            "offset": 0,
            "owner_id": owner_id,
            "sort_album": 0,
            "access_token": token
        }

        response = requests.post(api_url, params=params, data=body, headers=headers)
        response.raise_for_status()
        response_data = response.json()

        error_code = response_data.get("error", {}).get("error_code")
        if error_code == _VK_AUTH_ERROR_CODE:
            logger.warning("VK auth error (attempt %d) — refreshing token and retrying", attempt + 1)
            clear_token_cache()
            continue
        break
    else:
        raise ValueError("VK API auth failed after token refresh")

    items = response_data.get('response', {}).get('items', [])
    items_sorted = sorted(items, key=lambda x: x['video']['date'], reverse=True)

    titles = []

    for item in items_sorted:
        video = item['video']
        title = video['title']
        if video.get("direct_url"):
            video_url = video["direct_url"]
        else:
            video_url = f"https://vkvideo.ru/video{owner_id}_{video['id']}"
            logger.warning("direct_url missing for video '%s' — using fallback URL", title)
        titles.append({"date": video['date'], "title": title, 'url': video_url})

    return titles
