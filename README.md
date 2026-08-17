# 🏄 Surf Guide — Claude Skill

A personal surf guide skill for [Claude](https://claude.ai). Give it a location and your ability level, and it pulls live forecast data to tell you which spots are worth paddling out at — and when.

## What it does

1. **Asks once** for your surf level and stores it, so you don't repeat yourself every session
2. **Finds spots** near your location, filters out anything above your level or unsuitable for the conditions
3. **Pulls live data** — swell, wind, tides, water temperature — via [Open-Meteo](https://open-meteo.com/) (free, no API key)
4. **Rates and ranks** what's left, with a time window and honest uncertainty
5. **Remembers spots** you've checked before, so repeat visits are instant

Built for surfers of all levels. Beginners get plain-language explanations and conservative safety filters. Experienced surfers get the full picture without hand-holding.

## Example

> **You:** How's it looking in Sagres today? I'm on a softtop, just finished my first week of lessons.
>
> **Claude:** *Sagres, nice — give me a minute to check what's running.*
>
> *[researches spots, pulls forecast, checks tides]*
>
> **Tonel is your spot** — 1.0 m at 6 s with the wind blowing off the land, best window 9am to 1pm while the tide drops. Small and soft, but on the softtop you'll catch plenty. 3/2 mm wetsuit at 18.5 °C water...

## Install

### As a Claude skill (recommended)

1. Download the `.skill` file from [Releases](../../releases)
2. In Claude → Settings → Skills → drag the file in

### Manual

Copy the folder structure into your Claude skills directory:

```
surf-guide/
├── SKILL.md              # Main skill instructions
├── references/
│   └── guide.md          # Levels, scoring, data sources, glossary
└── scripts/
    └── forecast.py       # Open-Meteo fetcher (swell, wind, weather)
```

## Setup for best results

### Network allowlist (optional but recommended)

The skill includes a Python script that pulls forecast data directly from Open-Meteo — much faster and cheaper than scraping forecast websites. To enable it:

**Settings → Capabilities → Code execution and file creation → Domain allowlist**

Add these two domains:
- `marine-api.open-meteo.com`
- `api.open-meteo.com`

Without this, the skill falls back to web searches on surf-forecast.com. It works, just slower and more expensive in tokens.

### Memory (optional)

If memory is enabled, the skill stores:
- **Your surf level** in `/topics/surfing.md` — so it doesn't ask every time
- **Verified spot data** in `/topics/surf-spots.md` — coordinates, orientation, break type, cam links

Both build up naturally as you use the skill. Nothing is stored without your input.

## How it rates spots

The skill uses a weighted scoring system after filtering out anything that fails safety checks:

| Factor | Weight |
|---|---|
| Wind (direction + strength) | 35% |
| Swell quality (period + cleanliness) | 25% |
| Size matched to your level | 25% |
| Tide window at the right time | 15% |

Spots above your level are **excluded**, not downgraded — even if they're the best wave of the day.

## Data sources

| Source | What for | Access |
|---|---|---|
| [Open-Meteo Marine API](https://open-meteo.com/) | Swell, wind, water temp | Free, CC BY 4.0 |
| Web search | Tide times | Free |
| [Surfline](https://www.surfline.com/) | Spot descriptions, level notes | Public pages only (no paywall bypass) |
| [surf-forecast.com](https://www.surf-forecast.com/) | Spot orientation, fallback forecast | Free |

## Limitations

- **Wave models aren't cameras.** They run on multi-km grids and don't know sandbanks or local refraction. The skill says this when it matters and points you to a webcam.
- **Complex coasts** (peninsulas, island lees) can fool the model systematically. The skill switches to local forecast sources when it recognises this.
- **Tides** come from web search, not the model. Occasionally the search misses — the skill flags when tide data is absent.
- **Beyond 3 days**, wind and wave-shape predictions lose reliability fast. The skill says so instead of faking precision.

## License

[MIT](LICENSE)

## Credits

Forecast data by [Open-Meteo](https://open-meteo.com/) under CC BY 4.0.
