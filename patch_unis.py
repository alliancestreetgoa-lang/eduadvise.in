#!/usr/bin/env python3
"""Second pass: fill missing thumbs via Wikidata P18, retry misses, hand-fix sites/blurbs."""
import json
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "EduAdviseLanding/1.0 (contact: hello@eduadvise.in)"}
PATH = "/Users/shuakinsv/Desktop/EDUCA/eduadvise-landing/unis_data.json"


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def wiki_qid_extract(title):
    qs = urllib.parse.urlencode({
        "action": "query", "format": "json", "redirects": 1,
        "prop": "pageimages|extracts|pageprops", "piprop": "thumbnail", "pithumbsize": 640,
        "exintro": 1, "explaintext": 1, "exsentences": 2, "ppprop": "wikibase_item",
        "titles": title,
    })
    data = get(f"https://en.wikipedia.org/w/api.php?{qs}")
    for pid, page in data.get("query", {}).get("pages", {}).items():
        if pid == "-1":
            return None
        return {
            "qid": page.get("pageprops", {}).get("wikibase_item"),
            "thumb": page.get("thumbnail", {}).get("source"),
            "extract": (page.get("extract") or "").strip(),
        }
    return None


def p18_image(qid, width=640):
    try:
        data = get(f"https://www.wikidata.org/w/api.php?action=wbgetclaims&entity={qid}&property=P18&format=json")
        claims = data.get("claims", {}).get("P18", [])
        if claims:
            fname = claims[0]["mainsnak"]["datavalue"]["value"]
            return ("https://commons.wikimedia.org/wiki/Special:FilePath/"
                    + urllib.parse.quote(fname.replace(" ", "_")) + f"?width={width}")
    except Exception:
        pass
    return None


# Re-lookup titles used for thumb/qid resolution per display name
TITLES = {
    "Technological University of Shannon": "Technological University of the Shannon: Midlands Midwest",
    "University of Birmingham, Dubai": "University of Birmingham",
    "Griffith College Ireland": "Griffith College Dublin",
    "SBS Swiss Business School — Barcelona": "SBS Swiss Business School",
    "SBS Swiss Business School — Madrid": "SBS Swiss Business School",
    "ESLSCA Business School Paris": "ESLSCA",
    "Institut Lyfe (Institut Paul Bocuse)": "Institut Paul Bocuse",
    "University of Wollongong, Dubai": "University of Wollongong in Dubai",
    "University of Central Lancashire Cyprus": "UCLan Cyprus",
    "The Emirates Academy of Hospitality Management": "Emirates Academy of Hospitality Management",
}

SITE_FIX = {
    "Wrexham University": "https://www.wrexham.ac.uk",
    "Amity University Dubai": "https://www.amityuniversity.ae",
    "Middlesex University Dubai": "https://www.mdx.ac.ae",
    "University of Central Lancashire Cyprus": "https://www.uclancyprus.ac.cy",
    "SBS Swiss Business School — Barcelona": "https://www.sbs.edu",
    "SBS Swiss Business School — Madrid": "https://www.sbs.edu",
    "GBSB Global Business School": "https://www.global-business-school.org",
    "Holmes Institute": "https://www.holmes.edu.au",
    "Technological University of Shannon": "https://tus.ie",
    "Waterford Institute of Technology": "https://www.setu.ie",
    "The Emirates Academy of Hospitality Management": "https://www.emiratesacademy.edu",
    "Washington University of Science and Technology": "https://wust.edu",
    "École Ducasse": "https://www.ecoleducasse.com",
    "ESLSCA Business School Paris": "https://www.eslsca.fr",
    "Institut Lyfe (Institut Paul Bocuse)": "https://www.institutlyfe.com",
    "University of Birmingham, Dubai": "https://www.birmingham.ac.uk/dubai",
}

BLURB_FIX = {
    "Technological University of Shannon": "Technological University of the Shannon is a multi-campus technological university across Ireland's Midlands and Midwest, with campuses in Limerick, Athlone and Thurles.",
    "The Emirates Academy of Hospitality Management": "The Emirates Academy of Hospitality Management in Dubai is one of the world's leading hospitality business schools, associated with Jumeirah Group and certified by École hôtelière de Lausanne.",
    "Global Business School": "A Dubai-based business school offering internationally accredited undergraduate and postgraduate business programmes for an international student body.",
    "Washington University of Science and Technology": "Washington University of Science and Technology is a private university in Alexandria, Virginia, in the Washington, D.C. metro area, offering career-focused degrees in business, IT and health sciences.",
    "École Ducasse": "École Ducasse is a network of culinary arts and pastry schools created by legendary chef Alain Ducasse, with flagship campuses in and around Paris.",
    "ESLSCA Business School Paris": "ESLSCA Business School Paris is a French business school founded in 1949, recognised for its programmes in finance, management and international business.",
    "Institut Lyfe (Institut Paul Bocuse)": "Institut Lyfe, formerly Institut Paul Bocuse, in Lyon is among the world's most prestigious schools of culinary arts and hospitality management.",
    "University of Birmingham, Dubai": "The University of Birmingham Dubai brings the British Russell Group university's degrees to Dubai International Academic City, taught on a purpose-built campus.",
}

with open(PATH) as f:
    data = json.load(f)

for country, unis in data.items():
    for rec in unis:
        name = rec["name"]
        # Retry lookup for records missing thumb or blurb
        if not rec.get("thumb") or not rec.get("blurb"):
            title = TITLES.get(name, name)
            info = None
            try:
                info = wiki_qid_extract(title)
            except Exception as e:
                print(f"  ! {name}: {e}")
            if info:
                if not rec.get("blurb") and info.get("extract"):
                    rec["blurb"] = info["extract"]
                if not rec.get("thumb"):
                    rec["thumb"] = info.get("thumb") or p18_image(info.get("qid"))
            time.sleep(0.15)
        if name in SITE_FIX:
            rec["site"] = SITE_FIX[name]
        if name in BLURB_FIX and (not rec.get("blurb") or name in BLURB_FIX):
            rec["blurb"] = BLURB_FIX.get(name, rec.get("blurb"))
        status = []
        status.append("img" if rec.get("thumb") else "NO-IMG")
        status.append("blurb" if rec.get("blurb") else "NO-BLURB")
        status.append("site" if rec.get("site") else "NO-SITE")
        print(f"  [{'/'.join(status)}] {name}")

with open(PATH, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print("\nPatched unis_data.json")
