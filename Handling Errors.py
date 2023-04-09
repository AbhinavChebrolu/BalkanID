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
