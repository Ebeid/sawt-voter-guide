# Sawt — صوت

**Live site:** https://ebeid.github.io/sawt-voter-guide/

Sawt is a mobile-friendly guide for Muslim voters who want to follow
[CAIR Action's 2026 endorsements](https://cairaction.org/endorsements/).
*Sawt* means both "voice" and "vote" in Arabic.

> **Unofficial.** Sawt is an independent companion to CAIR Action's voter
> guides. It is not made, endorsed or reviewed by CAIR Action. Always confirm
> against the official guide before you vote.

## What it does

- **Step by step:** enter a ZIP code and walk through your ballot in its usual
  order (statewide offices, Congress, legislature, courts, county, city,
  schools, measures). For district races it asks which district you're in,
  because a ZIP code can cross district lines and several states redrew their
  maps for 2026.
- **All races:** browse, search and filter every endorsement by state.
- **My list:** the races on your ballot, in ballot order, ready to copy or send
  on WhatsApp. Stored only in your browser.
- **Seven languages:** English, Arabic, Urdu, Bengali, Somali, Persian and
  Turkish, with right-to-left layout and script-appropriate fonts. Candidate
  and office names stay in English to match the printed ballot. Translations
  were prepared with AI help and need review by native speakers.
- Works on any phone browser with nothing to install, and can be added to the
  home screen.

## Data

- Endorsements were copied from the state guides CAIR Action published for the
  November 3, 2026 general election, as of **October 18, 2026** (26 states).
  Nevada, New Hampshire and Wisconsin had no guide published yet.
- ZIP-to-county data comes from the
  [`zipcodes`](https://github.com/seanpianka/zipcodes) package (MIT License,
  see `src/vendor/zipcodes-LICENSE.txt`).

## Updating

Everything is one static page, built from the files in `src/`:

| File | What it holds |
|---|---|
| `src/data/*.json` | Endorsements per state: `[section, name, office, status]` for candidates, `["M", title, status, locality, description]` for measures |
| `src/classify.py` | Ballot order, district families, and county/city/school jurisdiction rules |
| `src/template.html` | The page: styles, translations and app logic |
| `src/build.py` | Combines the above into `index.html` |

Status codes: `E` endorsed, `P` preferred, `J` joint endorsement, `O` oppose,
`W` already won, `X` no endorsement; for measures `Y` support, `N` oppose,
`X` no recommendation.

To rebuild after editing:

```sh
python3 src/build.py
```

Then commit `index.html` along with your source changes. GitHub Pages serves
the repository root from the `main` branch.
