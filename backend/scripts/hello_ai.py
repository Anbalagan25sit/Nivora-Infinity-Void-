import os
import urllib.request
import json
from dotenv import load_dotenv

# 1. Load the secret API key from your .env file
load_dotenv()
# We're using Groq, which is crazy fast and you already have an API key!
my_api_key = os.getenv("GROQ_API_KEY")

# 2. Prepare the order (the URL and the headers)
url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {my_api_key}",
    "Content-Type": "application/json"
}

# 3. Create our message (A dictionary, just like you learned!)
data = {
    "model": "llama3-8b-8192",  # Using a fast open-source model
    "messages": [
        {"role": "user", "content": "Explain Python in exactly one sentence."}
    ],
    "max_tokens": 100
}

print("Asking Groq...")

# 4. Send the request (This is the tricky internet part)
try:
    # We turn our Python dictionary into JSON text (the language of the internet)
    json_data = json.dumps(data).encode("utf-8")
    
    # Create the "envelope" to send
    req = urllib.request.Request(url, data=json_data, headers=headers)
    
    # Send it and wait for the response!
    response = urllib.request.urlopen(req)
    
    # Read the response and turn it back into a Python dictionary
    response_body = response.read().decode("utf-8")
    result = json.loads(response_body)
    
    # 5. Print the answer!
    print("\nGroq says:")
    print(result["choices"][0]["message"]["content"])
    
except Exception as e:
    print(f"Oops! Something went wrong: {e}")
