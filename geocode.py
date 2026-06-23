import json, time, urllib.request, urllib.parse, os, re, socket
socket.setdefaulttimeout(5)

# Town center coordinates for Aroostook County area
# Pre-known to avoid geocoding every single business
TOWN_CENTERS = {
    "Presque Isle": {"lat": 46.6813, "lng": -68.0159},
    "Caribou": {"lat": 46.8605, "lng": -68.0120},
    "Limestone": {"lat": 46.9117, "lng": -67.8267},
    "Fort Fairfield": {"lat": 46.7723, "lng": -67.8336},
    "Mars Hill": {"lat": 46.5126, "lng": -67.8664},
    "Mapleton": {"lat": 46.6817, "lng": -68.1603},
    "Washburn": {"lat": 46.7884, "lng": -68.1575},
    "Ashland": {"lat": 46.6314, "lng": -68.4050},
    "Houlton": {"lat": 46.1262, "lng": -67.8403},
    "Hodgdon": {"lat": 46.0531, "lng": -67.8672},
    "Littleton": {"lat": 46.2092, "lng": -67.9139},
    "Monticello": {"lat": 46.3078, "lng": -67.8433},
    "Linneus": {"lat": 46.0392, "lng": -67.9439},
    "Oakfield": {"lat": 45.9939, "lng": -68.1417},
    "Smyrna": {"lat": 46.0239, "lng": -68.1181},
    "New Limerick": {"lat": 46.1000, "lng": -67.9667},
    "Bridgewater": {"lat": 46.4231, "lng": -67.8444},
    "Island Falls": {"lat": 45.9953, "lng": -68.2717},
    "Dyer Brook": {"lat": 46.0828, "lng": -68.2111},
    "Millinocket": {"lat": 45.6573, "lng": -68.7098},
    "East Millinocket": {"lat": 45.6289, "lng": -68.5869},
    "Medway": {"lat": 45.6089, "lng": -68.5250},
    "Sherman": {"lat": 45.8700, "lng": -68.4097},
    "Patten": {"lat": 45.9956, "lng": -68.4453},
    "Mount Chase": {"lat": 46.0170, "lng": -68.5253},
    "Shin Pond": {"lat": 46.1500, "lng": -68.5500},
    "Lincoln": {"lat": 45.3623, "lng": -68.5050},
    "Howland": {"lat": 45.2386, "lng": -68.6631},
    "Enfield": {"lat": 45.2478, "lng": -68.6392},
    "Burlington": {"lat": 45.2167, "lng": -68.4333},
    "Chester": {"lat": 45.4000, "lng": -68.5167},
    "Winn": {"lat": 45.4833, "lng": -68.3667},
    "Mattawamkeag": {"lat": 45.5167, "lng": -68.3500},
    "Lee": {"lat": 45.3600, "lng": -68.2867},
    "Springfield": {"lat": 45.4000, "lng": -68.1333},
    "Greenbush": {"lat": 45.0833, "lng": -68.6500},
    "Lowell": {"lat": 45.2000, "lng": -68.4667},
}

# Known address-specific coordinates for businesses we can precisely locate
KNOWN_COORDS = {
    "hannaford_supermarket_pharmacy_caribou": {"lat": 46.8614, "lng": -68.0066},
    "hannaford_supermarket_pharmacy_millinocket": {"lat": 45.6519, "lng": -68.7077},
    "hannaford_supermarket_houlton": {"lat": 46.1325, "lng": -67.8477},
    "hannaford_supermarket_lincoln": {"lat": 45.3661, "lng": -68.5104},
    "walmart_supercenter_presque_isle": {"lat": 46.6788, "lng": -68.0136},
    "walmart_supercenter_lincoln": {"lat": 45.3583, "lng": -68.4755},
    "wal_mart_1974_houlton": {"lat": 46.1331, "lng": -67.8494},
    "northern_light_ar_gould_hospital_presque_isle": {"lat": 46.6836, "lng": -68.0011},
    "cary_medical_center_caribou": {"lat": 46.8575, "lng": -67.9986},
    "houlton_regional_hospital_houlton": {"lat": 46.1217, "lng": -67.8406},
    "millinocket_regional_hospital_millinocket": {"lat": 45.6564, "lng": -68.7050},
    "penobscot_valley_hospital_lincoln": {"lat": 45.3653, "lng": -68.5086},
    "presque_isle_international_airport_presque_isle": {"lat": 46.6889, "lng": -68.0458},
}

def geocode_via_nominatim(query):
    params = urllib.parse.urlencode({"q": query, "format": "json", "limit": 1})
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "CoffeeNewsAroostook/1.0")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data:
                return {"lat": float(data[0]["lat"]), "lng": float(data[0]["lon"])}
    except:
        pass
    return None

def make_key(name, town=""):
    raw = f"{name} {town}"
    key = re.sub(r'[^a-z0-9]', '_', raw.lower()).strip('_')
    return re.sub(r'_+', '_', key)

def main():
    json_path = "cleaned/all_businesses.json"
    coord_path = "coordinates.json"

    with open(json_path) as f:
        businesses = json.load(f)

    coords = {}
    if os.path.exists(coord_path):
        with open(coord_path) as f:
            coords = json.load(f)

    total = len(businesses)
    api_calls = 0

    for i, biz in enumerate(businesses):
        town_val = biz.get("town", "") or biz.get("city", "")
        key = make_key(biz["name"], town_val)
        if key in coords:
            continue

        # Check known coords
        if key in KNOWN_COORDS:
            coords[key] = KNOWN_COORDS[key]
            continue

        # Get town center fallback
        town = biz.get("town", "")
        city = biz.get("city", "")
        addr = biz.get("address", "")
        target_location = town or city

        # If we have a street address, try Nominatim
        result = None
        if addr.strip():
            q = f"{addr}, {city}, ME {biz.get('zip', '')}"
            result = geocode_via_nominatim(q)
            api_calls += 1
            if result:
                coords[key] = result
                if api_calls % 20 == 0:
                    print(f"  Geocoded {api_calls} addresses...")
                    with open(coord_path, 'w') as f:
                        json.dump(coords, f, indent=2)
                time.sleep(1.1)
                continue

        # Fallback to town center
        if target_location in TOWN_CENTERS:
            coords[key] = TOWN_CENTERS[target_location]
        elif city in TOWN_CENTERS:
            coords[key] = TOWN_CENTERS[city]
        else:
            # Unknown town - skip for now
            print(f"  WARNING: No coordinates for {biz['name']} ({town}/{city})")

        if (i + 1) % 200 == 0:
            print(f"  Processed {i+1}/{total} businesses ({len(coords)} with coords)...")
            with open(coord_path, 'w') as f:
                json.dump(coords, f, indent=2)

    # Final save
    with open(coord_path, 'w') as f:
        json.dump(coords, f, indent=2)

    no_coords = sum(1 for b in businesses if make_key(b["name"], b.get("town", "") or b.get("city", "")) not in coords)
    print(f"\nDone! {len(coords)}/{total} businesses have coordinates")
    print(f"  Nominatim API calls: {api_calls}")
    print(f"  Missing coords: {no_coords}")

if __name__ == "__main__":
    main()
