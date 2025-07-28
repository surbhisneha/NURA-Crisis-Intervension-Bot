# ibm_services.py

from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, EmotionOptions
import os

API_KEY = os.getenv("NLU_API_KEY")
URL = os.getenv("NLU_URL")

authenticator = IAMAuthenticator(API_KEY)
nlu = NaturalLanguageUnderstandingV1(
    version='2021-08-01',
    authenticator=authenticator
)
nlu.set_service_url(URL)

def analyze_emotion(text):
    try:
        response = nlu.analyze(
            text=text,
            features=Features(emotion=EmotionOptions()),
            language='en'
        ).get_result()

        emotions = response.get('emotion', {}).get('document', {}).get('emotion', {})
        return emotions
    except Exception as e:
        print(f"NLU error: {e}")
        return {}
