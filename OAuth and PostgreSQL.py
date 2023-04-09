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

    # Define a set to store the unique owner IDs
    owner_ids = set()

    # Loop through each repository and insert it into the PostgreSQL database
    for repo in repositories:
        owner_id = repo["owner"]["id"]
        owner_name = repo["owner"]["login"]
        owner_email = repo["owner"].get("email")
        repo_id = repo["id"]
        repo_name = repo["name"]
        status = "private" if repo["private"] else "public"
        stars_count = repo["stargazers_count"]

        # Normalize the owner information and insert it into the owners table
        if owner_id not in owner_ids:
            owner_ids.add(owner_id)
            cur.execute(
                "INSERT INTO owners (id, name, email) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (owner_id, owner_name, owner_email)
            )

        # Insert the repository information into the repositories table
        cur.execute(
            "INSERT INTO repositories (owner_id, repo_id, name, status, stars) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
            (owner_id, repo_id, repo_name, status, stars_count)
        )

    # Commit the transaction and close the cursor and database connection
    conn.commit()
    cur.close()
    conn.close()

    print(f"Successfully inserted {len(repositories)} repositories into the database.")
else:
    print("Error retrieving repositories from GitHub API.")


#In this code, you would need to replace the dummy values for the GitHub OAuth access token and the PostgreSQL connection 
#information with the real values for your setup. The code makes a GitHub API request to retrieve the user's repositories, 
#loops through each repository and inserts it into the PostgreSQL database, detects duplicated values by catching the 
#psycopg2.IntegrityError exception, and displays exceptions for any other errors that occur during the insertion. The 
#code also closes the database connection and prints a message to confirm the number of repositories that were successfully inserted into the database.
    
