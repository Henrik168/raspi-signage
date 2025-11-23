#!/usr/bin/env python3
"""Create a user for the signage app.
Usage: python3 scripts/add_user.py <username> <role>
"""


import json
from pathlib import Path
from getpass import getpass
from werkzeug.security import generate_password_hash
from logging import getLogger
log = getLogger(__name__)

USERS = Path('data') / 'users.json'

USERS.parent.mkdir(parents=True, exist_ok=True)


def _load():
    if USERS.exists():
        return json.loads(USERS.read_text(encoding='utf-8'))
    return []


def _save(data):
    USERS.parent.mkdir(parents=True, exist_ok=True)
    USERS.write_text(json.dumps(data, indent=2), encoding='utf-8')


def add_user() -> bool:
    username = input('Please enter a new username: ').strip()
    role = "admin"

    pwd = getpass('Password: ')
    pwd2 = getpass('Repeat: ')
    if pwd != pwd2:
        log.error('Passwords do not match')
        return False

    data = [u for u in _load() if u.get('username') != username]
    data.append({'username': username,
                'password_hash': generate_password_hash(pwd), 'role': role})
    _save(data)
    log.info('User %s with role %s added.', username, role)
    return True
