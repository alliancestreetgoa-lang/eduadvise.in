#!/usr/bin/env python3
"""Download a real image for every university into img/ (Wikimedia thumb -> og:image -> Commons search)."""
import json
import os
import re
import time
import urllib.parse
import urllib.request

BASE = "/Users/shuakinsv/Desktop/EDUCA/eduadvise-landing"
IMG_DIR = os.path.join(BASE, "img")
os.makedirs(IMG_DIR, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"}
WIKI_UA = {"User-Agent": "EduAdviseLanding/1.0 (https://eduadvise.in; hello@eduadvise.in) python-urllib"}


def fetch(url, binary=False, retries=2):
    headers = WIKI_UA if ("wikimedia.org" in url or "wikipedia.org" in url) else UA
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=25) as r:
                data = r.read()
                ctype = r.headers.get("Content-Type", "")
                return (data, ctype) if binary else (data.decode("utf-8", "replace"), ctype)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries:
                time.sleep(6)
                continue
            raise
    raise RuntimeError("unreachable")


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s[:60]


def ext_for(ctype, url):
    if "png" in ctype: return ".png"
    if "webp" in ctype: return ".webp"
    if "svg" in ctype: return ".svg"
    if "jpeg" in ctype or "jpg" in ctype: return ".jpg"
    m = re.search(r"\.(jpe?g|png|webp)(?:\?|$)", url.lower())
    return f".{m.group(1)}" if m else ".jpg"


def save_image(url, slug):
    data, ctype = fetch(url, binary=True)
    if len(data) < 4000:  # skip tiny tracking pixels / favicons
        raise ValueError(f"too small ({len(data)}b)")
    ext = ext_for(ctype, url)
    if ext == ".svg":
        raise ValueError("svg skipped")
    path = os.path.join(IMG_DIR, slug + ext)
    with open(path, "wb") as f:
        f.write(data)
    return f"img/{slug}{ext}"


def og_image(site):
    html, _ = fetch(site)
    for pat in (r'property=["\']og:image["\'][^>]*content=["\']([^"\']+)',
                r'content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']',
                r'name=["\']twitter:image["\'][^>]*content=["\']([^"\']+)'):
        m = re.search(pat, html, re.I)
        if m:
            return urllib.parse.urljoin(site, m.group(1).strip())
    return None


def commons_search(name):
    qs = urllib.parse.urlencode({
        "action": "query", "format": "json", "list": "search",
        "srnamespace": 6, "srlimit": 5,
        "srsearch": f"{name} campus building",
    })
    raw, _ = fetch(f"https://commons.wikimedia.org/w/api.php?{qs}")
    hits = json.loads(raw).get("query", {}).get("search", [])
    for h in hits:
        title = h["title"]  # "File:..."
        if re.search(r"\.(jpe?g|png|webp)$", title, re.I):
            fname = title.split(":", 1)[1]
            return ("https://commons.wikimedia.org/wiki/Special:FilePath/"
                    + urllib.parse.quote(fname.replace(" ", "_")) + "?width=800")
    return None


with open(os.path.join(BASE, "unis_data.json")) as f:
    data = json.load(f)

for country, unis in data.items():
    for rec in unis:
        name, slug = rec["name"], slugify(rec["name"])
        # skip if already downloaded
        existing = [f for f in os.listdir(IMG_DIR) if f.startswith(slug + ".")]
        if existing:
            rec["local"] = f"img/{existing[0]}"
            print(f"  [cached] {name}")
            continue
        local = None
        # 1. Wikimedia thumb we already have
        if rec.get("thumb"):
            try:
                local = save_image(rec["thumb"], slug)
                src = "wiki"
            except Exception as e:
                print(f"    wiki thumb failed for {name}: {e}")
        # 2. og:image from official site
        if not local and rec.get("site"):
            try:
                og = og_image(rec["site"])
                if og:
                    local = save_image(og, slug)
                    src = "og"
            except Exception as e:
                print(f"    og:image failed for {name}: {e}")
        # 3. Commons search
        if not local:
            try:
                cs = commons_search(name)
                if cs:
                    local = save_image(cs, slug)
                    src = "commons"
            except Exception as e:
                print(f"    commons failed for {name}: {e}")
        if local:
            rec["local"] = local
            print(f"  [{src}] {name} -> {local}")
        else:
            print(f"  [NONE] {name}")
        time.sleep(0.6)

with open(os.path.join(BASE, "unis_data.json"), "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print("\nDone.")
