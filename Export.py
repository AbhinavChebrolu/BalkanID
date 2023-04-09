#Exporting the data from postgreSQL to CSV

import psycopg2
import csv
import os

# Connect to the PostgreSQL database
conn = psycopg2.connect(database="AbhinavChebrolu", user="AbhinavChebrolu", password="54321", host="localhost://", port="5432")

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute the SELECT query to retrieve the data from the repositories table
cur.execute("SELECT * FROM repositories")

# Fetch all rows from the cursor
rows = cur.fetchall()

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
