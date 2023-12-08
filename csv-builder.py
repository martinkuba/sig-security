from datetime import datetime
import os
import pytz
import pandas as pd
import requests

token = os.environ['TOKEN_SECRET']

# Define the URL for the GitHub Security Advisories API
url = "https://api.github.com/orgs/open-telemetry/security-advisories"

# Set up the request headers with the authorization token
headers = {
    'Accept': "application/vnd.github+json",
    'Authorization': f"Bearer {token}",
    'X-GitHub-Api-Version': "2022-11-28"
}

# Initialize an empty list to store responses
responses = []

try:
    # Send a GET request to the GitHub API
    response = requests.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        advisories = response.json()
        # Now, 'advisories' contains the security advisories data.
        # Append the response data to the 'responses' list
        responses.append(advisories)
        print(advisories)
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"An error occurred: {e}")

for idx, advisory_response in enumerate(responses, 1):
    print(f"Response {idx}:")
    print(advisory_response)

# Extract specified fields and create a DataFrame
data = {
    'ghsa_id': [item["ghsa_id"] for item in advisory_response],
    'cve_id': [item["cve_id"] for item in advisory_response],
    'html_url': [item["html_url"] for item in advisory_response],
    'summary': [item["summary"] for item in advisory_response],
    'severity': [item["severity"] for item in advisory_response],
    'state': [item["state"] for item in advisory_response],
    'created_at': [item["created_at"] for item in advisory_response],
    'updated_at': [item["updated_at"] for item in advisory_response]
}
df = pd.DataFrame(data)

# Split the repository name from the url and add it as a new column 'repo'
df['repo'] = df['html_url'].str.split('/').str[4]

# Filter rows where the 'text' column contains either 'test' or 'testing'
filtered_df = df[~df['summary'].str.contains('test only', case=False, regex=True)]

df_filled = filtered_df.fillna('na')

## Filter for published information
filtered_json = df_filled[df_filled['state'] == 'published']

# Specify the file path for the JSON file
json_file_path = 'published_output.json'

# Write DataFrame to JSON file for published incidents
filtered_json.to_json(json_file_path, orient='records')
