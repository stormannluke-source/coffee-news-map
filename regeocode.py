"""Re-geocode all 1122 businesses with addresstype precision classification.
Checkpoints every 50 entries. Resumable. Produces a report of imprecise entries."""

import json, time, socket, re, os
from urllib.request import urlopen, Request

CHECKPOINT = 'regeocode_checkpoint.json'
REPORT = 'regeocode_report.txt'
NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search?q={}&format=json&limit=1'
DELAY = 1.1  # slightly over 1s to be safe
TIMEOUT = 10

socket.setdefaulttimeout(TIMEOUT)

with open('cleaned/all_businesses.json') as f:
    businesses = json.load(f)

with open('coordinates.json') as f:
    current_coords = json.load(f)

# Load checkpoint if exists
start_from = 0
new_coords = {}
imprecise_log = []
precise_log = []
skipped_log = []

if os.path.exists(CHECKPOINT):
    with open(CHECKPOINT) as f:
        cp = json.load(f)
    start_from = cp.get('index', 0)
    new_coords = cp.get('coords', {})
    imprecise_log = cp.get('imprecise_log', [])
    precise_log = cp.get('precise_log', [])
    skipped_log = cp.get('skipped_log', [])
    print(f"Resumed from checkpoint: entry {start_from}/{len(businesses)}")
    print(f"  Precise so far: {len(precise_log)}, Imprecise so far: {len(imprecise_log)}, Skipped: {len(skipped_log)}")

def save_checkpoint(idx, coords, imp, prec, skip):
    cp = {
        'index': idx,
        'timestamp': time.time(),
        'coords': coords,
        'imprecise_log': imp,
        'precise_log': prec,
        'skipped_log': skip,
    }
    with open(CHECKPOINT, 'w') as f:
        json.dump(cp, f, indent=2)
    print(f"  [CHECKPOINT] Saved at entry {idx}/{len(businesses)}")

def classify_addresstype(result):
    """Determine if a Nominatim result is precise (building-level) or imprecise."""
    at = result.get('addresstype', '')
    cat = result.get('category', '')
    tp = result.get('type', '')
    cl = result.get('class', '')

    # These are precise — they point to actual features
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
                     'shelter', 'toilets', 'bench', 'waste_basket',
                     'retirement_home', 'studio', 'artwork', 'memorial',
                     'name', # matched by name
                     }

    if at in precise_types:
        return 'precise'

    # Road-level results
    if at in ('road', 'highway', 'street', 'secondary', 'primary', 'tertiary',
              'residential', 'unclassified', 'service', 'track', 'path',
              'footway', 'cycleway', 'bridleway'):
        return 'imprecise_road'

    # Town/city/village level
    if at in ('town', 'city', 'village', 'hamlet', 'locality', 'isolated_dwelling'):
        return 'imprecise_town'

    # Other fallback
    if cl == 'place':
        return 'imprecise_town'
    if cl == 'highway':
        return 'imprecise_road'

    return f'imprecise_other({at})'

def query_nominatim(query):
    url = NOMINATIM_URL.format(re.sub(r'\s+', '+', query.strip()))
    try:
        req = Request(url, headers={'User-Agent': 'CoffeeNewsAroostook/1.0 (research)'})
        resp = urlopen(req).read().decode()
        data = json.loads(resp)
        if data and len(data) > 0:
            return data[0]
        return None
    except Exception as e:
        print(f"  [WARN] Nominatim error for '{query[:60]}...': {e}")
        return None

def dist_meters(lat1, lng1, lat2, lng2):
    """Haversine distance in meters."""
    import math
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# Track stats
total = len(businesses)
print(f"\nStarting re-geocode audit of {total} businesses")
print(f"{'='*60}")

for i, biz in enumerate(businesses):
    if i < start_from:
        continue

    key = biz['key']
    name = biz['name']
    address = biz['address']
    town = biz['town']

    # Show progress with ETA
    if i % 10 == 0 and i > start_from:
        done = i
        remaining = total - done
        eta_secs = remaining * DELAY
        eta_min = int(eta_secs // 60)
        eta_sec = int(eta_secs % 60)
        pct = done * 100 / total
        print(f"  [{done}/{total} ({pct:.0f}%)] ETA: {eta_min}m{eta_sec}s | "
              f"Precise: {len(precise_log)} | Imprecise: {len(imprecise_log)} | Skipped: {len(skipped_log)}")

    # If no street address or town-only, skip (can't geocode)
    if not address or address == town or address == '':
        skipped_log.append({'key': key, 'name': name, 'reason': 'no_address'})
        # Keep existing coords if any
        if key in current_coords:
            new_coords[key] = current_coords[key]
        save_checkpoint(i, new_coords, imprecise_log, precise_log, skipped_log)
        time.sleep(0.1)  # small delay but not full rate limit
        continue

    # Build query: "Address, Town, ME"
    full_address = f"{address}, {town}, Maine"
    query = full_address

    result = query_nominatim(query)
    time.sleep(DELAY)

    if result is None:
        # Keep existing coords
        if key in current_coords:
            new_coords[key] = current_coords[key]
        skipped_log.append({'key': key, 'name': name, 'reason': 'nominatim_no_result', 'query': query[:80]})
        save_checkpoint(i, new_coords, imprecise_log, precise_log, skipped_log)
        continue

    lat = float(result['lat'])
    lng = float(result['lon'])
    classification = classify_addresstype(result)
    display_name = result.get('display_name', '')[:120]

    entry = {
        'key': key,
        'name': name,
        'address': address,
        'town': town,
        'lat': lat,
        'lng': lng,
        'classification': classification,
        'display_name': display_name,
        'query': query[:80],
    }

    if classification == 'precise':
        # Update coords
        new_coords[key] = {'lat': lat, 'lng': lng}
        precise_log.append(entry)

        # Check if this was previously imprecise (road/town center)
        if key in current_coords:
            old = current_coords[key]
            dist = dist_meters(old['lat'], old['lng'], lat, lng)
            if dist > 500:
                print(f"  ✓ {name} ({town}): improved by {dist:.0f}m")

    else:
        # Imprecise — keep existing coords if available
        if key in current_coords:
            new_coords[key] = current_coords[key]
        imprecise_log.append(entry)
        print(f"  ! {name} ({town}): {classification} — {display_name[:80]}")

    # Checkpoint every 50
    if (i + 1) % 50 == 0 or i == total - 1:
        save_checkpoint(i + 1, new_coords, imprecise_log, precise_log, skipped_log)

# Final save
save_checkpoint(total, new_coords, imprecise_log, precise_log, skipped_log)

print(f"\n{'='*60}")
print(f"Phase 1 Complete:")
print(f"  Total processed: {total}")
print(f"  Precise (building-level): {len(precise_log)}")
print(f"  Imprecise (road/town-level): {len(imprecise_log)}")
print(f"  Skipped (no address): {len(skipped_log)}")
print(f"  Coordinates saved: {len(new_coords)}")
PYEOF
