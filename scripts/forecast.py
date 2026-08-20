#!/usr/bin/env python3
"""
Pulls swell, wind and weather from Open-Meteo and prints a compact table.

Handles several spots in ONE pair of requests, so five candidates cost two
HTTP calls instead of ten. Far cheaper in tokens than fetching forecast pages.

Requires network access to api.open-meteo.com and marine-api.open-meteo.com.
On 403 or another network restriction, see references/guide.md.

Several spots (preferred):
  python scripts/forecast.py --days 2 \\
      --spot "El Cotillo:28.68,-14.01,270" \\
      --spot "Corralejo:28.74,-13.83,45"

Single spot:
  python scripts/forecast.py --lat 28.68 --lon -14.01 --name "El Cotillo" \\
      --facing 270

Spot format is  Name:lat,lon[,facing]  where facing is the direction the beach
looks out to sea in degrees (0=N, 90=E, 180=S, 270=W). Facing is what lets the
script call the wind offshore or onshore, which is the single biggest factor in
the rating — leave it out and you lose that column.
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request

MARINE = "https://marine-api.open-meteo.com/v1/marine"
WEATHER = "https://api.open-meteo.com/v1/forecast"

MARINE_VARS = ("wave_height,wave_period,wave_direction,swell_wave_height,"
               "swell_wave_period,swell_wave_direction,sea_surface_temperature")
WEATHER_VARS = ("wind_speed_10m,wind_direction_10m,wind_gusts_10m,"
                "temperature_2m,precipitation,cloud_cover")


def get(url, params):
    q = urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(f"{url}?{q}", timeout=30) as r:
            data = json.load(r)
    except Exception as e:
        print(f"ERROR fetching {url}: {e}", file=sys.stderr)
        print("If this is 403/Host not in allowlist: network access is not "
              "enabled. Switch to the fallback sources in "
              "references/guide.md.", file=sys.stderr)
        sys.exit(2)
    # Open-Meteo returns a bare object for one location, a list for several.
    return data if isinstance(data, list) else [data]


def compass(deg):
    pts = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
           "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    return pts[int((deg % 360) / 22.5 + 0.5) % 16]


def wind_state(wind_from_deg, facing_deg):
    """Wind is given as the direction it comes FROM. Offshore means it blows
    off the land, i.e. from the opposite of the beach's facing.
    Example: beach faces W (270), wind from E (90) -> offshore."""
    if facing_deg is None:
        return "?"
    diff = abs((wind_from_deg - (facing_deg + 180) + 180) % 360 - 180)
    if diff <= 45:
        return "offshore"
    if diff <= 90:
        return "cross-off"
    if diff <= 135:
        return "cross-on"
    return "onshore"


def parse_spot(s):
    """'Name:lat,lon[,facing]' -> dict"""
    if ":" not in s:
        sys.exit(f"Bad --spot value {s!r}. Expected Name:lat,lon[,facing]")
    name, coords = s.rsplit(":", 1)
    parts = [p.strip() for p in coords.split(",")]
    if len(parts) not in (2, 3):
        sys.exit(f"Bad coordinates in {s!r}. Expected lat,lon[,facing]")
    try:
        return {"name": name.strip(), "lat": float(parts[0]),
                "lon": float(parts[1]),
                "facing": float(parts[2]) if len(parts) == 3 else None}
    except ValueError:
        sys.exit(f"Non-numeric coordinates in {s!r}")


def render(spot, m, w, hours, compact=False):
    mh, wh = m.get("hourly", {}), w.get("hourly", {})
    if not mh.get("time"):
        print(f"# {spot['name']}: no wave data returned. Coordinates may sit "
              f"inland — move them into the water.\n")
        return

    sst = [x for x in mh.get("sea_surface_temperature", []) if x is not None]
    print(f"# {spot['name']}  ({spot['lat']}, {spot['lon']})")
    if sst:
        print(f"# Water: {sum(sst) / len(sst):.1f}C", end="")
    if spot["facing"] is not None:
        print(f"  Faces: {compass(spot['facing'])} ({spot['facing']:.0f}°)")
    else:
        print("  No facing given")

    # Collect rows
    rows = []
    for i, t in enumerate(mh["time"]):
        if not (hours[0] <= int(t[11:13]) <= hours[1]):
            continue
        try:
            sw_h, sw_p, sw_d = (mh["swell_wave_height"][i],
                                mh["swell_wave_period"][i],
                                mh["swell_wave_direction"][i])
            wd, ws, gu = (wh["wind_direction_10m"][i], wh["wind_speed_10m"][i],
                          wh["wind_gusts_10m"][i])
            tp, pr = wh["temperature_2m"][i], wh["precipitation"][i]
        except (IndexError, KeyError):
            continue
        if sw_h is None or ws is None:
            continue
        ws_state = wind_state(wd, spot["facing"])
        rows.append({"t": t, "sw_h": sw_h, "sw_p": sw_p, "sw_d": sw_d,
                      "wd": wd, "ws": ws, "gu": gu, "tp": tp, "pr": pr,
                      "ws_state": ws_state})

    if not rows:
        print("# No data in the requested hour range.\n")
        return

    if compact:
        render_compact(rows, spot)
    else:
        print(f"\n{'Time':<17}{'Swell':<18}{'Wind':<26}{'Air':<7}{'Rain'}")
        for r in rows:
            swell = f"{r['sw_h']:.1f}m {r['sw_p']:.0f}s {compass(r['sw_d'])}"
            wind = (f"{r['ws']:.0f}kn ({r['gu']:.0f}) {compass(r['wd'])} "
                    f"{r['ws_state']}")
            print(f"{r['t'].replace('T', ' '):<17}{swell:<18}{wind:<26}"
                  f"{r['tp']:.0f}C{'':<3}{r['pr']:.1f}mm")
    print()


def render_compact(rows, spot):
    """One block per day: best window, peak swell, wind range."""
    from itertools import groupby
    days = groupby(rows, key=lambda r: r["t"][:10])
    for date, day_rows in days:
        dr = list(day_rows)
        # Best window: hours with offshore or cross-off and lowest wind
        good = [r for r in dr if r["ws_state"] in ("offshore", "cross-off")]
        if not good:
            good = [r for r in dr if r["ws_state"] == "cross-on"]
        if not good:
            good = dr  # all onshore — still report

        best_start = good[0]["t"][11:16]
        best_end = good[-1]["t"][11:16]
        pk = max(dr, key=lambda r: r["sw_h"])
        wn_lo = min(dr, key=lambda r: r["ws"])
        wn_hi = max(dr, key=lambda r: r["ws"])
        rain = sum(r["pr"] for r in dr)

        print(f"  {date}  swell {pk['sw_h']:.1f}m {pk['sw_p']:.0f}s "
              f"{compass(pk['sw_d'])}  wind {wn_lo['ws']:.0f}–"
              f"{wn_hi['ws']:.0f}kn {compass(wn_lo['wd'])}"
              f"→{compass(wn_hi['wd'])} "
              f"({good[0]['ws_state']}→{good[-1]['ws_state']})  "
              f"air {dr[0]['tp']:.0f}–{dr[-1]['tp']:.0f}C"
              f"{'  rain ' + f'{rain:.0f}mm' if rain > 0.5 else ''}")
        if best_start != best_end:
            print(f"    best window: {best_start}–{best_end} "
                  f"({good[0]['ws_state']}, "
                  f"{good[0]['ws']:.0f}–{good[-1]['ws']:.0f}kn)")
        else:
            print(f"    best hour: {best_start} ({good[0]['ws_state']}, "
                  f"{good[0]['ws']:.0f}kn)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--spot", action="append", default=[],
                   help="Name:lat,lon[,facing] - repeat for several spots")
    p.add_argument("--lat", type=float)
    p.add_argument("--lon", type=float)
    p.add_argument("--name", default="Spot")
    p.add_argument("--facing", type=float, default=None,
                   help="direction the beach faces out to sea, in degrees")
    p.add_argument("--days", type=int, default=3)
    p.add_argument("--hours", type=int, nargs=2, default=[6, 20],
                   metavar=("FROM", "TO"), help="only print daylight hours")
    p.add_argument("--compact", action="store_true",
                   help="summary mode: best window + daily extremes instead "
                        "of hourly rows (preferred — much fewer tokens)")
    a = p.parse_args()

    spots = [parse_spot(s) for s in a.spot]
    if a.lat is not None and a.lon is not None:
        spots.append({"name": a.name, "lat": a.lat, "lon": a.lon,
                      "facing": a.facing})
    if not spots:
        sys.exit("Give at least one --spot or a --lat/--lon pair.")

    base = {"latitude": ",".join(str(s["lat"]) for s in spots),
            "longitude": ",".join(str(s["lon"]) for s in spots),
            "timezone": "auto", "forecast_days": a.days}
    marine = get(MARINE, {**base, "hourly": MARINE_VARS})
    weather = get(WEATHER, {**base, "hourly": WEATHER_VARS,
                            "wind_speed_unit": "kn"})

    if len(marine) != len(spots) or len(weather) != len(spots):
        print(f"WARNING: asked for {len(spots)} spots, got {len(marine)} wave "
              f"and {len(weather)} weather results. Output may be misaligned — "
              f"re-run spots individually before trusting it.", file=sys.stderr)

    print("# Wind in knots. 1 kn = 1.85 km/h.\n")
    for spot, m, w in zip(spots, marine, weather):
        render(spot, m, w, a.hours, compact=a.compact)

    print("# Source: Open-Meteo (CC BY 4.0). Open-water model values, "
          "not face height on the peak.")


if __name__ == "__main__":
    main()
