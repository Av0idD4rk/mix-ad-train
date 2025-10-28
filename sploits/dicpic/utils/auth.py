import requests

def register_user(url: str, user: dict) -> bool:
    resp = requests.post(f'{url}/auth/register', json=user)

    return 'registered' in resp.text

def get_user_token(url: str, user: dict) -> str:
    resp = requests.post(f'{url}/auth/login', json=user)
    user_token = resp.json().get('access_token', '')

    return user_token
