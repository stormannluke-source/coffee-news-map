import json, os, urllib.request, urllib.parse, time, socket
socket.setdefaulttimeout(5)

def load_env():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env()
API_KEY = os.environ.get('GOOGLE_API_KEY')
if not API_KEY or API_KEY == 'your_api_key_here':
    print('ERROR: Set GOOGLE_API_KEY in .env file')
    print('  Create a restricted API key in Google Cloud Console:')
    print('  1. APIs & Services > Library > Enable Geocoding API')
    print('  2. APIs & Services > Credentials > Create API Key')
    print('  3. Restrict to Geocoding API only, IP 143.244.47.72')
    print('  4. Paste key into .env: GOOGLE_API_KEY=your_key')
    exit(1)

with open('cleaned/all_businesses.json') as f:
    biz = json.load(f)
with open('coordinates.json') as f:
    coords = json.load(f)

with open('regeocode_report.txt') as f:
    report = f.read()

def google_geocode(query):
    url = 'https://maps.googleapis.com/maps/api/geocode/json?' + urllib.parse.urlencode({
        'address': query,
        'key': API_KEY,
    })
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        if data['status'] == 'OK' and data['results']:
            r = data['results'][0]
            loc = r['geometry']['location']
            loc_type = r['geometry'].get('location_type', 'APPROXIMATE')
            formatted = r.get('formatted_address', '')
            return {
                'lat': loc['lat'],
                'lng': loc['lng'],
                'location_type': loc_type,
                'formatted_address': formatted,
            }
    except:
        pass
    return None

TC = {
    'Ashland': (46.6292, -68.4085), 'Bridgewater': (46.4230, -67.8430),
    'Burlington': (45.2083, -68.4467), 'Caribou': (46.8606, -68.0120),
    'Chester': (45.4094, -68.5131), 'Dyer Brook': (45.9234, -68.1840),
    'East Millinocket': (45.6292, -68.5754), 'Enfield': (45.2479, -68.5685),
    'Fort Fairfield': (46.7713, -67.8344), 'Greenbush': (45.0797, -68.5788),
    'Hodgdon': (46.0530, -67.8660), 'Houlton': (46.1258, -67.8392),
    'Howland': (45.2385, -68.6600), 'Island Falls': (45.9970, -68.2550),
    'Lee': (45.3456, -68.2945), 'Limestone': (46.9080, -67.8250),
    'Lincoln': (45.3620, -68.5029), 'Linneus': (46.0380, -67.9410),
    'Littleton': (46.2300, -67.9150), 'Lowell': (45.1900, -68.4800),
    'Mapleton': (46.6805, -68.1585), 'Mars Hill': (46.5140, -67.8674),
    'Mattawamkeag': (45.5161, -68.3535), 'Medway': (45.6092, -68.5272),
    'Millinocket': (45.6570, -68.7105), 'Monticello': (46.3040, -67.8410),
    'Mount Chase': (45.8720, -68.5020), 'New Limerick': (46.1000, -67.9600),
    'Oakfield': (46.1013, -68.1555), 'Patten': (46.0010, -68.4480),
    'Presque Isle': (46.6812, -68.0148), 'Sherman': (45.8710, -68.3750),
    'Shin Pond': (46.0500, -68.4800), 'Smyrna': (46.0500, -68.1000),
    'Springfield': (45.3950, -68.1400), 'Washburn': (46.7875, -68.1578),
    'Winn': (45.4850, -68.3660),
}

cost_est = len([b for b in biz if b.get('address', '').strip()])
print(f'Script: google_geocode.py')
print(f'Total businesses: {len(biz)}')
print(f'With addresses (will query): {cost_est}')
print(f'Estimated cost: ${cost_est * 0.005:.2f} (1141 x $0.005 = $5.70 max)')
print(f'Using key: {API_KEY[:8]}...{API_KEY[-4:]}')
print(f'Rate: 50 req/s — no delay needed')
print()

rooftop_count = 0
other_count = 0
improved = 0
failed = 0
skipped = 0

for i, b in enumerate(biz):
    name = b['name']
    key = b['key']
    addr = b.get('address', '').strip()
    city = b.get('city', '').strip()
    state = b.get('state', '').strip()
    zip_code = b.get('zip', '').strip()
    town = b.get('town', '')

    if not addr:
        skipped += 1
        continue

    query = f'{addr}, {city}, {state} {zip_code}'
    result = google_geocode(query)

    if not result:
        failed += 1
        if i % 10 == 0:
            print(f'  [{i+1}/{cost_est}] FAIL: {name}')
        continue

    loc_type = result['location_type']
    new_lat = result['lat']
    new_lng = result['lng']

    tc = TC.get(town)
    if tc:
        dlat = new_lat - tc[0]
        dlng = new_lng - tc[1]
        dist_km = (dlat**2 + dlng**2)**0.5 * 111
        if dist_km > 30:
            failed += 1
            if i % 10 == 0:
                print(f'  [{i+1}/{cost_est}] FAR: {name} ({dist_km:.0f}km from {town})')
            continue

    if loc_type == 'ROOFTOP':
        rooftop_count += 1
    else:
        other_count += 1

    old = coords.get(key)
    if old:
        old_lat = old.get('lat')
        old_lng = old.get('lng')
        moved = abs(new_lat - old_lat) > 0.00005 or abs(new_lng - old_lng) > 0.00005
        if moved:
            coords[key] = {'lat': new_lat, 'lng': new_lng, 'google_location_type': loc_type}
            improved += 1
    else:
        coords[key] = {'lat': new_lat, 'lng': new_lng, 'google_location_type': loc_type}
        improved += 1

    if (i + 1) % 100 == 0:
        print(f'Progress: {i+1}/{cost_est} | ROOFTOP: {rooftop_count} | other: {other_count} | improved: {improved} | failed: {failed}')

with open('coordinates.json', 'w') as f:
    json.dump(coords, f, indent=2)

print(f'\n=== RESULTS ===')
print(f'Total queries: {cost_est}')
print(f'ROOFTOP (building-level): {rooftop_count}')
print(f'Other (road/town-level): {other_count}')
print(f'Coordinates improved/added: {improved}')
print(f'Failed/skipped: {failed + skipped}')
print(f'Total coordinates file: {len(coords)}')
print(f'\nEstimated cost: ${cost_est * 0.005:.2f}')
print(f'Done!')
