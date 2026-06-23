"""Targeted re-geocode of town-center entries.
Safe strategies: suite-stripped, street-only. NO state-wide queries (causes cross-state misplacement)."""
import json, time, urllib.request, urllib.parse, ssl, re, os, socket

from math import radians, cos, sin, asin, sqrt

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "CoffeeNewsAroostook/1.0"
REQUEST_TIMEOUT = 4.0
RATE_DELAY = 1.0
SAVE_EVERY = 5

def haversine(lat1, lon1, lat2, lon2):
    R = 3959  # miles
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * asin(sqrt(a))

ssl_ctx = ssl.create_default_context()
socket.setdefaulttimeout(REQUEST_TIMEOUT + 1)

TOWN_CENTERS = {
    "Presque Isle": (46.6813, -68.0159), "Caribou": (46.8605, -68.0120),
    "Limestone": (46.9117, -67.8267), "Fort Fairfield": (46.7723, -67.8336),
    "Mars Hill": (46.5126, -67.8664), "Mapleton": (46.6817, -68.1603),
    "Washburn": (46.7884, -68.1575), "Ashland": (46.6314, -68.4050),
    "Houlton": (46.1262, -67.8403), "Hodgdon": (46.0531, -67.8672),
    "Littleton": (46.2092, -67.9139), "Monticello": (46.3078, -67.8433),
    "Linneus": (46.0392, -67.9439), "Oakfield": (45.9939, -68.1417),
    "Smyrna": (46.0239, -68.1181), "New Limerick": (46.1000, -67.9667),
    "Bridgewater": (46.4231, -67.8444), "Island Falls": (45.9953, -68.2717),
    "Dyer Brook": (46.0828, -68.2111), "Millinocket": (45.6573, -68.7098),
    "East Millinocket": (45.6289, -68.5869), "Medway": (45.6089, -68.5250),
    "Sherman": (45.8700, -68.4097), "Patten": (45.9956, -68.4453),
    "Mount Chase": (46.0170, -68.5253), "Shin Pond": (46.1500, -68.5500),
    "Lincoln": (45.3623, -68.5050), "Howland": (45.2386, -68.6631),
    "Enfield": (45.2478, -68.6392), "Burlington": (45.2167, -68.4333),
    "Chester": (45.4000, -68.5167), "Winn": (45.4833, -68.3667),
    "Mattawamkeag": (45.5167, -68.3500), "Lee": (45.3600, -68.2867),
    "Springfield": (45.4000, -68.1333), "Greenbush": (45.0833, -68.6500),
    "Lowell": (45.2000, -68.4667),
}

def make_key(name, town=""):
    raw = f"{name} {town}"
    key = re.sub(r'[^a-z0-9]', '_', raw.lower()).strip('_')
    return re.sub(r'_+', '_', key)

def is_tc(coord):
    for clat, clng in TOWN_CENTERS.values():
        if abs(coord['lat'] - clat) < 0.0001 and abs(coord['lng'] - clng) < 0.0001:
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

def strip_suite(addr):
    return re.sub(r'\s*(?:Suite|Ste|Unit|#)\s*\d+.*$', '', addr, flags=re.IGNORECASE).strip().rstrip(',').strip()

with open('cleaned/all_businesses.json') as f:
    businesses = json.load(f)

coord_path = "coordinates.json"
with open(coord_path) as f:
    coords = json.load(f)

# Find town-center entries with addresses
entries = []
for biz in businesses:
    key = biz['key']
    c = coords.get(key)
    if not c or not is_tc(c):
        continue
    addr = biz.get('address', '').strip()
    if not addr:
        continue
    entries.append({
        'key': key,
        'name': biz['name'],
        'address': addr,
        'city': biz.get('city', ''),
        'zip': biz.get('zip', ''),
        'town': biz.get('town', '') or biz.get('city', ''),
    })

total = len(entries)
print(f"Town-center entries with addresses: {total}", flush=True)

api_calls = 0
improved = 0
by_strategy = {'suite': 0, 'street': 0, 'name': 0, 'failed': 0}

for i, e in enumerate(entries):
    addr = e['address']
    city = e['city']
    town = e['town']
    zipc = e['zip']
    name = e['name']
    key = e['key']

    # Strategy 1: Full address with suite/unit stripped
    clean = strip_suite(addr)
    q = f"{clean}, {city}, ME {zipc}"
    result = geocode(q)
    api_calls += 1
    strat = 'suite'

    # Strategy 2: Street name + town only (no house number)
    if not result:
        street_only = re.sub(r'^\d+\s*', '', clean).strip()
        q2 = f"{street_only}, {city}, ME"
        result = geocode(q2)
        api_calls += 1
        strat = 'street'

    # Strategy 3: Business name + town (Nominatim may know the business)
    if not result:
        name_clean = re.sub(r'[^a-z0-9\s]', '', name, flags=re.IGNORECASE).strip()
        q3 = f"{name_clean}, {city}, ME"
        result = geocode(q3)
        api_calls += 1
        strat = 'name'
        # Reject if result is >20 miles from expected town center
        if result:
            tc = TOWN_CENTERS.get(e.get('town', e.get('city', '')))
            if tc:
                d = haversine(result['lat'], result['lng'], tc[0], tc[1])
                if d > 20:
                    result = None
                    strat = 'name_rejected'

    if result:
        coords[key] = result
        improved += 1
        by_strategy[strat] = by_strategy.get(strat, 0) + 1
        print(f"  ✓ {name[:35]:35s} | {strat:6s} | ({result['lat']:.4f}, {result['lng']:.4f})", flush=True)
    else:
        by_strategy['failed'] += 1
        print(f"  ✗ {name[:35]:35s} | stays at town center", flush=True)

    if improved % SAVE_EVERY == 0:
        with open(coord_path, 'w') as f:
            json.dump(coords, f, indent=2)
        print(f"  [saved at {improved} improved / {i+1}/{total} processed]", flush=True)

    time.sleep(RATE_DELAY)

with open(coord_path, 'w') as f:
    json.dump(coords, f, indent=2)

tc_final = sum(1 for v in coords.values() if is_tc(v))
precise_final = len(coords) - tc_final

print(f"\n=== DONE ===", flush=True)
print(f"Total: {len(coords)}, Precise: {precise_final}, Town center: {tc_final}", flush=True)
print(f"API calls: {api_calls}", flush=True)
print(f"Improved this run: {improved}", flush=True)
print(f"By strategy: {by_strategy}", flush=True)
