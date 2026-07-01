import sys
sys.path.insert(0, ".")
import asyncio
from api.main import app
import uvicorn

# Start server in a thread, then test
import threading, time, requests

def start_server():
    uvicorn.run(app, host="0.0.0.0", port=8005, log_level="info")

t = threading.Thread(target=start_server, daemon=True)
t.start()
time.sleep(4)

# Test
try:
    r = requests.get("http://localhost:8005/api/crawler/spiders", timeout=5)
    print(f"spiders: {r.status_code} {r.text}")
except Exception as e:
    print(f"spiders error: {e}")

try:
    r = requests.get("http://localhost:8005/api/crawler/db-stats", timeout=5)
    print(f"db-stats: {r.status_code} {r.text[:200]}")
except Exception as e:
    print(f"db-stats error: {e}")

# Check OpenAPI
try:
    r = requests.get("http://localhost:8005/openapi.json", timeout=5)
    paths = r.json().get("paths", {})
    crawler_paths = [p for p in paths if "crawl" in p]
    print(f"crawler paths: {crawler_paths}")
    all_paths = sorted(paths.keys())
    print(f"total paths: {len(all_paths)}")
except Exception as e:
    print(f"openapi error: {e}")

print("done")
