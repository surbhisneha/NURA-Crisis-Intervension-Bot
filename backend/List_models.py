import os
import requests
from dotenv import load_dotenv

load_dotenv()

IAM_URL = os.getenv("IAM_URL")
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
WATSONX_REGION = os.getenv("WATSONX_REGION")  # e.g. https://us-south.ml.cloud.ibm.com

def get_iam_token():
    data = f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={WATSONX_API_KEY}"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(IAM_URL, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def list_models():
    token = get_iam_token()
    url = f"{WATSONX_REGION}/ml/v1/foundation_model_specs?version=2024-05-01"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    models = response.json().get("resources", [])
    print("\nYour accessible model IDs:")
    for model in models:
        print("-", model.get("model_id"))

if __name__ == "__main__":
    list_models()
