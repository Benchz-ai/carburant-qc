#!/usr/bin/env python3
"""
Télécharge les prix de carburant du jour depuis regieessencequebec.ca
et produit docs/stations.json, utilisé par la carte interactive (PWA).

Ce script est conçu pour tourner quotidiennement via GitHub Actions,
mais peut aussi être exécuté manuellement : python3 fetch_stations.py
"""
import gzip
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone

SOURCE_URL = "https://regieessencequebec.ca/stations.geojson.gz"
OUTPUT_PATH = "docs/stations.json"

FUEL_KEY_MAP = {
    "Régulier": "reg",
    "Regulier": "reg",
    "Super": "sup",
    "Diesel": "dies",
}


def fetch_source(url: str) -> dict:
    """Télécharge le GeoJSON. Robuste aux deux cas possibles : le serveur
    renvoie soit le JSON déjà décompressé (Content-Encoding géré en amont),
    soit les octets gzip bruts (urllib ne décompresse pas automatiquement,
    contrairement à des libs comme requests)."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; carburant-app-bot/1.0)",
            "Accept-Encoding": "gzip",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()

    # Signature gzip : 1f 8b -> on décompresse manuellement.
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)

    return json.loads(raw.decode("utf-8"))


def parse_price(price_str):
    if not price_str:
        return None
    m = re.match(r"^([\d.]+)", str(price_str))
    return float(m.group(1)) if m else None


def transform(source: dict) -> dict:
    features = source.get("features", [])
    stations = []

    for feat in features:
        props = feat.get("properties", {})
        geom = feat.get("geometry", {})
        coords = geom.get("coordinates")
        if not coords or len(coords) != 2:
            continue
        lng, lat = coords

        prices = {"reg": None, "sup": None, "dies": None}
        for p in props.get("Prices", []):
            key = FUEL_KEY_MAP.get(p.get("GasType"))
            if key and p.get("IsAvailable", True):
                prices[key] = parse_price(p.get("Price"))

        stations.append({
            "n": props.get("Name"),
            "b": props.get("brand"),
            "a": props.get("Address"),
            "r": props.get("Region"),
            "cp": props.get("PostalCode"),
            "lat": lat,
            "lng": lng,
            "reg": prices["reg"],
            "sup": prices["sup"],
            "dies": prices["dies"],
        })

    return {
        "generated_at": source.get("metadata", {}).get("generated_at"),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "total": len(stations),
        "stations": stations,
    }


def main():
    try:
        source = fetch_source(SOURCE_URL)
    except Exception as exc:
        print(f"Erreur lors du téléchargement : {exc}", file=sys.stderr)
        sys.exit(1)

    result = transform(source)

    if result["total"] < 1000:
        # Garde-fou : si la source renvoie anormalement peu de stations,
        # on n'écrase pas les bonnes données existantes.
        print(
            f"Nombre de stations suspect ({result['total']}), abandon.",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, separators=(",", ":"))

    print(f"OK : {result['total']} stations écrites dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
