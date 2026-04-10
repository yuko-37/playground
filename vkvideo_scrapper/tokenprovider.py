import logging
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_cache: dict = {}


def clear_token_cache() -> None:
    _cache.clear()


def get_token() -> str:
    now = time.time()

    if _cache.get("token") and now < _cache.get("expires_at", 0):
        return _cache["token"]

    logger.info("Fetching new anonymous VK token")
    url = "https://login.vk.com/"

    params = {"act": "get_anonym_token"}

    data = {
        "client_secret": os.environ["VK_CLIENT_SECRET"],
        "client_id": os.environ["VK_CLIENT_ID"],
        "scopes": "audio_anonymous,video_anonymous,photos_anonymous,profile_anonymous",
        "isApiOauthAnonymEnabled": "false",
        "version": "1",
        "app_id": os.environ["VK_APP_ID"]
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(url, params=params, data=data, headers=headers)
        response.raise_for_status()

        json_data = response.json()
        payload = json_data.get("data", {})
        token = payload.get("access_token")
        if not token:
            raise ValueError("Token missing from response payload")

        expires_in = payload.get("expires_in", 3600)
        _cache["token"] = token
        _cache["expires_at"] = now + expires_in
        logger.info("Token acquired successfully (valid for %ss)", expires_in)
    except Exception as e:
        logger.error("Failed to get token: %s", e)
        raise ValueError(f"Failed to get token: {e}") from e

    return token
