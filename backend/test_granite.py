import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

IAM_URL = os.getenv("IAM_URL")
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
PROJECT_ID = os.getenv("PROJECT_ID")
WATSONX_REGION = os.getenv("WATSONX_REGION")  # Example: https://us-south.ml.cloud.ibm.com

def get_iam_token():
    data = f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={WATSONX_API_KEY}"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(IAM_URL, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def call_granite_model(user_input):
    token = get_iam_token()
    url = f"{WATSONX_REGION}/ml/v1-beta/generation/text?version=2024-05-01"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    data = {
    "model_id": "ibm/granite-13b-instruct-v2",  # your chosen model
    "project_id": PROJECT_ID,
    "input": f"Respond helpfully to the following input:\n\n{user_input}\n\nResponse:",
    "parameters": {
        "decoding_method": "greedy",
        "max_new_tokens": 200
    }
}



    response = requests.post(url, headers=headers, json=data)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("HTTP error status:", response.status_code)
        print("Response body:", response.text)
        raise e

    result = response.json()
    return result["results"][0]["generated_text"]

if __name__ == "__main__":
    prompt = input("Enter your prompt: ")
    reply = call_granite_model(prompt)
    print("Granite Response:", reply)
