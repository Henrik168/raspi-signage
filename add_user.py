#!/usr/bin/env python3
"""Create a user for the signage app.
Usage: python3 scripts/add_user.py <username> <role>
"""


import json
from pathlib import Path
from getpass import getpass
from werkzeug.security import generate_password_hash

USERS = Path('data') / 'users.json'

USERS.parent.mkdir(parents=True, exist_ok=True)


def load():
    if USERS.exists():
        return json.loads(USERS.read_text(encoding='utf-8'))
    return []


def save(data):
    USERS.parent.mkdir(parents=True, exist_ok=True)
    USERS.write_text(json.dumps(data, indent=2), encoding='utf-8')


def add(username, role):

    pwd = getpass('Password: ')
    pwd2 = getpass('Repeat: ')
    if pwd != pwd2:
        print('Passwords do not match')

    data = [u for u in load() if u.get('username') != username]
    data.append({'username': username,
                'password_hash': generate_password_hash(pwd), 'role': role})
    save(data)
    print('User saved')


def main() -> None:
    if USERS.exists():
        print(f'Existing users: {[u["username"] for u in load()]}')

    username = input('Please enter a new username: ').strip()
    add(username, 'admin')


if __name__ == '__main__':
    main()
