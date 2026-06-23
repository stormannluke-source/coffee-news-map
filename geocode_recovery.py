"""Recover geocode precision by re-geocoding town-center businesses.
Handles Nominatim timeouts with socket-level timeout and progress saves."""
import json, time, urllib.request, urllib.parse, ssl, re, os, socket

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "CoffeeNewsAroostook/1.0"
REQUEST_TIMEOUT = 4.0  # seconds per request
RATE_DELAY = 1.0       # seconds between requests
SAVE_EVERY = 50

ssl_ctx = ssl.create_default_context()
socket.setdefaulttimeout(REQUEST_TIMEOUT + 1)

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

def make_key(name, town=""):
    raw = f"{name} {town}"
    key = re.sub(r'[^a-z0-9]', '_', raw.lower()).strip('_')
    return re.sub(r'_+', '_', key)

def is_town_center(coord):
    for tc in TOWN_CENTERS.values():
        if abs(coord['lat'] - tc['lat']) < 0.0001 and abs(coord['lng'] - tc['lng']) < 0.0001:
            return True
    return False

def geocode(query):
    params = urllib.parse.urlencode({"q": query, "format": "json", "limit": 1})
    url = f"{NOMINATIM_URL}?{params}"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    try:
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=REQUEST_TIMEOUT) as resp:
            data = json.loads(resp.read().decode())
            if data:
                return {"lat": float(data[0]["lat"]), "lng": float(data[0]["lon"])}
    except:
        pass
    return None

def get_town_center(town, city):
    return TOWN_CENTERS.get(town) or TOWN_CENTERS.get(city)

with open('cleaned/all_businesses.json') as f:
    businesses = json.load(f)

coord_path = "coordinates.json"
coords = {}
if os.path.exists(coord_path):
    with open(coord_path) as f:
        coords = json.load(f)

print(f"Existing coords: {len(coords)}", flush=True)

api_calls = 0
improved = 0
skipped_no_addr = 0
already_precise = 0
retry_hits = 0

for i, biz in enumerate(businesses):
    name = biz["name"]
    addr = biz.get("address", "").strip()
    town_val = biz.get("town", "") or biz.get("city", "")
    city = biz.get("city", "")
    zip_code = biz.get("zip", "")
    key = make_key(name, town_val)

    # Already has coords?
    if key not in coords:
        # Fill with town center
        tc = get_town_center(town_val, city)
        if tc:
            coords[key] = tc
        continue

    c = coords.get(key)
    if not c:
        tc = get_town_center(town_val, city)
        if tc:
            coords[key] = tc
        continue

    # Skip if already precise
    if not is_town_center(c):
        already_precise += 1
        continue

    # Skip if no street address
    if not addr:
        skipped_no_addr += 1
        continue

    # Try Nominatim with full query
    q = f"{addr}, {city}, ME {zip_code}"
    result = geocode(q)
    api_calls += 1

    if not result:
        time.sleep(RATE_DELAY * 0.5)
        # Retry with simpler query (street + town only)
        simple_q = f"{addr.split(',')[0].strip()}, {city}, ME"
        result = geocode(simple_q)
        api_calls += 1
        if result:
            retry_hits += 1

    if result:
        coords[key] = result
        improved += 1
        status = "✓"
    else:
        status = "✗"

    if (i + 1) % 200 == 0 or improved % SAVE_EVERY == 0:
        with open(coord_path, 'w') as f:
            json.dump(coords, f, indent=2)
        tc_now = sum(1 for v in coords.values() if is_town_center(v))
        precise_now = len(coords) - tc_now
        print(f"  [{i+1}/{len(businesses)}] API calls: {api_calls}, precise: {precise_now}, TC: {tc_now}, improved this run: {improved}", flush=True)

    time.sleep(RATE_DELAY)

# Final save
with open(coord_path, 'w') as f:
    json.dump(coords, f, indent=2)

tc_final = sum(1 for v in coords.values() if is_town_center(v))
precise_final = len(coords) - tc_final

print(f"\n=== DONE ===", flush=True)
print(f"Total: {len(coords)}", flush=True)
print(f"Precise: {precise_final}", flush=True)
print(f"Town center: {tc_final}", flush=True)
print(f"API calls: {api_calls}", flush=True)
print(f"Improved this run: {improved}", flush=True)
print(f"Retry hits: {retry_hits}", flush=True)
print(f"Skipped (no address): {skipped_no_addr}", flush=True)
print(f"Already precise: {already_precise}", flush=True)
