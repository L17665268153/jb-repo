# -*- coding: utf-8 -*-
"""删除 GitHub 远端单个文件（Contents API DELETE）"""
import os, sys, urllib.request, urllib.error, json

OWNER = "TLzypjy"
REPO = "jb-repo"
API = "https://api.github.com"

def get_token():
    t = os.environ.get("GH_TOKEN")
    if t:
        return t
    for p in (os.path.join(os.path.expanduser("~"), "jb-repo.token"),
              os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".token")):
        if os.path.exists(p):
            with open(p, "r") as f:
                return f.read().strip()
    print("无 token")
    sys.exit(1)

TOKEN = get_token()
path = sys.argv[1] if len(sys.argv) > 1 else ""

def api(method, p, payload=None):
    req = urllib.request.Request(API + p, method=method)
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "jb-repo-publisher")
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, data=data, timeout=120) as r:
            body = r.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        print("HTTP %s %s -> %s" % (method, p, e.code))
        print(e.read().decode("utf-8", "replace")[:300])
        sys.exit(1)

if not path:
    print("用法: python delete_remote.py <path>")
    sys.exit(1)

# 取 sha
info = api("GET", "/repos/%s/%s/contents/%s" % (OWNER, REPO, path))
sha = info.get("sha")
if not sha:
    print("远端不存在或无法获取 sha:", path)
    sys.exit(1)
api("DELETE", "/repos/%s/%s/contents/%s" % (OWNER, REPO, path), {"message": "remove old deb", "sha": sha, "branch": "main"})
print("已删除远端:", path)
