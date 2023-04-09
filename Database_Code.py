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
for repo in data:
    owner = repo["owner"]
    owner_id = owner["id"]
    owner_name = owner["login"]
    owner_email = owner.get("email")
    if owner_id not in owners:
        owners[owner_id] = {"name": owner_name, "email": owner_email}
    repo_id = repo["id"]
    repo_name = repo["name"]
    status = "Public" if repo["private"] is False else "Private"
    stars = repo["stargazers_count"]
    cur.execute("SELECT * FROM repo WHERE id = %s", (repo_id,))
    existing_repo = cur.fetchone()
    if existing_repo is None:
        owners_data = owners[owner_id]
        cur.execute("INSERT INTO owner (name, email) VALUES (%s, %s) RETURNING id", (owners_data["name"], owners_data["email"]))
        owner_id = cur.fetchone()[0]
        repos.append({
            "id": repo_id,
            "owner_id": owner_id,
            "name": repo_name,
            "status": status,
            "stars_count": stars
        })

# Insert data into tables
for owner_id, owner in owners.items():
    cur.execute('''
        INSERT INTO owner (name, email) VALUES (%s, %s)
        ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name, email=EXCLUDED.email
        RETURNING id;
    ''', (owner['name'], owner['email']))
    owner_row = cur.fetchone()
    if owner_row:
        owner_id == owner_row[0]
    for repo in repos:
        if repo['owner_id'] == owner_id:
            cur.execute('''
                INSERT INTO repo (owner_id, name, status, stars_count)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET owner_id=EXCLUDED.owner_id, name=EXCLUDED.name, status=EXCLUDED.status, stars_count=EXCLUDED.stars_count;
            ''', (owner_id, repo['name'], repo['status'], repo['stars_count']))

# Commit changes and close connection
conn.commit()
cur.close()
conn.close()
