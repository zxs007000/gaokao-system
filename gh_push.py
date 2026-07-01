import urllib.request, urllib.error
import json, base64, os, sys, hashlib, time

TOKEN = sys.stdin.readline().strip()
OWNER = "zxs007000"
REPO_NAME = "gaokao-system"

def api(url, data=None, method=None, timeout=30):
    headers = {
        "Authorization": f"token {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "hermes-agent",
        "Accept": "application/vnd.github.v3+json"
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(
        f"https://api.github.com{url}", data=body, headers=headers,
        method=method or ("POST" if body else "GET")
    )
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err = e.read().decode()[:200]
        print(f"  ERR {e.code} on {url[:60]}: {err}")
        raise

# Get initial commit info
repo = api(f"/repos/{OWNER}/{REPO_NAME}")
default_branch = repo["default_branch"]
ref = api(f"/repos/{OWNER}/{REPO_NAME}/git/refs/heads/{default_branch}")
initial_commit_sha = ref["object"]["sha"]
initial_commit = api(f"/repos/{OWNER}/{REPO_NAME}/git/commits/{initial_commit_sha}")
initial_tree_sha = initial_commit["tree"]["sha"]
initial_tree = api(f"/repos/{OWNER}/{REPO_NAME}/git/trees/{initial_tree_sha}")
print(f"Repo ready, commit: {initial_commit_sha[:8]}")

# Walk and collect files
REPO_PATH = "D:\\gaokao-system"
EXCLUDED = {"__pycache__", "node_modules", ".next", ".hermes", ".git"}
IGNORE_SUFFIXES = {".pyc", ".log"}
IGNORE_FILES = {"frontend_err.txt", "frontend_log.txt"}

files_to_push = []
for root, dirs, files in os.walk(REPO_PATH):
    dirs[:] = [d for d in dirs if d not in EXCLUDED and not d.startswith(".")]
    for f in files:
        full = os.path.join(root, f)
        rel = os.path.relpath(full, REPO_PATH).replace("\\", "/")
        if any(rel.startswith(p + "/") for p in EXCLUDED) or rel.startswith(".git/"):
            continue
        if any(rel.endswith(s) for s in IGNORE_SUFFIXES) or f in IGNORE_FILES:
            continue
        if "screenshot" in rel.lower() and rel.endswith(".png"):
            continue
        if rel == "README.md":
            continue
        with open(full, "rb") as fh:
            content = fh.read()
        files_to_push.append((rel, content))

N = len(files_to_push)
print(f"Files: {N}")

# Create blobs
blob_map = {}
for i, (path, content) in enumerate(files_to_push):
    is_lfs = path.startswith("data/db/") and path.endswith(".db")
    if is_lfs:
        s = os.path.getsize(os.path.join(REPO_PATH, path))
        h = hashlib.sha256(content).hexdigest()
        content = f"version https://git-lfs.github.com/spec/v1\noid sha256:{h}\nsize {s}\n".encode()
    
    for attempt in range(3):
        try:
            encoded = base64.b64encode(content).decode()
            res = api(f"/repos/{OWNER}/{REPO_NAME}/git/blobs", {"content": encoded, "encoding": "base64"}, timeout=30)
            blob_map[path] = res["sha"]
            break
        except Exception as e:
            if attempt == 2:
                print(f"  FAILED: {path}")
                raise
            time.sleep(2)
    
    if (i+1) % 20 == 0 or i == N:
        print(f"  Blobs: {i+1}/{N}")

print("All blobs done!")

# Create tree
tree_items = [item for item in initial_tree["tree"] if item["path"] not in blob_map]
for path, sha in blob_map.items():
    ext = os.path.splitext(path)[1]
    mode = "100755" if ext in (".sh", ".bat", ".py", ".exe") else "100644"
    tree_items.append({"path": path, "mode": mode, "type": "blob", "sha": sha})

res = api(f"/repos/{OWNER}/{REPO_NAME}/git/trees", {"tree": tree_items})
tree_sha = res["sha"]
print(f"Tree: {tree_sha}")

# Create commit
res = api(f"/repos/{OWNER}/{REPO_NAME}/git/commits", {
    "message": "feat: 初始开源版本 — 完整的高考志愿分析平台",
    "tree": tree_sha,
    "parents": [initial_commit_sha],
    "author": {"name": OWNER, "email": f"{OWNER}@users.noreply.github.com"}
})
commit_sha = res["sha"]
print(f"Commit: {commit_sha}")

# Update ref
api(f"/repos/{OWNER}/{REPO_NAME}/git/refs/heads/{default_branch}", {"sha": commit_sha, "force": True})

print(f"\\nDone! https://github.com/{OWNER}/{REPO_NAME}")
os.remove(__file__)
