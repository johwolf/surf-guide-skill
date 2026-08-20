# Reference: levels, rating, data sources

## Level tiers

| Tier | Description | Max face height | Breaks |
|---|---|---|---|
| 1 — Starting out | Whitewater, softtop, first take-offs | ≤ 0.8 m | sand, no reef, no rips |
| 2 — Getting there | Green waves, angles along, no duck dive | ≤ 1.2 m | gentle beach/point |
| 3 — Solid | Reads lineup, duck dive, links turns | ≤ 2.0 m | beach, point, easy reef |
| 4 — Experienced | Surfs overhead, picks spots unaided | open | reef, power spots |

When in doubt, drop one tier and say so.

## Beginner inversion

Public ratings (stars, x/10) measure energy → calibrated for tier 3–4.
For tier 1–2 the scale is partly upside down:

| Source rating | Tier 1–2 | Tier 3–4 |
|---|---|---|
| 0–2 | often the **target**: small, clean, learnable | flat |
| 3–5 | usable, near ceiling | solid |
| 6–8 | too much push / current | very good |
| 9–10 | ruled out | highlight |

**Never pass a source rating through.** Rate against the level yourself.

## Knockouts (don't enter ranking)

1. Above their level (height or break type)
2. Swell misses the spot's window → flat
3. Wrong tide → dangerous or dead
4. Onshore ≥ 25 kn (46 km/h) → junk
5. Live hazard: rip on this swell, shark, closure, sewage

Tier 1–2 extra: no reef, no documented rips, no wind > 15 kn (28 km/h).

## Scoring (after knockouts)

| Factor | Weight |
|---|---|
| Wind direction + strength | 35 % |
| Swell quality (period + cleanliness) | 25 % |
| Size vs level | 25 % |
| Tide window at intended time | 15 % |

Always give score + reason. Crowd and drive time go in the detail, not the score.

## Quick number guide

**Wind** (biggest factor, all thresholds in knots; 1 kn = 1.85 km/h):
offshore 3–12 kn ideal, > 20 kn shuts take-off down;
onshore > 15 kn ugly, > 25 kn junk; glassy < 5 kn best of all.

**Period**: < 8 s windswell (gutless); 8–11 s workable; 12–15 s groundswell
(clean, powerful); > 16 s serious push, breaks bigger than height suggests.

**Tide**: shifts ~50 min/day. Always give HW/LW times. Big-range coasts
(France, Portugal, UK): window often only 2–3 h.

**Model height ≠ face height.** Communicate as estimate.

## Wetsuit

| Water | Call |
|---|---|
| > 24 °C | boardshorts | 21–24 | shorty / 2 mm | 18–21 | 3/2 mm |
| 15–18 | 4/3 mm | 11–14 | 5/4 + hood/boots | < 11 | 5/4/3 full kit |

Cold air / wind shifts this one step up.

## Board
Small gutless waves → more volume (longboard, mid-length, fish).
Tier 1–2: always more volume than seems right.

## Plain-language glossary (tier 1–2 only)

Use these in-line on first mention, not as a footnote.

| Term | Say instead |
|---|---|
| offshore | wind from land to sea — holds the wave open |
| onshore | wind from sea to land — chops it up |
| glassy | no wind, smooth water |
| period | seconds between waves; longer = more power |
| swell | waves travelling in from out at sea |
| rip | current pulling out to sea; go sideways, not against it |
| beach/reef/point break | sand / rock / headland — sand is forgiving, rock is not |
| set | group of larger waves arriving together |
| duck dive | pushing the board under an incoming wave |

For hazards: always term + what to do about it.

## Data sources

**A. Open-Meteo via script (default)**
```
python scripts/forecast.py --days 2 \
    --spot "Cotillo:28.68,-14.01,270" \
    --spot "Corralejo:28.74,-13.83,45"
```
Format: `Name:lat,lon[,facing]`. All spots in one call. Use `--compact` for
a summary instead of hourly rows (preferred — saves tokens).
On a network denial, name the required domains once
(`marine-api.open-meteo.com` and `api.open-meteo.com`) and ask the user to allow
them through the host's network controls when supported; otherwise fall back to D.

**B. Tides** — search "tide times [place] [date]". Open-Meteo has none.

**C. Spot knowledge** — Surfline (descriptions, not numbers — paywall),
surf-forecast.com (orientation, swell window, tide), Windguru/Windfinder
(cross-check). Reuse or retain verified spot details only through a host-provided
memory feature when available and permitted.

**D. Fallback** — search `surf-forecast.com <spot> forecast`, fetch the
result. Max 2–3 spots. Wind in km/h, convert before comparing thresholds.

**Webcams** — prefer free (surf schools, Skyline Webcams). Surfline cams
need subscription. Retain the URL with other spot details when persistence is
available.

**Complex coasts** (peninsula, deep bay, island lee — Cape Town, west
Ireland, Canaries, Indonesia): model is systematically wrong, not uncertain.
Lead with per-spot forecast pages, model as rough check only.

Source: Open-Meteo CC BY 4.0. Credit with fetch time in answer.
