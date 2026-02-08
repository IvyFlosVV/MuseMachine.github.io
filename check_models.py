import requests
import os

# PASTE YOUR KEY HERE
GENAI_KEY = "AIzaSyCWkNhdwtz1TDlFDd4yv0HuoLi1BzM-tEg"

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GENAI_KEY}"

try:
    response = requests.get(url)
    data = response.json()
    
    print("---------------- AVAILABLE MODELS ----------------")
    if 'models' in data:
        for model in data['models']:
            # We only care about models that can 'generateContent'
            if "generateContent" in model['supportedGenerationMethods']:
                print(f"Name: {model['name']}")
    else:
        print("Error fetching models:")
        print(data)
    print("--------------------------------------------------")

except Exception as e:
    print(f"Connection Error: {e}")