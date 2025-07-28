import os
import json
import re
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from rag_engine import ask_with_rag
from cloudant_helper import save_chat_to_cloudant, load_last_mood  # ✅ Cloudant helpers
from datetime import datetime


load_dotenv()
app = Flask(__name__)
CORS(app)

# ENV variables
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
WATSONX_REGION = os.getenv("WATSONX_REGION")
IAM_URL = os.getenv("IAM_URL")
PROJECT_ID = os.getenv("PROJECT_ID")
MODEL_ID = "meta-llama/llama-3-2-3b-instruct"

# IAM Token
def get_iam_token():
    data = f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={WATSONX_API_KEY}"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(IAM_URL, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

# Geocode function using OpenStreetMap
def geocode_location(location):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": location, "format": "json", "limit": 1}
    headers = {"User-Agent": "MyApp/1.0 (neurocare@example.com)"}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 403:
        raise ValueError("403 Forbidden: OpenStreetMap blocked the request.")
    response.raise_for_status()
    data = response.json()
    if not data:
        raise ValueError(f"Location not found: {location}")
    return float(data[0]["lat"]), float(data[0]["lon"])

# Nearby places using Overpass API
def get_nearby_places(lat, lng, category, radius=1000):
    overpass_tags = {
        "hospital": "amenity=hospital",
        "restaurant": "amenity=restaurant",
        "cafe": "amenity=cafe",
        "hotel": "tourism=hotel",
        "museum": "tourism=museum",
        "school": "amenity=school",
        "supermarket": "shop=supermarket",
        "pharmacy": "amenity=pharmacy",
        "gym": "leisure=fitness_centre",
        "park": "leisure=park"
    }
    tag = overpass_tags.get(category, "amenity=restaurant")
    url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:25];
    (
      node[{tag}](around:{radius},{lat},{lng});
      way[{tag}](around:{radius},{lat},{lng});
      relation[{tag}](around:{radius},{lat},{lng});
    );
    out center 20;
    """
    response = requests.post(url, data=query)
    response.raise_for_status()
    data = response.json()

    places = []
    for element in data["elements"]:
        name = element.get("tags", {}).get("name")
        if name:
            places.append({"name": name})
    return places

# Extract category/location
def extract_location_and_category(user_input):
    token = get_iam_token()
    url = f"{WATSONX_REGION}/ml/v1/text/chat?version=2024-05-01"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    prompt = f"""
Extract the location and category for a place search from the user's sentence.

Only choose categories from this list:
["restaurant", "hospital", "cafe", "hotel", "museum", "school", "supermarket", "pharmacy", "gym", "park"]

Sentence: "{user_input}"

Respond ONLY in this JSON format:
{{
  "category": "...",
  "location": "..."
}}
"""
    payload = {
        "model_id": MODEL_ID,
        "project_id": PROJECT_ID,
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        "parameters": {"temperature": 0.3, "max_tokens": 100}
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    output = response.json()["choices"][0]["message"]["content"]
    print("🧠 Watsonx Raw Output:\n", output)
    try:
        json_match = re.search(r'\{.*\}', output, re.DOTALL)
        parsed = json.loads(json_match.group()) if json_match else None
        if not parsed:
            raise ValueError("Failed to extract JSON from response.")
        return parsed
    except Exception as e:
        raise ValueError(f"Invalid JSON from Watsonx: {e}")

# Mood detection
def detect_mood_from_text(text):
    text = text.lower()
    if any(word in text for word in ["sad", "depressed", "unhappy", "anxious", "cry"]):
        return "sad"
    elif any(word in text for word in ["happy", "excited", "joy", "great", "cheerful"]):
        return "happy"
    return "neutral"

# 🧠 Main chatbot endpoint
@app.route("/api/message", methods=["POST"])
def message():
    try:
        data = request.json
        user_input = data.get("input", "").strip()
        user_id = data.get("user_id", "anonymous")
        use_rag = data.get("use_rag", False)

        if not user_input:
            return jsonify({"error": "Input is required"}), 400

        # Step 1: Check last mood
        last_mood = load_last_mood(user_id)

        # Step 2: Handle location query
        if "near" in user_input.lower() or "around" in user_input.lower():
            print("📍 Detected location-based query")
            info = extract_location_and_category(user_input)
            lat, lng = geocode_location(info["location"])
            category = info["category"].lower()
            places = get_nearby_places(lat, lng, category)
            if not places:
                final_response = f"No places found near {info['location']}."
            else:
                place_names = [place.get("name", "Unknown") for place in places[:5]]
                final_response = f"Nearby {category}s in {info['location']}: " + ", ".join(place_names)

        # Step 3: Use RAG if requested
        elif use_rag:
            final_response = ask_with_rag(user_input)

        # Step 4: Default to Watsonx
        else:
            token = get_iam_token()
            url = f"{WATSONX_REGION}/ml/v1/text/chat?version=2024-05-01"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            payload = {
                "project_id": PROJECT_ID,
                "model_id": MODEL_ID,
                "messages": [{"role": "user", "content": [{"type": "text", "text": user_input}]}],
                "parameters": {"temperature": 0.7, "top_p": 0.9, "max_tokens": 300}
            }
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            final_response = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        # Step 5: Detect current mood
        current_mood = detect_mood_from_text(user_input)

        # Step 6: Save to Cloudant
        save_chat_to_cloudant(user_id, user_input, final_response, mood=current_mood)

        # Step 7: Add greeting or mood reminder
        greeting = ""
        if last_mood:
            greeting = f"Hey again! Last time you seemed a bit {last_mood}. How are you feeling today?\n\n"
        else:
            greeting = "Hi there! I'm always here for you. 😊\n\n"

        full_response = greeting + final_response
        print("✅ Final response:", full_response)

        return jsonify({"response": full_response})

    except Exception as e:
        print("❌ Error in /api/message:", e)
        return jsonify({"error": "Server error"}), 500


# ✅ NEW — welcome route to recall previous mood
@app.route("/api/welcome", methods=["POST"])
def welcome():
    try:
        data = request.json
        user_id = data.get("user_id", "anonymous")
        last_mood = load_last_mood(user_id)

        if last_mood == "sad":
            return jsonify({"response": "Welcome back! I remember you weren't feeling great earlier. How are you feeling now?"})
        elif last_mood == "happy":
            return jsonify({"response": "Welcome back! You seemed happy last time we spoke 😊"})
        elif last_mood == "neutral":
            return jsonify({"response": "Hey again. I'm here if you want to talk."})
        else:
            return jsonify({"response": "Hi! How can I help you today?"})

    except Exception as e:
        print(f"❌ Error in /api/welcome: {e}")
        return jsonify({"error": str(e)}), 500

# Run app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
