# -*- coding: utf-8 -*-
"""发布脚本：把本地仓库的变更文件同步到 GitHub（Contents API，不依赖网页通道）。

用法：在仓库目录运行  python publish_repo.py
令牌来源（按优先级）：环境变量 GH_TOKEN > C:\\Users\\Administrator\\jb-repo.token > 仓库内 .token
"""
import os, sys, json, base64, hashlib, urllib.request, urllib.error

OWNER = "TLzypjy"
REPO = "jb-repo"
ROOT = os.path.dirname(os.path.abspath(__file__))
API = "https://api.github.com"

def get_token():
    t = os.environ.get("GH_TOKEN")
    if t:
        return t
    for p in (os.path.join(os.path.expanduser("~"), "jb-repo.token"),
              os.path.join(ROOT, ".token")):
        if os.path.exists(p):
            with open(p, "r") as f:
                return f.read().strip()
    print("错误：未找到令牌。请设置环境变量 GH_TOKEN，或把令牌写入 C:\\Users\\Administrator\\jb-repo.token")
    sys.exit(1)

TOKEN = get_token()

def api(method, path, payload=None, timeout=120):
    req = urllib.request.Request(API + path, method=method)
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "jb-repo-publisher")
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, data=data, timeout=timeout) as r:
            body = r.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        print("HTTP %s %s -> %s" % (method, path, e.code))
        print(e.read().decode("utf-8", "replace")[:500])
        sys.exit(1)

def git_blob_sha1(data):
    h = hashlib.sha1()
    h.update(b"blob %d\x00" % len(data))
    h.update(data)
    return h.hexdigest()

# 1. 本地文件清单
local = {}
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git",)]
    if ".git" in dirpath:
        continue
    for fn in filenames:
        full = os.path.join(dirpath, fn)
        rel = os.path.relpath(full, ROOT).replace("\\", "/")
        with open(full, "rb") as f:
            data = f.read()
        local[rel] = (data, git_blob_sha1(data))

# 2. 远端当前文件 SHA（tree API，一次拿全）
tree = api("GET", "/repos/%s/%s/git/trees/main?recursive=1" % (OWNER, REPO))
remote = {}
for it in tree.get("tree", []):
    if it.get("type") == "blob":
        remote[it["path"]] = it["sha"]

# 3. 对比并上传变更
changes = 0
for rel, (data, sha) in sorted(local.items()):
    if remote.get(rel) == sha:
        continue
    payload = {"message": "update %s" % rel, "content": base64.b64encode(data).decode("ascii"), "branch": "main"}
    if rel in remote:
        payload["sha"] = remote[rel]
    api("PUT", "/repos/%s/%s/contents/%s" % (OWNER, REPO, rel), payload)
    print("已更新: %s" % rel)
    changes += 1

if changes == 0:
    print("没有变更，仓库已是最新。")
else:
    print("发布完成，共更新 %d 个文件。" % changes)
    print("源地址: https://%s.github.io/%s/" % (OWNER, REPO))
