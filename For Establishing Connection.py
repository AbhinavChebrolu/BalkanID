import requests
import psycopg2

# Github API access token
access_token = "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"

# Database connection details
db_name = "AbhinavChebrolu"
db_user = "Abhinavchebrolu"
db_password = "54321"
db_host = "localhost"
db_port = "5432"

# Github API endpoint
api_endpoint = "https://api.github.com/user/repos"

# Make a GET request to the Github API
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(api_endpoint, headers=headers)

# Parse the response JSON and extract required fields
data = response.json()
repos = []
for repo in data:
    owner_id = repo["owner"]["id"]
    owner_name = repo["owner"]["login"]
    owner_email = repo["owner"].get("email")
    repo_id = repo["id"]
    repo_name = repo["name"]
    status = "public" if repo["private"] == False else "private"
    stars_count = repo["stargazers_count"]
    repos.append((owner_id, owner_name, owner_email, repo_id, repo_name, status, stars_count))

# Connect to the database and insert data
conn = psycopg2.connect(
    dbname=db_name,
    user=db_user,
    password=db_password,
    host=db_host,
    port=db_port
)
cur = conn.cursor()

# Create the 'repositories' table if it doesn't already exist
cur.execute("""
    CREATE TABLE IF NOT EXISTS repositories (
        id SERIAL PRIMARY KEY,
        owner_id INTEGER NOT NULL,
        owner_name VARCHAR(255) NOT NULL,
        owner_email VARCHAR(255),
        repo_id INTEGER NOT NULL,
        repo_name VARCHAR(255) NOT NULL,
        status VARCHAR(10) NOT NULL,
        stars_count INTEGER NOT NULL
    )
""")

# Normalize the data to remove duplicates
repos_normalized = []
for repo in repos:
    if repo not in repos_normalized:
        repos_normalized.append(repo)

# Insert the normalized data into the 'repositories' table
for repo in repos_normalized:
    cur.execute("""
        INSERT INTO repositories (owner_id, owner_name, owner_email, repo_id, repo_name, status, stars_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, repo)

conn.commit()

# Print the data from the 'repositories' table
cur.execute("SELECT * FROM repositories")
rows = cur.fetchall()
for row in rows:
    print(row)

# Close the database connection
cur.close()
conn.close()
