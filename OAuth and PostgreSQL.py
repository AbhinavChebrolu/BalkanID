import requests
import psycopg2

# Define the GitHub OAuth access token and API endpoint
# Change the token values in respective to your account 
access_token = "your_github_oauth_access_token"
api_url = "https://api.github.com/user/repos"

# Define the PostgreSQL connection information
dbname = "your_database_name"
user = "your_username"
password = "your_password"
host = "your_host_name_or_ip_address"
port = "your_port_number"

# Connect to the PostgreSQL database
conn = psycopg2.connect(database=dbname, user=user, password=password, host=host, port=port)

# Open a cursor to perform database operations
cur = conn.cursor()

# Set up the headers for the GitHub API request
headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/vnd.github.v3+json"
}

# Make the GitHub API request to retrieve the user's repositories
response = requests.get(api_url, headers=headers)

# Check if the response was successful (status code 200)
if response.status_code == 200:
    # Parse the response JSON data to extract the repository information
    repositories = response.json()

    # Loop through each repository and insert it into the PostgreSQL database
    for repo in repositories:
        try:
            cur.execute(
                "INSERT INTO repositories (owner_id, owner_name, owner_email, repo_id, repo_name, status, stars_count) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (repo["owner"]["id"], repo["owner"]["login"], repo["owner"].get("email"), repo["id"], repo["name"], repo["private"], repo["stargazers_count"])
            )
            conn.commit()
        except psycopg2.IntegrityError:
            # If the repository is already in the database, print a message and continue
            print(f"Repository '{repo['name']}' already exists in the database.")
            conn.rollback()
        except Exception as e:
            # If an exception occurs, print the error message and rollback the transaction
            print(f"Error inserting repository '{repo['name']}' into the database: {e}")
            conn.rollback()

    # Close the cursor and database connection
    cur.close()
    conn.close()

    print(f"Successfully inserted {len(repositories)} repositories into the database.")
else:
    print("Error retrieving repositories from GitHub API.")
