import requests
import random
import re
import os
from flask import Flask, render_template, request
from colorthief import ColorThief
from io import BytesIO

app = Flask(__name__)

# --- CONFIGURATION ---
GENAI_KEY = "AIzaSyCWkNhdwtz1TDlFDd4yv0HuoLi1BzM-tEg" 

# ... (Keep your existing smart_local_summary and get_ai_summary functions exactly as they are) ...
# [Paste smart_local_summary and get_ai_summary here]

def smart_local_summary(text):
    if not text: return ["Just enjoy the visuals."]
    clean_text = text.replace('<p>', '').replace('</p>', '')
    sentences = re.split(r'(?<=[.!?]) +', clean_text)
    good_sentences = [s for s in sentences if 10 < len(s) < 300]
    if good_sentences: return good_sentences[:3]
    else: return [clean_text[:150] + "..."]

def get_ai_summary(text):
    # (Use the code from our previous step)
    if not text or len(text) < 50: return ["Just enjoy the visuals!"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={GENAI_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = { "contents": [{ "parts": [{ "text": f"Task: Extract exactly 3 distinct facts from this art description. Rules: No introduction. No 'Here are'. No exclamation marks. Keep it professional and historical. Max 15 words per point. Text: '{text}'" }] }] }
    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        if 'candidates' in data:
            raw_text = data['candidates'][0]['content']['parts'][0]['text']
            lines = raw_text.split('\n')
            clean_points = [line.strip('*•- ') for line in lines if line.strip() and "Here are" not in line]
            if clean_points: return clean_points[:3]
        return smart_local_summary(text)
    except: return smart_local_summary(text)


# --- NEW FUNCTIONS FOR RECOMMENDATIONS ---

def get_artwork_data(artwork_id=None):
    """
    Fetches a specific artwork (if ID provided) OR a random one.
    """
    try:
        if artwork_id:
            # Fetch SPECIFIC Art
            api_url = f"https://api.artic.edu/api/v1/artworks/{artwork_id}?fields=id,title,artist_display,image_id,description,exhibition_history,provenance_text"
            response = requests.get(api_url).json()
            art_data = response.get('data')
        else:
            # Fetch RANDOM Art
            random_page = random.randint(1, 1000)
            api_url = f"https://api.artic.edu/api/v1/artworks/search?query[term][is_public_domain]=true&page={random_page}&limit=1&fields=id,title,artist_display,image_id,description,exhibition_history,provenance_text"
            response = requests.get(api_url).json()
            art_data = response['data'][0] if response.get('data') else None

        if not art_data: return None, None, "No art found."

        # Story Logic
        story = art_data.get('description') or art_data.get('exhibition_history') or art_data.get('provenance_text') or "No story available."
        
        # Image Logic
        image_id = art_data.get('image_id')
        image_url = f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg" if image_id else None
        
        return art_data, image_url, story
    except Exception as e:
        print(f"Error: {e}")
        return None, None, "Error fetching art."

def get_recommendations():
    """
    Fetches random artworks. If that fails, falls back to a curated 'Hall of Fame' list.
    """
    clean_recs = [] # Initialize empty list safely
    max_retries = 2 
    
    # --- PLAN A: Random Discovery ---
    for attempt in range(max_retries):
        try:
            # We look at pages 1-100 (Most famous stuff lives here)
            random_page = random.randint(1, 100)
            api_url = f"https://api.artic.edu/api/v1/artworks/search?query[term][is_public_domain]=true&page={random_page}&limit=15&fields=id,title,image_id"
            
            response = requests.get(api_url, timeout=3).json()
            raw_recs = response.get('data', [])
            
            temp_recs = []
            for item in raw_recs:
                if item.get('image_id'):
                    temp_recs.append({
                        'id': item['id'],
                        'title': item['title'],
                        'thumb': f"https://www.artic.edu/iiif/2/{item['image_id']}/full/400,/0/default.jpg"
                    })
                
                if len(temp_recs) >= 3:
                    return temp_recs # Success! We found 3 fresh ones.
                    
        except Exception as e:
            print(f"Random Search Attempt {attempt} failed: {e}")
            continue

    # --- PLAN B: The Safety Net ---
    # If random search failed (empty list or errors), we load these 3 specific masterpieces.
    # 111628 (Nighthawks), 28560 (The Bedroom), 16568 (The Bathers)
    print("Random search failed. Loading Safety Net...")
    fallback_ids = [111628, 28560, 16568] 
    fallback_recs = []
    
    for art_id in fallback_ids:
        try:
            url = f"https://api.artic.edu/api/v1/artworks/{art_id}?fields=id,title,image_id"
            data = requests.get(url, timeout=3).json().get('data')
            if data:
                fallback_recs.append({
                    'id': data['id'],
                    'title': data['title'],
                    'thumb': f"https://www.artic.edu/iiif/2/{data['image_id']}/full/400,/0/default.jpg"
                })
        except:
            pass # Keep going if even one of these fails
            
    return fallback_recs

def get_dominant_color(url):
    # (Keep your existing color code)
    if not url: return "20, 20, 20"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        img_bytes = BytesIO(response.content)
        color_thief = ColorThief(img_bytes)
        c = color_thief.get_color(quality=1)
        return f"{c[0]}, {c[1]}, {c[2]}"
    except:
        return "20, 20, 20"

@app.route('/')
def index():
    # Check if the user clicked a recommendation (URL will look like /?id=12345)
    requested_id = request.args.get('id')
    
    # 1. Get Main Art
    art, img_url, full_story = get_artwork_data(requested_id)
    
    # 2. Get Color
    color = get_dominant_color(img_url)
    
    # 3. Get AI Summary
    summary_points = get_ai_summary(full_story)
    
    # 4. Get 3 New Recommendations
    recommendations = get_recommendations()
    
    return render_template('main.html', art=art, img_url=img_url, color=color, summary_points=summary_points, story=full_story, recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')