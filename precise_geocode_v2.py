import json, urllib.request, urllib.parse, re, time, socket
socket.setdefaulttimeout(5)

# Load data
with open('regeocode_report.txt') as f:
    report = f.read()
with open('cleaned/all_businesses.json') as f:
    biz = json.load(f)
with open('coordinates.json') as f:
    coords = json.load(f)

# Town centers for validation
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

# Build biz lookup
name_to_biz = {b['name'].lower().strip(): b for b in biz}
name_to_key = {b['name'].lower().strip(): b['key'] for b in biz}

# Parse imprecise entries from report
entries = []
for line in report.split('\n'):
    m = re.match(r'\s+(.+?)\s+\|\s+(.+?)\s+\|\s+current=\(([\d.-]+),\s*([\d.-]+)\)', line)
    if m:
        entries.append({
            'name': m.group(1).strip(),
            'address': m.group(2).strip(),
            'lat': float(m.group(3)),
            'lng': float(m.group(4)),
        })

def census_geocode(address):
    url = 'https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress?' + urllib.parse.urlencode({
        'address': address,
        'benchmark': 'Public_AR_Current',
        'vintage': 'Current_Current',
        'format': 'json',
    })
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            matches = data.get('result', {}).get('addressMatches', [])
            if matches:
                m = matches[0]
                # Get state from matched address components
                coords_out = m['coordinates']
                addr_parts = m.get('addressComponents', {})
                state = addr_parts.get('state', '')
                return (coords_out['y'], coords_out['x'], state, m.get('matchedAddress', ''))
    except:
        pass
    return None

improved = 0
failed = 0
for i, entry in enumerate(entries):
    name = entry['name']
    addr_raw = entry['address']
    
    # Find business to get ZIP, town
    b = name_to_biz.get(name.lower().strip())
    if not b:
        failed += 1
        continue
    
    town = b.get('town', '')
    zip_code = b.get('zip', '')
    city = b.get('city', '')
    
    # Clean address
    addr_clean = re.sub(r'\s*\(.*?\)\s*$', '', addr_raw).strip()
    
    # Skip PO boxes
    if 'PO Box' in addr_clean or 'P.O.' in addr_clean:
        failed += 1
        continue
    
    # Build query with ZIP if available
    if zip_code:
        census_addr = f'{addr_clean}, ME {zip_code}'
    else:
        census_addr = f'{addr_clean}, ME'
    
    result = census_geocode(census_addr)
    if result:
        new_lat, new_lng, state, matched = result
        
        # Verify: must be in Maine
        if state != 'ME' and state != '23':
            failed += 1
            continue
        
        # Verify: must be within reasonable distance of town center
        tc = TC.get(town)
        if tc:
            dlat = new_lat - tc[0]
            dlng = new_lng - tc[1]
            # Accept within 30km of town center
            dist_km = (dlat**2 + dlng**2)**0.5 * 111
            if dist_km > 30:
                # Try without ZIP (some ZIPs are wrong)
                if zip_code:
                    result2 = census_geocode(f'{addr_clean}, ME')
                    if result2:
                        new_lat2, new_lng2, state2, matched2 = result2
                        if state2 in ('ME', '23'):
                            dlat2 = new_lat2 - tc[0]
                            dlng2 = new_lng2 - tc[1]
                            if (dlat2**2 + dlng2**2)**0.5 * 111 <= 30:
                                new_lat, new_lng = new_lat2, new_lng2
                                matched = matched2
                            else:
                                failed += 1
                                time.sleep(0.2)
                                continue
                        else:
                            failed += 1
                            time.sleep(0.2)
                            continue
                    else:
                        failed += 1
                        time.sleep(0.2)
                        continue
                else:
                    failed += 1
                    time.sleep(0.2)
                    continue
        
        key = name_to_key.get(name.lower().strip())
        if key and key in coords:
            old_lat, old_lng = coords[key]['lat'], coords[key]['lng']
            if abs(new_lat - old_lat) > 0.0001 or abs(new_lng - old_lng) > 0.0001:
                coords[key] = {'lat': new_lat, 'lng': new_lng}
                improved += 1
    else:
        failed += 1
    
    if i % 50 == 0 and i > 0:
        print(f'  Progress: {i}/{len(entries)}, improved: {improved}, failed: {failed}')
    time.sleep(0.15)

with open('coordinates.json', 'w') as f:
    json.dump(coords, f, indent=2)

print(f'\n✅ Complete: {improved} improved, {failed} failed/skipped')
print(f'Remaining imprecise: {len(entries) - improved - failed}')
