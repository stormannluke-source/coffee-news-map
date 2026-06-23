import csv
import json
import re
import os
from collections import defaultdict

OUT_DIR = "audit_output"
os.makedirs(OUT_DIR, exist_ok=True)

# Load all businesses
all_rows = []
for fname in ['presque_isle_area.csv', 'caribou_limestone.csv', 'houlton_region.csv', 'millinocket_area.csv', 'lincoln_area.csv']:
    with open(f'cleaned/{fname}') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['_file'] = fname
            all_rows.append(row)

print(f"Total businesses: {len(all_rows)}")

def slug(name):
    return re.sub(r'_+', '_', re.sub(r'[^a-z0-9]', '_', name.lower())).strip('_')

# ==================== 1. Town-only entries ====================
town_only = []
for r in all_rows:
    addr = r['Street Address'].strip()
    city = r['City'].strip()
    town = r['Town'].strip()
    if addr == city or addr == town or addr.lower() in [city.lower(), town.lower()]:
        town_only.append(r)

print(f"\n=== TOWN-ONLY ENTRIES: {len(town_only)} ===")
for r in town_only:
    print(f"  {r['_file']:35s} | {r['Business Name']:40s} | phone={r['Phone']}")

# Save to file
with open(f'{OUT_DIR}/town_only.json', 'w') as f:
    json.dump([{'file': r['_file'], 'name': r['Business Name'], 'phone': r['Phone'], 'town': r['Town'], 'category': r['Category']} for r in town_only], f, indent=2)

# ==================== 2. Phone conflicts ====================
by_phone = defaultdict(list)
for r in all_rows:
    phone = r['Phone'].strip()
    if phone:
        by_phone[phone].append(r)

phone_conflicts = {}
for phone, rows in sorted(by_phone.items()):
    if len(rows) > 1:
        names = set(r['Business Name'].strip() for r in rows)
        addresses = set(r['Street Address'].strip() for r in rows)
        towns = set(r['Town'].strip() for r in rows)
        # Filter: different name OR different address
        if len(names) > 1 or len(addresses) > 1:
            phone_conflicts[phone] = rows

print(f"\n=== PHONE CONFLICTS: {len(phone_conflicts)} groups ===")
for phone, rows in sorted(phone_conflicts.items()):
    print(f"\n  Phone: {phone}")
    for r in rows:
        print(f"    {r['_file']:35s} | {r['Business Name']:40s} | {r['Street Address']:30s} | {r['Town']}")

# Save to file
phone_conflict_groups = []
for phone, rows in sorted(phone_conflicts.items()):
    phone_conflict_groups.append({
        'phone': phone,
        'entries': [{'file': r['_file'], 'name': r['Business Name'], 'address': r['Street Address'], 'town': r['Town'], 'city': r['City'], 'category': r['Category']} for r in rows]
    })
with open(f'{OUT_DIR}/phone_conflicts.json', 'w') as f:
    json.dump(phone_conflict_groups, f, indent=2)

# ==================== 3. Duplicate detection ====================
# Group by (name slug, town) to find near-duplicates
by_slug_town = defaultdict(list)
for r in all_rows:
    key = (slug(r['Business Name']), r['Town'].strip().lower())
    by_slug_town[key].append(r)

potential_dupes = []
for key, rows in by_slug_town.items():
    if len(rows) > 1:
        names = set(r['Business Name'].strip() for r in rows)
        addrs = set(r['Street Address'].strip() for r in rows)
        if len(names) > 1 or (len(names) == 1 and len(addrs) == 1):
            # Same name + same address = clear duplicate (regardless of phone)
            # Different name + same address + same phone = likely duplicate
            phones = set(r['Phone'].strip() for r in rows if r['Phone'].strip())
            if len(addrs) == 1 and (len(phones) <= 1 or list(phones)[0] == ''):
                potential_dupes.append(rows)

print(f"\n=== POTENTIAL DUPLICATES: {len(potential_dupes)} groups ===")
for rows in potential_dupes:
    print(f"  Same: {' vs '.join(r['Business Name'].strip() for r in rows)}")
    print(f"  Address: {rows[0]['Street Address']}, {rows[0]['Town']}")
    print(f"  Phones: {', '.join(r['Phone'].strip() for r in rows)}")
    print(f"  Files: {', '.join(r['_file'] for r in rows)}")

# ==================== 4. No phone entries ====================
no_phone = [r for r in all_rows if not r['Phone'].strip()]
print(f"\n=== NO PHONE: {len(no_phone)} ===")
for r in no_phone:
    print(f"  {r['_file']:35s} | {r['Business Name']:40s} | {r['Street Address']:30s} | {r['Town']}")

# ==================== 5. No website entries ====================
no_web = [r for r in all_rows if not r['Website'].strip()]
print(f"\n=== NO WEBSITE: {len(no_web)} ===")

# ==================== 6. Street name summary ====================
streets_by_town = defaultdict(set)
for r in all_rows:
    addr = r['Street Address'].strip()
    city = r['City'].strip()
    town = r['Town'].strip()
    if addr and addr != city and addr != town:
        key = slug(r['Business Name'])
        streets_by_town[town].add(addr)

print(f"\n=== STREET NAME SAMPLES PER TOWN ===")
for town in sorted(streets_by_town):
    streets = sorted(streets_by_town[town])
    print(f"  {town:25s} ({len(streets)} unique addresses)")

# Save all suspicious entries to a batch research file
research_batch = []

# Add phone conflict entries
for phone, rows in sorted(phone_conflicts.items()):
    for r in rows:
        research_batch.append({
            'type': 'phone_conflict',
            'group': phone,
            'name': r['Business Name'].strip(),
            'address': r['Street Address'].strip(),
            'phone': phone,
            'town': r['Town'].strip(),
            'file': r['_file'],
            'category': r['Category'].strip(),
        })

# Add town-only entries
for r in town_only:
    research_batch.append({
        'type': 'town_only',
        'name': r['Business Name'].strip(),
        'address': '',
        'phone': r['Phone'].strip(),
        'town': r['Town'].strip(),
        'file': r['_file'],
        'category': r['Category'].strip(),
    })

# Add no-phone entries
for r in no_phone:
    research_batch.append({
        'type': 'no_phone',
        'name': r['Business Name'].strip(),
        'address': r['Street Address'].strip(),
        'phone': '',
        'town': r['Town'].strip(),
        'file': r['_file'],
        'category': r['Category'].strip(),
    })

with open(f'{OUT_DIR}/research_batch.json', 'w') as f:
    json.dump(research_batch, f, indent=2)

print(f"\n=== SUMMARY ===")
print(f"Total entries: {len(all_rows)}")
print(f"Town-only: {len(town_only)}")
print(f"Phone conflict groups: {len(phone_conflicts)}")
print(f"Potential duplicate groups: {len(potential_dupes)}")
print(f"No phone: {len(no_phone)}")
print(f"Research batch items: {len(research_batch)}")
print(f"\nOutput files in {OUT_DIR}/")
