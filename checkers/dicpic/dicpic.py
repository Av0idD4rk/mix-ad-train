import requests
import os
import random
from checklib import *

PORT = 1337
CHECKER_PATH = os.path.dirname(os.path.abspath(__file__))
TIMEOUT = 10

def rnd_image():
    return random.choice([image.path for image in os.scandir(f'{CHECKER_PATH}/img')])

class CheckMachine:
    @property
    def url(self):
        return f'http://{self.c.host}:{self.port}'
    
    def __init__(self, checker: BaseChecker):
        self.c = checker
        self.port = PORT
    
    def register(self, email: str, password: str, status: Status.MUMBLE) -> None:
        url = f'{self.url}/auth/register'
        resp = requests.post(url, json={'email': email, 'password': password}, timeout=TIMEOUT)
        self.c.assert_in('registered', resp.text, f'{email}:{password}')
    
    def login(self, email: str, password: str, status: Status.MUMBLE) -> str:
        url = f'{self.url}/auth/login'
        resp = requests.post(url, json={'email': email, 'password': password}, timeout=TIMEOUT)

        self.c.assert_in('access_token', resp.text, f'{email}:{password}')

        return resp.json().get('access_token', '')
    
    def put_image(self, token: str, text: str, premium_only: str, status: Status.MUMBLE) -> None:
        url = f'{self.url}/photo/upload'

        image_path = rnd_image()
        headers = {
            'Authorization': f'Bearer {token}'
        }
        files = {'file': open(image_path, 'rb')}
        data = {
            'name': 'My Image',
            'description': text,
            'premium_only': premium_only
        }
        resp = requests.post(url, headers=headers, files=files, data=data, timeout=TIMEOUT)
        self.c.assert_in('Photo uploaded successfully', resp.text, '')
    
    def get_image(self, token: str) -> str:
        url = f'{self.url}/photo/my'
        headers = {
            'Authorization': f'Bearer {token}'
        }
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        
        try:
            text = resp.json()[0].get('description', '')
        except:
            text = ''

        return text
