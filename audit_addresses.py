import csv, json, re, time, urllib.request, urllib.parse, os, socket
socket.setdefaulttimeout(5)

def normalize_key(name, town):
    n = re.sub(r'[^a-z0-9\s]', '', name.lower().strip())
    n = re.sub(r'\s+', ' ', n).strip()
    t = re.sub(r'[^a-z0-9\s]', '', town.lower().strip())
    t = re.sub(r'\s+', ' ', t).strip()
    return f"{n}|{t}"

def geocode(query):
    params = urllib.parse.urlencode({"q": query, "format": "json", "limit": 1})
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "CoffeeNewsAroostook/1.0")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data:
                return data[0]
    except:
        pass
    return None

def strip_unit(addr):
    addr = re.sub(r'\s+(Ste|Suite|Unit|Apt|Rm|Room)\s*#?\s*\w*$', '', addr, flags=re.I)
    addr = re.sub(r'\s+[A-Z]$', '', addr)  # "21 Main St A" -> "21 Main St"
    return addr.strip()

def extract_street_name(addr):
    # Remove house number to get street name
    m = re.match(r'^[\d\-\/]+\s+(.*)', addr)
    if m:
        return m.group(1).strip()
    return addr

def load_all_businesses():
    all_biz = []
    for region in ['presque_isle_area', 'caribou_limestone', 'houlton_region', 'millinocket_area', 'lincoln_area']:
        fp = f'cleaned/{region}.csv'
        with open(fp, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                row['region'] = region
                all_biz.append(row)
    return all_biz

def main():
    all_biz = load_all_businesses()
    
    # Load existing coordinates to know which had successful Nominatim
    with open('coordinates.json') as f:
        coords = json.load(f)
    
    # Town centers for reference
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
    
    center_by_coords = {}
    for town, (clat, clng) in TOWN_CENTERS.items():
        center_by_coords[(round(clat, 4), round(clng, 4))] = town
    
    # Categorize each business
    results = []
    previously_flagged = []
    town_center_fallbacks = []
    precise_ok = []
    
    for biz in all_biz:
        name = biz['Business Name'].strip()
        city = biz.get('City', '').strip()
        town = biz.get('Town', '').strip()
        addr = biz.get('Street Address', '').strip()
        
        key = normalize_key(name, town)
        coord = coords.get(key)
        
        entry = {
            'name': name,
            'address': addr,
            'city': city,
            'town': town,
            'region': biz.get('region', ''),
        }
        
        if not addr or addr == city:
            entry['status'] = 'town_only'
            entry['note'] = 'No street address'
            town_center_fallbacks.append(entry)
            continue
        
        if not coord:
            entry['status'] = 'no_coords'
            entry['note'] = 'No coordinates in coordinates.json'
            previously_flagged.append(entry)
            continue
        
        rlat, rlng = round(coord['lat'], 4), round(coord['lng'], 4)
        is_tc = (rlat, rlng) in center_by_coords
        
        if is_tc:
            entry['status'] = 'town_center_fallback'
            entry['note'] = 'Nominatim failed to geocode address'
            town_center_fallbacks.append(entry)
        else:
            entry['status'] = 'precise_ok'
            entry['note'] = f'Nominatim geocoded to {coord["lat"]:.4f},{coord["lng"]:.4f}'
            precise_ok.append(entry)
    
    print(f"Total businesses: {len(all_biz)}")
    print(f"Precise Nominatim OK: {len(precise_ok)}")
    print(f"Town center fallbacks: {len(town_center_fallbacks)}")
    town_only_count = sum(1 for r in town_center_fallbacks if r.get('status') == 'town_only')
    print(f"Town-only/no address: {town_only_count}")
    
    # Now re-check the town center fallbacks with better Nominatim queries
    print(f"\n--- Checking {len(town_center_fallbacks)} town-center fallbacks ---")
    
    found = []
    still_missing = []
    
    for i, entry in enumerate(town_center_fallbacks):
        name = entry['name']
        addr = entry['address']
        city = entry['city']
        
        if entry.get('status') == 'town_only':
            still_missing.append(entry)
            continue
        
        print(f"[{i+1}/{len(town_center_fallbacks)}] {name} | {addr}")
        
        # Try 1: Full address
        q1 = f"{addr}, {city}, ME"
        r1 = geocode(q1)
        if r1 and 'ME' in r1.get('display_name', ''):
            entry['nom_found'] = True
            entry['nom_query'] = q1
            entry['nom_result'] = r1['display_name']
            print(f"  OK: {r1['display_name'][:80]}")
            found.append(entry)
            time.sleep(1.1)
            continue
        
        # Try 2: Strip unit numbers
        addr2 = strip_unit(addr)
        q2 = f"{addr2}, {city}, ME"
        r2 = geocode(q2)
        if r2 and 'ME' in r2.get('display_name', ''):
            entry['nom_found'] = True
            entry['nom_query'] = q2
            entry['nom_result'] = r2['display_name']
            entry['note'] += f' (found via stripped address: {addr2})'
            print(f"  OK (stripped): {r2['display_name'][:80]}")
            found.append(entry)
            time.sleep(1.1)
            continue
        
        # Try 3: Just street name
        street = extract_street_name(addr)
        q3 = f"{street}, {city}, ME"
        r3 = geocode(q3)
        if r3 and 'ME' in r3.get('display_name', ''):
            entry['nom_found'] = True
            entry['nom_query'] = q3
            entry['nom_result'] = r3['display_name']
            entry['note'] += f' (found via street name: {street})'
            print(f"  OK (street): {r3['display_name'][:80]}")
            found.append(entry)
            time.sleep(1.1)
            continue
        
        # Try 4: Without "ME" (some OSM entries don't have state tagged)
        q4 = f"{addr}, {city}"
        r4 = geocode(q4)
        if r4:
            entry['nom_found'] = True
            entry['nom_query'] = q4
            entry['nom_result'] = r4['display_name']
            entry['note'] += f' (found without state)'
            print(f"  OK (no state): {r4['display_name'][:80]}")
            found.append(entry)
            time.sleep(1.1)
            continue
        
        entry['nom_found'] = False
        entry['nom_query'] = q1
        entry['nom_result'] = ''
        still_missing.append(entry)
        print(f"  NOT FOUND")
        time.sleep(1.1)
    
    print(f"\n--- Results ---")
    print(f"Addresses found with retry: {len(found)}/{len(town_center_fallbacks)}")
    print(f"Still missing (truly unverifiable via OSM): {len(still_missing)}")
    
    if still_missing:
        print(f"\n=== STILL MISSING === (manual review needed)")
        for e in still_missing:
            print(f"  {e['name']:40s} | {e['address']:40s} | {e['city']:20s}")
    else:
        print(f"\nAll town-center fallbacks resolved!")
    
    # Save full results
    output = {
        'precise_ok': len(precise_ok),
        'found_with_retry': len(found),
        'still_missing': len(still_missing),
        'still_missing_details': [{'name': e['name'], 'address': e['address'], 'city': e['city'], 'town': e['town']} for e in still_missing],
    }
    with open('address_audit_phase1.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to address_audit_phase1.json")

if __name__ == '__main__':
    main()
