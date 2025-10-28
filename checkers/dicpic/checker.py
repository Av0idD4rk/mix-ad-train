#!/usr/bin/env python3

import sys
import requests
import json
from checklib import *
from dicpic import *

def rnd_email():
    return f'{rnd_username()}@{rnd_username()}.ru'

class Checker(BaseChecker):
    vulns: int = 1
    timeout: int = 10
    uses_attack_data: bool = True

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.mch = CheckMachine(self)
    
    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except requests.exceptions.ConnectionError:
            self.cquit(Status.DOWN, "Connection error", "Got requests connection error")
        
    def check(self, *args, **kwargs):
        email, password = rnd_email(), rnd_password()
        self.mch.register(email, password, Status.MUMBLE)
        token = self.mch.login(email, password, Status.MUMBLE)
        original_value = rnd_string(10)
        self.mch.put_image(token, original_value, 'off', Status.MUMBLE)
        resp_value = self.mch.get_image(token)
        self.assert_eq(original_value, resp_value, "Can't get flag while check", Status.MUMBLE)
        self.cquit(Status.OK)

    def put(self, flag_id: str, flag: str, vuln: str):
        email, password = rnd_email(), rnd_password()
        self.mch.register(email, password, Status.MUMBLE)
        token = self.mch.login(email, password, Status.MUMBLE)
        self.mch.put_image(token, flag, 'on', Status.MUMBLE)
        self.cquit(
            Status.OK,
            public=f"{email}:{password}"
        )
    
    def get(self, flag_id: str, flag: str, vuln: str):
        email, password = flag_id.split(":")
        token = self.mch.login(email, password, Status.CORRUPT)
        value = self.mch.get_image(token)
        self.assert_eq(value, flag, "Can't get flag while 'get'", Status.CORRUPT)
        self.cquit(Status.OK)

if __name__ == '__main__':
    c = Checker(sys.argv[2])

    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)
