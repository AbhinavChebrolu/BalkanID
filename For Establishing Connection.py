import requests
import psycopg2
import os

# Github OAuth access token
access_token = "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"

# Postgres database credentials
dbname = 'AbhinavChebrolu'
user = 'AbhinavChebrolu'
password = '54321'
host = 'localhost'
port = '5432'

# Connect to Postgres database
conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
cur = conn.cursor()

# Create tables
cur.execute('''
    CREATE TABLE IF NOT EXISTS owner (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT
    );
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS repo (
        id SERIAL PRIMARY KEY,
        owner_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        status TEXT NOT NULL,
        stars_count INTEGER NOT NULL,
        FOREIGN KEY (owner_id) REFERENCES owner (id)
    );
''')

# Fetch data from Github API
headers = {'Authorization': f'token {access_token}'}
response = requests.get('https://api.github.com/user/repos', headers=headers)
data = response.json()

# Normalize and deduplicate data
owners = {}
repos = []
for item in data:
    owner = item['owner']
    owner_id = owner['id']
    if owner_id not in owners:
        owners[owner_id] = {
            'name': owner['login'],
            'email': owner.get('email', '')
        }
    repo = {
        'owner_id': owner_id,
        'name': item['name'],
        'status': item['private'] and 'private' or 'public',
        'stars_count': item['stargazers_count']
    }
    repos.append(repo)

# Insert data into tables
for owner_id, owner in owners.items():
    cur.execute('''
        INSERT INTO owner (name, email) VALUES (%s, %s)
        ON CONFLICT DO NOTHING
        RETURNING id;
    ''', (owner['name'], owner['email']))
    owner_row = cur.fetchone()
    if owner_row:
        owner_id = owner_row[0]
    for repo in repos:
        if repo['owner_id'] == owner_id:
            cur.execute('''
                INSERT INTO repo (owner_id, name, status, stars_count)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            ''', (owner_id, repo['name'], repo['status'], repo['stars_count']))

# Commit changes and close connection
conn.commit()
cur.close()
conn.close()
