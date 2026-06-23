import csv
import json
import re

def make_key(name, town):
    raw = f"{name} {town}"
    key = re.sub(r'[^a-z0-9]', '_', raw.lower()).strip('_')
    return re.sub(r'_+', '_', key)

REGION_MAP = {
    "Presque Isle Area": ["Presque Isle", "Caribou", "Limestone", "Fort Fairfield", "Mars Hill", "Mapleton", "Washburn", "Ashland"],
    "Houlton Region": ["Houlton", "Hodgdon", "Littleton", "Monticello", "Linneus", "Oakfield", "Smyrna", "New Limerick", "Bridgewater", "Island Falls", "Dyer Brook"],
    "Millinocket Area": ["Millinocket", "East Millinocket", "Medway", "Sherman", "Patten", "Mount Chase", "Shin Pond"],
    "Lincoln Area": ["Lincoln", "Howland", "Enfield", "Burlington", "Chester", "Winn", "Mattawamkeag", "Lee", "Springfield", "Greenbush", "Lowell"],
}

def get_region(town):
    for region, towns in REGION_MAP.items():
        if town in towns:
            return region
    return "Other"

def main():
    all_rows = []
    for region in ['presque_isle_area', 'houlton_region', 'millinocket_area', 'lincoln_area']:
        fp = f'cleaned/{region}.csv'
        with open(fp, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['Region'] = get_region(row.get('Town', '').strip())
                all_rows.append(row)

    master = []
    for r in all_rows:
        entry = {
            "key": make_key(r.get("Business Name", "").strip(), r.get("Town", "").strip()),
            "name": r.get("Business Name", "").strip(),
            "address": r.get("Street Address", "").strip(),
            "city": r.get("City", "").strip(),
            "state": r.get("State", "").strip(),
            "zip": r.get("Zip", "").strip(),
            "phone": r.get("Phone", "").strip(),
            "email": r.get("Email", "").strip(),
            "website": r.get("Website", "").strip(),
            "category": r.get("Category", "").strip(),
            "town": r.get("Town", "").strip(),
            "region": r.get("Region", ""),
            "suitableForAds": r.get("SuitableForAds", "").strip(),
        }
        master.append(entry)

    with open('cleaned/all_businesses.json', 'w', encoding='utf-8') as f:
        json.dump(master, f, indent=2, ensure_ascii=False)

    with_phone = sum(1 for b in master if b['phone'])
    with_email = sum(1 for b in master if b['email'])
    with_addr = sum(1 for b in master if b['address'])
    with_region = sum(1 for b in master if b['region'])
    print(f'JSON regenerated: {len(master)} entries')
    print(f'  With phone: {with_phone}')
    print(f'  With email: {with_email}')
    print(f'  With address: {with_addr}')
    print(f'  With region: {with_region}')
    regions = set(b['region'] for b in master if b['region'])
    print(f'  Regions: {sorted(regions)}')

if __name__ == '__main__':
    main()
