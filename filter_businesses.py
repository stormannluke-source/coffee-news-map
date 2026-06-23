import csv
import json
import re

# Businesses to remove (confirmed defunct, no phone found, or no address)
# These were identified through extensive research including chambers of commerce,
# web searches, Google Maps, and individual business website lookups.

REMOVE_NAMES = set()

# === NO PHONE FOUND (12) — could not find any phone number via any source ===
NO_PHONE = [
    ("Ashland General Store", "Ashland"),        # historic, no longer operating
    ("Mapleton Family Practice", "Mapleton"),     # no standalone practice exists
    ("Bangor Savings Bank", "Presque Isle"),     # no PI branch exists
    ("Lotus Lounge", "Presque Isle"),             # no published number
    ("Rossignol Performance & Fitness", "Presque Isle"),  # contact form only
    ("Starbucks", "Presque Isle"),                # inside Lowe's, no direct line
    ("Washburn General Store", "Washburn"),       # no business at this address
    ("Washburn Pharmacy", "Washburn"),            # no pharmacy at this address
    ("Rossignol Performance & Fitness", "Caribou"),       # contact form only
    ("Rossignol Performance & Fitness (Caribou)", "Caribou"), # duplicate entry
    ("Talk of the Town Salon", "Limestone"),      # permanently closed
    ("Mai's Take Out", "East Millinocket"),       # no published number
]

# === NO STREET ADDRESS (45) ===
NO_ADDRESS = [
    ("Ashland Fire Department", "Ashland"),
    ("Greenlaw Electric LLC", "Fort Fairfield"),
    ("Mapleton Family Practice", "Mapleton"),
    ("Mapleton Public Library", "Mapleton"),
    ("Dodo's Market", "Caribou"),
    ("DFAS Limestone", "Limestone"),
    ("Limestone Development Foundation", "Limestone"),
    ("Northern Maine Paving Inc.", "Limestone"),
    ("Talk of the Town Salon", "Limestone"),
    ("Bradbury Bros Potato Buyers", "Bridgewater"),
    ("D & B Fire Prevention", "Hodgdon"),
    ("Brooks Equipment Service & Sales", "Island Falls"),
    ("D&M Storage", "Island Falls"),
    ("Eastern Maine Electric Co-op (Island Falls)", "Island Falls"),
    ("GR Porter & Sons", "Island Falls"),
    ("Golden Ridge Farms", "Island Falls"),
    ("Hatch Custom Meat Cutting LLC", "Island Falls"),
    ("Hunt Law Offices", "Island Falls"),
    ("K&T Fire Equipment", "Island Falls"),
    ("Moulton's Small Engine Repair", "Island Falls"),
    ("Perrin Realty", "Island Falls"),
    ("Pleasant Pond Self Storage", "Island Falls"),
    ("RH Auto Sales", "Island Falls"),
    ("Rockwell Properties", "Island Falls"),
    ("Roymar Corporation (Self Storage)", "Island Falls"),
    ("Shear Energy Salon", "Island Falls"),
    ("Smith's Lawn Care Services LLC", "Island Falls"),
    ("Snapper's Plumbing", "Island Falls"),
    ("Tom York LLC", "Island Falls"),
    ("Unique Airbrushed Cakes", "Island Falls"),
    ("Va Jo Wa Maple", "Island Falls"),
    ("Vacationland Estates Resort", "Island Falls"),
    ("Valley Pro Services", "Island Falls"),
    ("Wilderness Pines Campground", "Monticello"),
    ("Keyes Asphalt Paving", "Smyrna"),
    ("Bangor Savings Bank", "East Millinocket"),
    ("Fingers & Toes Nail Care", "East Millinocket"),
    ("LA Casa de Fiesta Restaurant", "East Millinocket"),
    ("Katahdin General - Medway", "Medway"),
    ("Katahdin Valley Health Center - Patten", "Patten"),
    ("Katahdin Welding", "Patten"),
    ("Patten Lumbermen's Museum", "Patten"),
    ("Brenda's Restaurant", "Sherman"),
    ("Maine Lumber & Flooring Sales", "Sherman"),
    ("Tom's Garage", "Sherman"),
]

def normalize(s):
    if not s: return ""
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9\s]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def make_key(name, town):
    return f"{normalize(name)}|{normalize(town)}"

def main():
    # Build removal set
    remove_keys = set()
    for name, town in NO_PHONE:
        remove_keys.add(make_key(name, town))
    for name, town in NO_ADDRESS:
        remove_keys.add(make_key(name, town))

    print(f"Businesses to remove: {len(remove_keys)}")

    regions = ['presque_isle_area', 'caribou_limestone', 'houlton_region', 'millinocket_area', 'lincoln_area']
    total_removed = 0
    total_kept = 0

    for region in regions:
        fp = f'cleaned/{region}.csv'
        with open(fp, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = reader.fieldnames

        kept = []
        removed = 0
        for row in rows:
            key = make_key(row['Business Name'], row['Town'])
            if key in remove_keys:
                removed += 1
                total_removed += 1
            else:
                kept.append(row)
                total_kept += 1

        with open(fp, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(kept)

        print(f"  {region}: removed {removed}, kept {len(kept)}")

    print(f"\nTotal removed: {total_removed}")
    print(f"Total kept: {total_kept}")

if __name__ == '__main__':
    main()
