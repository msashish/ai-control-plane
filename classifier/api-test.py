import requests

# Define the service URL running on port 8085
url = "http://localhost:8085/prompt/classification"

# Set up your payload matching the PromptRequest schema
payload = {
    "prompt": "Tell me a joke about programming"
}

try:
    # Make the POST request with the JSON data
    response = requests.post(url, json=payload)
    
    # Check if the request was successful
    response.raise_for_status()
    
    # Parse and print the classification result
    result = response.json()
    print("Classification Output:", result)

except requests.exceptions.RequestException as e:
    print(f"An error occurred while connecting to Laya service: {e}")
