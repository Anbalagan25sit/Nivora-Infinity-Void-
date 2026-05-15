import os
import boto3
from dotenv import load_dotenv

# 1. Load AWS keys from your .env file
load_dotenv()

# 2. Create the AWS "Waiter" (Bedrock client)
# boto3 automatically finds your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY from the .env
region = os.getenv("AWS_REGION", "us-east-1")
client = boto3.client("bedrock-runtime", region_name=region)

print("Asking AWS Nova Pro...")

# 3. Prepare the order (Variables and Dictionaries!)
model_id = "amazon.nova-pro-v1:0"

# AWS Nova Pro expects the message in this specific dictionary format
messages = [
    {
        "role": "user",
        "content": [{"text": "Explain Python in exactly one sentence."}]
    }
]

# 4. Send the request (Try/Except for safety)
try:
    # We use the 'converse' method to talk to Nova models
    response = client.converse(
        modelId=model_id,
        messages=messages
    )
    
    # 5. Extract the answer from the dictionary response
    # The response is a nested dictionary. We navigate it step by step, just like person["address"]["city"]
    answer = response["output"]["message"]["content"][0]["text"]
    
    print("\nNova Pro says:")
    print(answer)

except Exception as e:
    print(f"Oops! Something went wrong: {e}")
