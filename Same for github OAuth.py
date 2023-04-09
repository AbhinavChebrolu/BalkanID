import requests
import psycopg2
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

# Set up OAuth authentication
client_id = 'your_client_id'
client_secret = 'your_client_secret'
oauth_client = BackendApplicationClient(client_id=client_id)
oauth_session = OAuth2Session(client=oauth_client)
token = oauth_session.fetch_token(token_url='https://github.com/login/oauth/access_token',
                                  client_id=client_id, client_secret=client_secret)

# Fetch data from the Github API
api_url = 'https://api.github.com/users/your_username/repos'
headers = {'Authorization': 'token ' + token['access_token']}
response = requests.get(api_url, headers=headers)
data = response.json()

# Store the fetched data in the Postgres database
conn = psycopg2.connect(dbname='your_database_name', user='your_username',
                        password='your_password', host='localhost')
cur = conn.cursor()
for item in data:
    cur.execute("INSERT INTO your_table_name (id, name, description) VALUES (%s, %s, %s)",
                (item['id'], item['name'], item['description']))
conn.commit()
cur.close()
conn.close()
