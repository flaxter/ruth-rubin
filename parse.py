#!/usr/bin/env python3
"""Parse cached Ruth Rubin item HTML into structured JSON + CSV."""
import os, re, json, csv, html, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
HTML_DIR = os.path.join(ROOT, "data", "html")
OUT_JSON = os.path.join(ROOT, "data", "items.json")
OUT_CSV = os.path.join(ROOT, "data", "items.csv")

# Metadata fields look like:
#   <div id='SECTION-field' class='element ...'><h3>Label</h3>
#     <div class='element-text'>VALUE</div><div class='element-text'>VALUE2</div></div>
# We segment the metadata region at each opening "<div id='X' class='element ",
# then within each segment grab the <h3> label and all element-text values.
ELEM_OPEN_RE = re.compile(r"<div id='([a-z0-9-]+)' class='element ")
ETEXT_RE = re.compile(r"<div class='element-text'>(.*?)</div>", re.S)

def clean(s):
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()

def parse(path):
    h = open(path, encoding="utf-8", errors="replace").read()
    item_id = int(os.path.splitext(os.path.basename(path))[0])
    # restrict to item-metadata block
    mstart = h.find('id="item-metadata"')
    mend = h.find('id="item-citation"')
    if mend == -1:
        mend = h.find("This item has no relations")
    region = h[mstart:mend] if mstart != -1 else h
    rec = {"id": item_id, "url": f"https://ruthrubin.yivo.org/items/show/{item_id}"}
    # generic element extraction: segment region at each element-block opening
    opens = list(ELEM_OPEN_RE.finditer(region))
    for i, m in enumerate(opens):
        seg = region[m.end():opens[i + 1].start() if i + 1 < len(opens) else len(region)]
        lab = re.search(r"<h3>(.*?)</h3>", seg, re.S)
        if not lab:
            continue
        key = clean(lab.group(1)).lower().replace(" ", "_")
        if not key:
            continue
        vals = [clean(t) for t in ETEXT_RE.findall(seg) if clean(t)]
        if not vals:
            continue
        rec[key] = vals[0] if len(vals) == 1 else " ; ".join(vals)
    # title fallback
    if "title" not in rec:
        mt = re.search(r"<title>(.*?)(?: &middot;| &#183;|·)", h)
        if mt:
            rec["title"] = clean(mt.group(1))
    # audio file
    ma = re.search(r"(https?://[^\"' ]+\.mp3)", h)
    rec["audio"] = ma.group(1) if ma else ""
    rec["has_audio"] = bool(ma)
    # image thumbnail
    mi = re.search(r"(https?://[^\"' ]+/(?:fullsize|square_thumbnails)/[^\"' ]+)", h)
    rec["image"] = mi.group(1) if mi else ""
    return rec

def main():
    files = sorted(glob.glob(os.path.join(HTML_DIR, "*.html")),
                   key=lambda p: int(os.path.splitext(os.path.basename(p))[0]))
    recs = []
    for p in files:
        try:
            r = parse(p)
            # keep only items with a real title
            if r.get("title"):
                recs.append(r)
        except Exception as e:
            print("ERR", p, e)
    # write json
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    json.dump(recs, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    # union of keys for csv
    keys = []
    for r in recs:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in recs:
            w.writerow(r)
    # quick field-coverage report
    from collections import Counter
    cov = Counter()
    for r in recs:
        for k in r:
            cov[k] += 1
    print(f"parsed {len(recs)} items")
    for k, c in cov.most_common():
        print(f"  {c:5d}  {k}")

if __name__ == "__main__":
    main()
