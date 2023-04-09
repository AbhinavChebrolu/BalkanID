#Exporting the data from postgreSQL to CSV
import requests
import psycopg2
import csv
import os
from flask import Flask, jsonify, request, Response


# Connect to the PostgreSQL database
conn = psycopg2.connect(database="AbhinavChebrolu", user="AbhinavChebrolu", password="54321", host="localhost://", port="5432")

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute the SELECT query to retrieve the data from the repositories table
cur.execute("SELECT * FROM repositories")

# Fetch all rows from the cursor
rows = cur.fetchall()

app = Flask(__name__)
@app.route('/csv', methods=['GET'])
def download_csv():
    cur.execute('''
        SELECT owner.id, owner.name, COALESCE(owner.email, ''), repo.id, repo.name, repo.status, repo.stars_count
        FROM owner
        JOIN repo ON repo.owner_id = owner.id;
    ''')
    results = cur.fetchall()
    if len(results) == 0:
        return Response(status=404)
    csv = 'Owner ID,Owner Name,Owner Email,Repo ID,Repo Name,Status,Stars Count\n'
    for row in results:
        csv += f'{row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]}\n'
    return Response(csv, mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=data.csv'})

repos = []
for repo in data:
    owner_id = repo["owner"]["id"]
    repo_id = repo["id"]
    repo_name = repo["name"]
    status = "Public" if repo["private"] is False else "Private"
    stars = repo["stargazers_count"]
    cur.execute("SELECT * FROM repo WHERE id = %s AND owner_id = %s", (repo_id, owner_id))
    existing_repo = cur.fetchone()
    if existing_repo is None:
        repos.append({
            "owner_id": owner_id,
            "id": repo_id,
            "name": repo_name,
            "status": status,
            "stars_count": stars
        })
    else:
        cur.execute("UPDATE repo SET name = %s, status = %s, stars_count = %s WHERE id = %s AND owner_id = %s", (repo_name, status, stars, repo_id, owner_id))

# Close the cursor and database connection
cur.close()
conn.close()

# Define the path and filename for the output CSV file
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
output_file = os.path.join(desktop_path, "repositories.csv")

# Open the output file for writing and create a CSV writer
with open(output_file, "w", newline="") as file:
    writer = csv.writer(file)

    # Write the header row to the CSV file
    writer.writerow(["owner_id", "owner_name", "owner_email", "repo_id", "repo_name", "status", "stars_count"])

    # Write each row from the result set to the CSV file
    for row in rows:
        writer.writerow(row)
     
print("Data exported to CSV file at " + output_file)
