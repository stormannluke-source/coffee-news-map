import json, urllib.request, urllib.parse, urllib.error, socket, time

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
                # Verify it's in Maine
                if 'Maine' in display or 'ME' in display or (43 <= lat <= 48 and -72 <= lng <= -66):
                    return (lat, lng, display[:80])
                return None
    except Exception:
        pass
    return None

with open('coordinates.json') as f:
    coords = json.load(f)

entries = [
    ('united_construction_forestry_united_ag_turf_houlton', '106 North St, Houlton, ME', 'Houlton'),
    ('wood_works_rocks_of_maine_linneus', '612 Drews Mills Rd, Linneus, ME', 'Linneus'),
    ('83_north_bar_grill_billiards_medway', '2149 Medway Rd, Medway, ME', 'Medway'),
    ('noah_s_ark_food_ice_cream_medway', '289 Pattagumpus Rd, Medway, ME', 'Medway'),
    ('two_rivers_canoe_tackle_medway', '2323 Medway Rd, Medway, ME', 'Medway'),
    ('hotel_terrace_restaurant_millinocket', '52 Medway Rd, Millinocket, ME', 'Millinocket'),
    ('russ_barber_styling_millinocket', '99 Penobscot Ave, Millinocket, ME', 'Millinocket'),
    ('ashley_cunningham_co_furniture_burlington', '344 Long Ridge Rd, Burlington, ME', 'Burlington'),
    ('high_performance_hair_tanning_lincoln', '40 Main St, Lincoln, ME', 'Lincoln'),
    ('marden_s_surplus_salvage_lincoln', '28 Main St, Lincoln, ME', 'Lincoln'),
    ('true_value_lincoln', '51 Main St, Lincoln, ME', 'Lincoln'),
    ('lee_barbershop_styling_salon_springfield', '985 Main St, Springfield, ME', 'Springfield'),
    ('st_thomas_episcopal_church_winn', '14 Main St, Winn, ME', 'Winn'),
]

for key, query, town in entries:
    old = coords.get(key, 'N/A')
    print(f'\n=== {key} ===')
    print(f'  Old: {old}')
    print(f'  Query: {query}')
    
    result = nominatim_query(query)
    if result:
        lat, lng, display = result
        print(f'  Nominatim result: ({lat:.6f}, {lng:.6f}) — {display}')
        coords[key] = {'lat': lat, 'lng': lng}
    else:
        print(f'  Nominatim FAILED — falling back to town center')
        tc = TOWN_CENTERS.get(town)
        if tc:
            coords[key] = {'lat': tc[0], 'lng': tc[1]}
            print(f'  Set to town center: ({tc[0]:.6f}, {tc[1]:.6f})')
    
    time.sleep(1.1)  # Rate limit

with open('coordinates.json', 'w') as f:
    json.dump(coords, f, indent=2)

print('\n✅ All 13 entries processed')
