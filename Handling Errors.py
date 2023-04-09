# Fetch data from Github API
headers = {'Authorization': f'token {access_token}'}
url = 'https://api.github.com/user/repos'
max_retries = 3
for i in range(max_retries):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        break
    except (requests.exceptions.RequestException, ValueError) as e:
        # Log the error and retry the request
        logging.error(f"Error fetching data from Github API: {e}")
        if i < max_retries - 1:
            logging.warning(f"Retrying request ({i+1}/{max_retries})")
            time.sleep(5)
        else:
            logging.error("Max retries exceeded. Aborting.")
            raise

            
# Insert data into tables
max_retries = 3
for owner_id, owner in owners.items():
    for repo in repos:
        if repo['owner_id'] == owner_id:
            for i in range(max_retries):
                try:
                    cur.execute('''
                        INSERT INTO repo (owner_id, name, status, stars_count)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT DO NOTHING;
                    ''', (owner_id, repo['name'], repo['status'], repo['stars_count']))
                    conn.commit()
                    break
                except psycopg2.Error as e:
                    # Log the error and retry the operation
                    logging.error(f"Error inserting data into database: {e}")
                    if i < max_retries - 1:
                        logging.warning(f"Retrying operation ({i+1}/{max_retries})")
                        time.sleep(5)
                    else:
                        logging.error("Max retries exceeded. Aborting.")
                        raise
