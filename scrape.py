#!/usr/bin/env python3
"""Scrape Ruth Rubin Legacy Archive item pages, caching HTML to data/html/."""
import os, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://ruthrubin.yivo.org/items/show/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "html")
os.makedirs(OUT, exist_ok=True)

LO, HI = 1800, 6660  # generous range; 404s are skipped
HEADERS = {"User-Agent": "Mozilla/5.0 (research; contact flaxter@gmail.com) ruthrubin-dataviz"}

def fetch(n):
    path = os.path.join(OUT, f"{n}.html")
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return (n, "cached")
    req = urllib.request.Request(BASE + str(n), headers=HEADERS)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            with open(path, "wb") as f:
                f.write(data)
            return (n, "ok")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return (n, "404")
            time.sleep(1 + attempt)
        except Exception:
            time.sleep(1 + attempt)
    return (n, "fail")

def main():
    ids = list(range(LO, HI + 1))
    ok = c = nf = fail = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fetch, n): n for n in ids}
        for i, fut in enumerate(as_completed(futs)):
            n, st = fut.result()
            if st in ("ok",): ok += 1
            elif st == "cached": c += 1
            elif st == "404": nf += 1
            else: fail += 1
            if (i + 1) % 200 == 0:
                print(f"{i+1}/{len(ids)} done | ok={ok} cached={c} 404={nf} fail={fail}", flush=True)
    print(f"DONE ok={ok} cached={c} 404={nf} fail={fail} total_saved={ok+c}", flush=True)

if __name__ == "__main__":
    main()
