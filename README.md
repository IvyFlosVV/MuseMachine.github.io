# Muse & Machine

**Muse & Machine** is an interactive web experience that bridges historical art with modern artificial intelligence. It serves as a serendipitous discovery engine, pulling random masterpieces from the archives and using AI to translate academic descriptions into engaging, bite-sized insights.

## Features

* **Serendipitous Discovery:** Fetches random artworks from the public domain archives.
* **AI Curator:** Uses **Google Gemini 2.0 Flash Lite** to rewrite complex art history texts into three exciting, digestible bullet points.
* **Smart Fallbacks:** Includes a custom text-slicing algorithm to generate summaries locally if the AI API hits a rate limit.
* **Dynamic Aesthetics:** Extracts the dominant color from the artwork to tint the "Aurora" background animation.
* **Infinite Scroll:** A recommendation engine fetches 3 visually similar or random artworks to keep the exploration going.
* **Visual Polish:** Features a high-end "Glassmorphism" UI with a liquid cursor trail and 3D tilt effects.

## APIs Used

1.  **Art Institute of Chicago API:**
    * Used to fetch artwork metadata, high-resolution IIIF images, and historical descriptions.
    * Endpoint: `https://api.artic.edu/api/v1/artworks`
2.  **Google Gemini API (Generative Language):**
    * Used to summarize art descriptions into "Curator Notes."
    * Model: `gemini-2.0-flash-lite` (with fallbacks to standard Flash).

## Installation & Setup

### 1. Prerequisites
* Python 3.8 or higher
* A Google Gemini API Key (Get one [here](https://aistudio.google.com/app/apikey))

### 2. Clone the Repository
```bash
git clone [https://github.com/yourusername/muse-and-machine.git](https://github.com/yourusername/muse-and-machine.git)
cd muse-and-machine
