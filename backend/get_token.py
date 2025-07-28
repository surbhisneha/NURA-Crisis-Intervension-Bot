import os
import requests
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Now get env vars
IAM_URL = os.getenv("IAM_URL")
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")

def test_iam_token():
    print("IAM_URL =", IAM_URL)
    print("WATSONX_API_KEY =", bool(WATSONX_API_KEY))  # just to confirm it's loaded

    data = {
        "apikey": WATSONX_API_KEY,
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(IAM_URL, headers=headers, data=data)
    response.raise_for_status()
    token = response.json()["access_token"]
    print("IAM token:", token)
    return token

test_iam_token()
