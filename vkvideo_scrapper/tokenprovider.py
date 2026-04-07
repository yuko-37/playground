import requests


def get_token():
    print("Trigger get_token...")
    url = "https://login.vk.com/"
    
    params = {
        "act": "get_anonym_token"
    }

    data = {
        "client_secret": "o557NLIkAErNhakXrQ7A",
        "client_id": "52461373",
        "scopes": "audio_anonymous,video_anonymous,photos_anonymous,profile_anonymous",
        "isApiOauthAnonymEnabled": "false",
        "version": "1",
        "app_id": "6287487"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(url, params=params, data=data, headers=headers)
        response.raise_for_status()
    
        json_data = response.json()
        token = json_data.get("data", {}).get("access_token")
    except Exception as e:
        raise ValueError('Failed to get token: {e}') from e

    return token
