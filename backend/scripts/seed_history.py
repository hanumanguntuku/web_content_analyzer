# Simple helper to seed analysis_history.json for local development
import os
import json
import time

HERE = os.path.abspath(os.path.dirname(__file__))
BACKEND_ROOT = os.path.abspath(os.path.join(HERE, '..'))
HISTORY_FILE = os.path.join(BACKEND_ROOT, 'analysis_history.json')

sample = {
    "url": "https://example.com",
    "title": "Example Domain",
    "timestamp": time.time(),
    "overall_quality_score": 78.5,
    "extraction_quality": 85,
    "processing_quality": 90,
    "seo_score": 72,
    "readability_score": 80
}

if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump([sample], f, indent=2)
    print(f"Created {HISTORY_FILE}")
else:
    # append
    try:
        with open(HISTORY_FILE, 'r+', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        data = []
    data.append(sample)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Appended to {HISTORY_FILE}")
