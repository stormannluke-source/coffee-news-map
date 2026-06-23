import json, urllib.request, urllib.parse, socket, time

socket.setdefaulttimeout(5)

TOWN_CENTERS = {
    'Ashland': (46.6292, -68.4085),
    'Bridgewater': (46.4230, -67.8430),
    'Burlington': (45.2083, -68.4467),
    'Caribou': (46.8606, -68.0120),
    'Chester': (45.4094, -68.5131),
    'Dyer Brook': (45.9234, -68.1840),
    'East Millinocket': (45.6292, -68.5754),
    'Enfield': (45.2479, -68.5685),
    'Fort Fairfield': (46.7713, -67.8344),
    'Greenbush': (45.0797, -68.5788),
    'Hodgdon': (46.0530, -67.8660),
    'Houlton': (46.1258, -67.8392),
    'Howland': (45.2385, -68.6600),
    'Island Falls': (45.9970, -68.2550),
    'Lee': (45.3456, -68.2945),
    'Limestone': (46.9080, -67.8250),
    'Lincoln': (45.3620, -68.5029),
    'Linneus': (46.0380, -67.9410),
    'Littleton': (46.2300, -67.9150),
    'Lowell': (45.1900, -68.4800),
    'Mapleton': (46.6805, -68.1585),
    'Mars Hill': (46.5140, -67.8674),
    'Mattawamkeag': (45.5161, -68.3535),
    'Medway': (45.6092, -68.5272),
    'Millinocket': (45.6570, -68.7105),
    'Monticello': (46.3040, -67.8410),
    'Mount Chase': (45.8720, -68.5020),
    'New Limerick': (46.1000, -67.9600),
    'Oakfield': (46.1013, -68.1555),
    'Patten': (46.0010, -68.4480),
    'Presque Isle': (46.6812, -68.0148),
    'Sherman': (45.8710, -68.3750),
    'Shin Pond': (46.0500, -68.4800),
    'Smyrna': (46.0500, -68.1000),
    'Springfield': (45.3950, -68.1400),
    'Washburn': (46.7875, -68.1578),
    'Winn': (45.4850, -68.3660),
}

def nominatim_query(query):
    url = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode({
        'q': query,
        'format': 'json',
        'limit': 1,
    })
    req = urllib.request.Request(url, headers={'User-Agent': 'CoffeeNews/1.0'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lng = float(data[0]['lon'])
                display = data[0].get('display_name', '')
                if 'Maine' in display or 'ME' in display or (43 <= lat <= 48 and -72 <= lng <= -66):
                    return (lat, lng, display[:80])
    except:
        pass
    return None

with open('cleaned/all_businesses.json') as f:
    biz = json.load(f)
with open('coordinates.json') as f:
    coords = json.load(f)

existing_keys = set(coords.keys())
all_keys = {b['key'] for b in biz}
missing = all_keys - existing_keys

print(f'Existing: {len(existing_keys)}, Total: {len(all_keys)}, Missing: {len(missing)}')

for b in biz:
    key = b['key']
    if key not in missing:
        continue
    
    name = b['name']
    addr = b.get('address', '').strip()
    town = b.get('town', '')
    city = b.get('city', '')
    
    # Build query
    if addr:
        query = f'{addr}, {city}, ME'
    else:
        query = f'{name}, {town}, ME'
    
    print(f'\nGeocoding: {name} ({key})')
    print(f'  Query: {query}')
    
    result = nominatim_query(query)
    if result:
        lat, lng, display = result
        print(f'  ✅ ({lat:.6f}, {lng:.6f}) — {display}')
        coords[key] = {'lat': lat, 'lng': lng}
    else:
        tc = TOWN_CENTERS.get(town)
        if tc:
            print(f'  ⚠️ Nominatim failed, using town center ({tc[0]:.4f}, {tc[1]:.4f})')
            coords[key] = {'lat': tc[0], 'lng': tc[1]}
        else:
            print(f'  ❌ No town center for {town}')
    
    time.sleep(1.1)

with open('coordinates.json', 'w') as f:
    json.dump(coords, f, indent=2)

print(f'\n✅ Geocoded {len(missing)} new entries')
