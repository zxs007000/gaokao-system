import urllib.request, json, os, base64

# Check if repo exists first
req = urllib.request.Request("https://api.github.com/repos/zxs007000/gaokao-system")
req.add_header("User-Agent", "hermes-agent")
try:
    resp = urllib.request.urlopen(req)
    r = json.loads(resp.read())
    print(f"仓库存在: {r['html_url']}")
    print(f"默认分支: {r['default_branch']}")
except urllib.error.HTTPError as e:
    print(f"错误 {e.code}: {e.read().decode()[:200]}")

os.remove(__file__)
