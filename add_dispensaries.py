import csv, os

# New dispensaries to add, organized by CSV file
# Format: (Business Name, Street Address, City, State, Zip, Phone, Email, Website, Category, Town, SuitableForAds)

LINCOLN_NEW = [
    ("Blazin' Trailz", "90 River Rd", "Lincoln", "ME", "04457", "(207) 403-9151", "", "https://blazintrailz.com", "Cannabis Dispensary", "Lincoln", "Yes"),
    ("Experience Cannabis", "100 River Rd", "Lincoln", "ME", "04457", "(207) 403-9204", "", "", "Cannabis Dispensary", "Lincoln", "Yes"),
    ("American Marijuana Cultivators", "100 River Rd", "Lincoln", "ME", "04457", "(207) 403-9247", "", "", "Cannabis Dispensary", "Lincoln", "Yes"),
    ("Fire Pharms", "293 W Broadway", "Lincoln", "ME", "04457", "(207) 449-6080", "", "", "Cannabis Dispensary", "Lincoln", "Yes"),
    ("Brothers Cannabis", "222 W Broadway Unit 2", "Lincoln", "ME", "04457", "(207) 403-9095", "", "https://www.broscannabis.com", "Cannabis Dispensary", "Lincoln", "Yes"),
    ("Hazy Moose Craft Cannabis", "22 Main St", "Howland", "ME", "04448", "(207) 732-7072", "", "https://hazymoose.com", "Cannabis Dispensary", "Howland", "Yes"),
]

PI_NEW = [
    ("Richardson Remedies", "719 Main St", "Presque Isle", "ME", "04769", "(207) 760-7202", "", "https://www.richardsonremedies.com", "Cannabis Dispensary", "Presque Isle", "Yes"),
    ("Full Bloom Cannabis", "483 Main St", "Presque Isle", "ME", "04769", "(207) 760-7586", "", "https://www.fullbloomcannabis.com", "Cannabis Dispensary", "Presque Isle", "Yes"),
    ("Cloud 9", "28 Houlton Rd", "Presque Isle", "ME", "04740", "(207) 540-1043", "", "", "Cannabis Dispensary", "Presque Isle", "Yes"),
    ("Northern Maine Flower", "540 Main St", "Presque Isle", "ME", "04769", "(207) 760-7015", "", "", "Cannabis Dispensary", "Presque Isle", "Yes"),
    ("Star City Wellness", "694 Main St", "Presque Isle", "ME", "04769", "(207) 540-1045", "", "http://starcitywellnesspi.com", "Cannabis Dispensary", "Presque Isle", "Yes"),
    ("Richardson Remedies", "9 Bog Rd", "Caribou", "ME", "04736", "(207) 493-1181", "", "https://www.richardsonremedies.com", "Cannabis Dispensary", "Caribou", "Yes"),
    ("Safe Alternatives", "1137 Presque Isle Rd", "Caribou", "ME", "04736", "(207) 492-2651", "", "https://safealternativesmaine.com", "Cannabis Dispensary", "Caribou", "Yes"),
]

HOULTON_NEW = [
    ("Vargas Farm", "28 Airport Dr", "Houlton", "ME", "04730", "(207) 405-5256", "", "", "Cannabis Dispensary", "Houlton", "Yes"),
    ("Lifted Cannabis", "32 Access Rd", "Houlton", "ME", "04730", "(207) 631-4818", "", "https://www.liftedmaine.com", "Cannabis Dispensary", "Houlton", "Yes"),
    ("Family Roots Medical Marijuana", "66 Industrial Dr", "Houlton", "ME", "04730", "(207) 538-7336", "", "", "Cannabis Dispensary", "Houlton", "Yes"),
    ("Northwoods Farms", "79 Bangor St", "Houlton", "ME", "04730", "(207) 558-0755", "", "", "Cannabis Dispensary", "Houlton", "Yes"),
]

MILLINOCKET_NEW = [
    ("Magic City Med Shop", "166 Central St", "Millinocket", "ME", "04462", "(207) 261-1004", "", "", "Cannabis Dispensary", "Millinocket", "Yes"),
    ("Outer Limits", "200 Iron Bridge Rd", "Millinocket", "ME", "04462", "(207) 723-6332", "", "", "Cannabis Dispensary", "Millinocket", "Yes"),
]

CSV_FIELDS = ["Business Name", "Street Address", "City", "State", "Zip", "Phone", "Email", "Website", "Category", "Town", "SuitableForAds"]

def add_to_csv(filepath, new_rows):
    """Append rows to CSV if they don't already exist (by Business Name + Town)."""
    existing_names = set()
    if os.path.exists(filepath):
        with open(filepath, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_names.add((row['Business Name'].strip().lower(), row['Town'].strip().lower()))
    
    added = 0
    skipped = 0
    with open(filepath, 'a', newline='') as f:
        writer = csv.writer(f)
        for row in new_rows:
            key = (row[0].strip().lower(), row[9].strip().lower())
            if key in existing_names:
                skipped += 1
                continue
            writer.writerow(row)
            existing_names.add(key)
            added += 1
    return added, skipped

files = [
    ('cleaned/lincoln_area.csv', LINCOLN_NEW),
    ('cleaned/presque_isle_area.csv', PI_NEW),
    ('cleaned/houlton_region.csv', HOULTON_NEW),
    ('cleaned/millinocket_area.csv', MILLINOCKET_NEW),
]

total_added = 0
total_skipped = 0
for filepath, rows in files:
    added, skipped = add_to_csv(filepath, rows)
    total_added += added
    total_skipped += skipped
    print(f'{filepath}: added {added}, skipped {skipped} (already existed)')

print(f'\nTotal added: {total_added}, Total skipped: {total_skipped}')
