# Ruth Rubin Sound Archive — Data Explorer

An interactive, single-page explorer for the [YIVO Ruth Rubin Legacy Archive of
Yiddish Folksong](https://ruthrubin.yivo.org/) — the field recordings Ruth Rubin
gathered from singers between 1946 and the 1970s.

**Live site:** https://flaxter.github.io/ruth-rubin/

It is an unofficial research aid. Data and audio © YIVO Institute for Jewish
Research; recordings stream directly from YIVO's servers.

## What's here

- **`index.html`** — the whole explorer, self-contained (data embedded inline).
  Summary stats; charts of recordings over time, top performers, genres,
  recording locations, songs-per-tape, and performer gender (all click-to-filter);
  a searchable/sortable table of every recording with inline audio playback and a
  playback-speed control; shareable URL permalinks for every filter; and an
  "album → field recordings" browser that maps tracks of Ruth Rubin albums (e.g.
  the 1957 Folkways LP *Jewish Children's Songs and Games*) to the archival
  recordings that may have informed them.

## How it was built (reproducible pipeline)

1. **`scrape.py`** — fetches every `/items/show/N` page from ruthrubin.yivo.org
   into a local cache (`data/html/`, git-ignored).
2. **`parse.py`** — parses the cached pages into `data/items.json` / `data/items.csv`
   (title, performer, gender, lyricist, composer, date, location, tape, track,
   description, audio URL, …).
3. **`build_site.py`** — emits `index.html` with the dataset embedded.

```bash
python3 scrape.py      # ~2,450 pages, cached
python3 parse.py       # -> data/items.json + data/items.csv
python3 build_site.py  # -> index.html
```

The committed `data/items.json` / `data/items.csv` let you rebuild the site
without re-scraping.
