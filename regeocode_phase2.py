"""Phase 2: Retry imprecise entries with business name + town query.
Checkpoints every 50 entries. Resumable."""

import json, time, socket, re, os
from urllib.request import urlopen, Request

CHECKPOINT = 'regeocode_phase2_checkpoint.json'
DELAY = 1.1
socket.setdefaulttimeout(10)

with open('regeocode_checkpoint.json') as f:
    cp = json.load(f)

imprecise_entries = cp['imprecise_log']
total = len(imprecise_entries)
print(f"Phase 2: Retrying {total} imprecise entries with name+town query")

with open('coordinates.json') as f:
    coords = json.load(f)

with open('cleaned/all_businesses.json') as f:
    businesses = json.load(f)

biz_by_key = {b['key']: b for b in businesses}

# Load checkpoint
start_from = 0
phase2_results = []
improved = 0
still_imprecise = []

if os.path.exists(CHECKPOINT):
    with open(CHECKPOINT) as f:
        cp2 = json.load(f)
    start_from = cp2.get('index', 0)
    phase2_results = cp2.get('results', [])
    improved = cp2.get('improved', 0)
    still_imprecise = cp2.get('still_imprecise', [])
    print(f"  Resumed from checkpoint: {start_from}/{total}")
    print(f"  Improved so far: {improved}")

def classify_addresstype(result):
    at = result.get('addresstype', '')
    cl = result.get('class', '')
    precise_types = {'building', 'amenity', 'shop', 'office', 'place_of_worship',
                     'pub', 'cafe', 'restaurant', 'fast_food', 'hotel', 'motel',
                     'museum', 'library', 'school', 'university', 'college',
                     'hospital', 'clinic', 'dentist', 'pharmacy', 'bank',
                     'post_office', 'fire_station', 'police', 'townhall',
                     'cinema', 'theatre', 'community_centre', 'community_center',
                     'fuel', 'convenience', 'supermarket', 'mall', 'department_store',
                     'car_dealership', 'car_repair', 'car_wash', 'parking',
                     'hardware', 'doityourself', 'garden_centre', 'garden_center',
                     'stationery', 'laundry', 'dry_cleaning', 'beauty', 'hairdresser',
                     'barber', 'sports_centre', 'sports_center', 'fitness_centre',
                     'fitness_center', 'social_facility', 'nursing_home',
                     'childcare', 'kindergarten', 'place_of_worship',
                     'grave_yard', 'cemetery', 'attraction', 'viewpoint',
                     'camp_site', 'caravan_site', 'picnic_site', 'playground',
                     'shelter', 'toilets', 'bench',
                     'retirement_home', 'studio', 'artwork', 'memorial'}
    if at in precise_types:
        return 'precise'
    if at in ('road', 'highway', 'street', 'secondary', 'primary', 'tertiary',
              'residential', 'unclassified', 'service', 'track', 'path',
              'footway', 'cycleway', 'bridleway'):
        return 'imprecise_road'
    if at in ('town', 'city', 'village', 'hamlet', 'locality', 'isolated_dwelling'):
        return 'imprecise_town'
    if cl == 'place':
        return 'imprecise_town'
    if cl == 'highway':
        return 'imprecise_road'
    return f'imprecise_other({at})'

for idx, entry in enumerate(imprecise_entries):
    if idx < start_from:
        continue
    
    key = entry['key']
    name = entry['name']
    
    if idx % 25 == 0 and idx > start_from:
        done = idx
        remaining = total - done
        eta = remaining * DELAY
        pct = done * 100 / total
        print(f"  [{done}/{total} ({pct:.0f}%)] ETA: {eta/60:.0f}m | Improved: {improved} | Still imprecise: {len(still_imprecise)}")
    
    # Build name+town query, stripping "LLC", "Inc", etc for better matching
    clean_name = re.sub(r'\b(LLC|Inc|Inc\.|Co|Co\.|Corp|Corp\.|Ltd|P\.A\.|P A)\b', '', name).strip()
    query = f"{clean_name}, {entry.get('town', '')}, Maine"
    # Remove parenthetical suffixes like "(Caribou)" 
    query = re.sub(r'\s*\([^)]*\)\s*', ' ', query)
    
    url = f'https://nominatim.openstreetmap.org/search?q={re.sub(r"\s+", "+", query.strip())}&format=json&limit=3'
    
    try:
        req = Request(url, headers={'User-Agent': 'CoffeeNewsAroostook/1.0 (phase2)'})
        resp = urlopen(req).read().decode()
        data = json.loads(resp)
    except Exception as e:
        still_imprecise.append(key)
        time.sleep(DELAY)
        continue
    
    best_result = None
    best_class = None
    
    if data:
        for r in data:
            cls = classify_addresstype(r)
            if cls == 'precise':
                best_result = r
                best_class = cls
                break
            if best_result is None:
                best_result = r
                best_class = cls
        
        if best_class == 'precise':
            lat = float(best_result['lat'])
            lng = float(best_result['lon'])
            coords[key] = {'lat': lat, 'lng': lng}
            improved += 1
            phase2_results.append({'key': key, 'name': name, 'improved': True})
            if improved % 10 == 0:
                print(f"    ✓ #{improved}: {name[:40]}")
        else:
            still_imprecise.append(key)
            phase2_results.append({'key': key, 'name': name, 'improved': False})
    else:
        still_imprecise.append(key)
        phase2_results.append({'key': key, 'name': name, 'improved': False})
    
    # Checkpoint every 50
    if (idx + 1) % 50 == 0 or idx == total - 1:
        cp2 = {
            'index': idx + 1,
            'timestamp': time.time(),
            'results': phase2_results,
            'improved': improved,
            'still_imprecise': still_imprecise,
        }
        with open(CHECKPOINT, 'w') as f:
            json.dump(cp2, f, indent=2)
    
    time.sleep(DELAY)

# Final save
cp2 = {
    'index': total,
    'timestamp': time.time(),
    'results': phase2_results,
    'improved': improved,
    'still_imprecise': still_imprecise,
}
with open(CHECKPOINT, 'w') as f:
    json.dump(cp2, f, indent=2)

with open('coordinates.json', 'w') as f:
    json.dump(coords, f, indent=2)

print(f"\n✅ Phase 2 Complete!")
print(f"  Retried: {total}")
print(f"  Improved (now precise): {improved}")
print(f"  Still imprecise: {len(still_imprecise)}")
print(f"  coordinates.json updated")
PYEOF
