import requests
import json
import os
from dotenv import load_dotenv

# Function that loads the environment variables
load_dotenv()

# Define your API key and search engine ID
API_KEY = os.getenv("google-search-key")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

# Define your query and make a request to the API
query = "what is the newest nba 2k game"
url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}&num=10"
response = requests.get(url)

# Parse the JSON response and extract the relevant information
data = json.loads(response.text)

# Create a list to hold the search results
results = []

# Loop through each search result and extract the relevant information
for item in data['items']:
    result = {}
    result['url'] = item['link']
    result['date'] = item['snippet'].split('-')[0].strip()
    details = item['snippet'].split('-')
    if len(details) > 1:
        result['details'] = details[1].strip()
    else:
        result['details'] = "N/A"
    results.append(result)

# Save the results as JSON to a file
with open('results.json', 'w') as outfile:
    json.dump(results, outfile)
