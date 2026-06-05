#!/usr/bin/env python3
"""Fetch Wikipedia thumbnail, summary and official website for each partner university."""
import json
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "EduAdviseLanding/1.0 (contact: hello@eduadvise.in)"}

UNIS = {
    "Ireland": [
        ("Dublin City University", None),
        ("University College Dublin", None),
        ("University College Cork", None),
        ("Technological University Dublin", None),
        ("University of Limerick", None),
        ("Maynooth University", None),
        ("Technological University of Shannon", "Technological University of the Shannon"),
        ("Waterford Institute of Technology", None),
        ("Dundalk Institute of Technology", None),
        ("Dublin Business School", None),
        ("Griffith College Ireland", "Griffith College Dublin"),
        ("National College of Ireland", None),
        ("Holmes Institute", None),
    ],
    "United Kingdom": [
        ("University of Northampton", None),
        ("Anglia Ruskin University", None),
        ("Buckinghamshire New University", None),
        ("Abertay University", None),
        ("Wrexham University", None),
        ("Aberystwyth University", None),
        ("Arts University Bournemouth", None),
        ("Bangor University", None),
    ],
    "UAE": [
        ("Amity University Dubai", None),
        ("University of Wollongong, Dubai", "University of Wollongong in Dubai"),
        ("University of Birmingham, Dubai", "University of Birmingham Dubai"),
        ("Canadian University Dubai", None),
        ("Middlesex University Dubai", None),
        ("The Emirates Academy of Hospitality Management", "Emirates Academy of Hospitality Management"),
        ("Global Business School", None),
    ],
    "USA": [
        ("Monroe College", None),
        ("Jessup University", None),
        ("Culinary Institute of America", None),
        ("Washington University of Science and Technology", None),
        ("City University of Seattle", None),
        ("Northwood University", None),
    ],
    "Spain": [
        ("SBS Swiss Business School — Barcelona", "SBS Swiss Business School"),
        ("SBS Swiss Business School — Madrid", "SBS Swiss Business School"),
        ("EAE Business School", None),
        ("GBSB Global Business School", None),
    ],
    "France": [
        ("École Ducasse", None),
        ("ESLSCA Business School Paris", "ESLSCA"),
        ("Institut Lyfe (Institut Paul Bocuse)", "Institut Paul Bocuse"),
    ],
    "Italy": [
        ("Rome Business School", None),
        ("Università Cattolica del Sacro Cuore", None),
    ],
    "Cyprus": [
        ("University of Nicosia", None),
        ("University of Central Lancashire Cyprus", "UCLan Cyprus"),
    ],
    "Switzerland": [("Glion Institute of Higher Education", None)],
    "Canada": [("Crandall University", None)],
}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def wiki_lookup(title):
    qs = urllib.parse.urlencode({
        "action": "query", "format": "json", "redirects": 1,
        "prop": "pageimages|extracts|pageprops|info",
        "piprop": "thumbnail", "pithumbsize": 640,
        "exintro": 1, "explaintext": 1, "exsentences": 2,
        "ppprop": "wikibase_item", "inprop": "url",
        "titles": title,
    })
    data = get(f"https://en.wikipedia.org/w/api.php?{qs}")
    pages = data.get("query", {}).get("pages", {})
    for pid, page in pages.items():
        if pid == "-1":
            return None
        return {
            "thumb": page.get("thumbnail", {}).get("source"),
            "extract": (page.get("extract") or "").strip(),
            "qid": page.get("pageprops", {}).get("wikibase_item"),
            "wiki": page.get("fullurl"),
        }
    return None


def official_site(qid):
    if not qid:
        return None
    try:
        data = get(f"https://www.wikidata.org/w/api.php?action=wbgetclaims&entity={qid}&property=P856&format=json")
        claims = data.get("claims", {}).get("P856", [])
        if claims:
            return claims[0]["mainsnak"]["datavalue"]["value"]
    except Exception:
        pass
    return None


out = {}
for country, unis in UNIS.items():
    out[country] = []
    for display, override in unis:
        title = override or display
        info = None
        try:
            info = wiki_lookup(title)
        except Exception as e:
            print(f"  ! {display}: {e}")
        site = official_site(info["qid"]) if info else None
        rec = {
            "name": display,
            "thumb": info["thumb"] if info else None,
            "blurb": info["extract"] if info else None,
            "site": site,
            "wiki": info["wiki"] if info else None,
        }
        out[country].append(rec)
        status = "ok" if info and info.get("thumb") else ("no-img" if info else "MISS")
        print(f"  [{status}] {display} -> site={site}")
        time.sleep(0.15)

with open("/Users/shuakinsv/Desktop/EDUCA/eduadvise-landing/unis_data.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("\nSaved unis_data.json")
