import json
import csv
import os

# =============================================
# MANUALLY CURATED CORRECTIONS FROM RESEARCH
# =============================================

# Corrections: (csv_file, match_name, match_town, field, new_value)
CORRECTIONS = [
    # === PHONE CORRECTIONS ===
    ("caribou_limestone.csv", "Limestone Community School", "Limestone", "Phone", "(207) 325-4742"),
    ("caribou_limestone.csv", "Limestone Town Office", "Limestone", "Phone", "(207) 325-4704"),
    ("caribou_limestone.csv", "SFE Manufacturing", "Limestone", "Phone", "(207) 540-0668"),
    ("caribou_limestone.csv", "SFE Manufacturing Inc.", "Limestone", "Phone", "(207) 540-0668"),
    ("caribou_limestone.csv", "The Cubby Thriftstore", "Caribou", "Phone", "(207) 496-0600"),
    ("caribou_limestone.csv", "Aroostook National Wildlife Refuge", "Limestone", "Phone", "(207) 454-7161"),
    ("presque_isle_area.csv", "Katahdin Trust Company", "Ashland", "Phone", "(207) 435-6461"),
    ("houlton_region.csv", "Ivey's Motor Lodge", "Houlton", "Phone", "(207) 532-4206"),
    ("houlton_region.csv", "Sloat's Machining & Fabrication", "Houlton", "Phone", "(207) 532-4594"),
    ("houlton_region.csv", "County Tractor of Houlton", "Houlton", "Phone", "(207) 538-3155"),
    ("houlton_region.csv", "Louisiana Pacific", "Houlton", "Phone", "(207) 532-7361"),
    ("houlton_region.csv", "United Construction & Forestry / United Ag & Turf", "Houlton", "Phone", "(207) 532-6517"),
    ("millinocket_area.csv", "Circle K / Medway Irving Big Stop", "Medway", "Phone", "(207) 746-3411"),
    ("houlton_region.csv", "Mt. Timoney Cycle Center", "Smyrna", "Phone", "(207) 757-7198"),
    ("houlton_region.csv", "Crown of Maine Taxidermy", "Hodgdon", "Phone", "(207) 521-1534"),

    # === ADDRESS CORRECTIONS ===
    ("presque_isle_area.csv", "Parkhurst Siding Pub", "Presque Isle", "Street Address", "35 Parkhurst Siding Rd"),
    ("presque_isle_area.csv", "Pizza Box", "Presque Isle", "Street Address", "527 Main St Ste 1"),
    ("presque_isle_area.csv", "The Maple Pig", "Presque Isle", "Street Address", "710 Main St"),
    ("houlton_region.csv", "Ivey's Motor Lodge", "Houlton", "Street Address", "241 North St"),
    ("houlton_region.csv", "Sloat's Machining & Fabrication", "Houlton", "Street Address", "170 Bangor St"),
    ("houlton_region.csv", "County Tractor of Houlton", "Houlton", "Street Address", "708 North St"),
    ("houlton_region.csv", "Louisiana Pacific", "Houlton", "Street Address", "240 Station Rd"),
    ("houlton_region.csv", "United Construction & Forestry / United Ag & Turf", "Houlton", "Street Address", "106 North St"),
    ("presque_isle_area.csv", "Caldwell's Auto", "Fort Fairfield", "Street Address", "133 Presque Isle St"),
    ("presque_isle_area.csv", "Ashland Post Office", "Ashland", "Street Address", "14 Sheridan Rd"),
    ("presque_isle_area.csv", "Ashland Public Library", "Ashland", "Street Address", "57 Exchange St"),
    ("caribou_limestone.csv", "Aroostook National Wildlife Refuge", "Limestone", "Street Address", "97 Refuge Rd"),
    # On the Run address typo fix
    ("caribou_limestone.csv", "On the Run", "Caribou", "Street Address", "117 Bennett Dr"),

    # === NAME CORRECTIONS ===
    ("presque_isle_area.csv", "Ashland Post Office", "Ashland", "Business Name", "Ashland Post Office (Burby Repair LLC)"),
    ("presque_isle_area.csv", "Ashland Public Library", "Ashland", "Business Name", "Ashland Community Library"),
]

# Duplicates to remove: (csv_file, business_name, town)
DUPLICATES_TO_REMOVE = [
    ("caribou_limestone.csv", "Cote's Auto Repair", "Limestone"),  # keep "Cote Auto Repair Inc."
    ("caribou_limestone.csv", "The Bunker Inn", "Limestone"),  # keep "Bunker Inn"
    ("caribou_limestone.csv", "Manaus Books & Coffee Shop", "Limestone"),  # keep "Manaus Books & Coffee"
    ("caribou_limestone.csv", "Caribou Bowl-O-Drome", "Caribou"),  # keep "Caribou Bowl-A-Drome"
    ("caribou_limestone.csv", "Ruska Coffee Company", "Caribou"),  # keep "Ruska Coffee Co."
    ("caribou_limestone.csv", "Plourde Furniture Company", "Caribou"),  # keep "Plourde Furniture Co."
    ("caribou_limestone.csv", "Caribou Recreation Department", "Caribou"),  # keep "Caribou Parks & Recreation Department"
    ("caribou_limestone.csv", "Caribou Save-a-Lot", "Caribou"),  # keep "Save-A-Lot"
    ("caribou_limestone.csv", "Caribou Inn & Convention Center", "Caribou"),  # keep "Best Western Caribou Inn"
    ("caribou_limestone.csv", "Caribou Theater", "Caribou"),  # keep "The Caribou Theater"
    ("caribou_limestone.csv", "Haney's", "Caribou"),  # keep "Haney's Building Specialties"
    ("caribou_limestone.csv", "Pines Health Services Caribou", "Caribou"),  # keep "Pines Health Services - Caribou Health Center"
    ("presque_isle_area.csv", "Big Rock Ski Area", "Mars Hill"),  # keep "BigRock Mountain"
    ("presque_isle_area.csv", "Gateway Variety", "Ashland"),  # keep "Gateway Trading Post Inc"
    ("presque_isle_area.csv", "USPS Mapleton Post Office", "Mapleton"),  # keep "Mapleton Post Office"
    ("presque_isle_area.csv", "Presque Isle Inn and Convention Center", "Presque Isle"),  # keep "Presque Isle Hotel"
    ("presque_isle_area.csv", "USPS Washburn Post Office", "Washburn"),  # keep "Washburn Post Office" (but fix address)
    ("presque_isle_area.csv", "Washburn Public Library", "Washburn"),  # keep "Washburn Memorial Public Library"
    ("houlton_region.csv", "County Co-op and Farm Store", "Houlton"),  # keep "The Country Co-op and Farm Store"
    ("houlton_region.csv", "Houlton Community Golf Course", "New Limerick"),  # keep "Houlton Community Golf Club"
    ("houlton_region.csv", "Hidden Spring Winery", "Houlton"),  # keep Hodgdon version
    ("houlton_region.csv", "Ferris Qwik Stop (Linneus Corner Store)", "Linneus"),  # both have same address, keep "Clark's Variety"
    ("houlton_region.csv", "Market Square Housing/CC Realty Mgmt", "Houlton"),  # keep "Houlton Market Square Shopping Center"
    ("houlton_region.csv", "Mini Music Shop (2nd location)", "New Limerick"),  # keep "Mini Music Shop" Houlton version
    ("houlton_region.csv", "Whited Bible Camp", "Bridgewater"),  # keep "Aroostook Pentecostal Campground"
    ("houlton_region.csv", "Shiretown Inn and Suites", "Houlton"),  # keep under this name
    ("presque_isle_area.csv", "Northwoods Diner", "Ashland"),  # keep "Old Post Cafe" (same biz, keep one)
    ("presque_isle_area.csv", "Shell Gas Station", "Fort Fairfield"),  # keep "Freshies Fort Fairfield"
    ("presque_isle_area.csv", "On the Run", "Caribou"),  # keep "Mobil / On the Run" (already merged)
]

# Also need to fix: the "Ashland Post Office" at 54 Main St is actually Burby Repair LLC
# Add as duplicate removal
DUPLICATES_TO_REMOVE.append(("presque_isle_area.csv", "Ashland Post Office", "Ashland"))  # wrong entry, keep USPS one
# But wait - we already corrected the address above. Let me think about this.
# Actually there are TWO entries:
# 1. "Ashland Post Office" at 54 Main St
# 2. "USPS Ashland Post Office" at 14 Sheridan Rd
# The research said the 54 Main St one is actually "Burby Repair LLC"
# So we should rename "Ashland Post Office" to "Burby Repair LLC" with correct phone
# Or remove it since it's a completely wrong listing.

# Better: rename and fix
CORRECTIONS.append(("presque_isle_area.csv", "Ashland Post Office", "Ashland", "Business Name", "Burby Repair LLC"))
CORRECTIONS.append(("presque_isle_area.csv", "Ashland Post Office", "Ashland", "Phone", "(207) 435-9010"))

# Washburn Post Office at 8 Main St - fix address to 9 Woodman St (same as USPS entry)
CORRECTIONS.append(("presque_isle_area.csv", "Washburn Post Office", "Washburn", "Street Address", "9 Woodman St"))

# Northwoods Diner / Old Post Cafe - same business, merge
CORRECTIONS.append(("presque_isle_area.csv", "Old Post Cafe", "Ashland", "Business Name", "Northwoods Diner / Old Post Cafe"))


def apply_corrections():
    for csv_file in set(c for c, _, _, _, _ in CORRECTIONS) | set(d for d, _, _ in DUPLICATES_TO_REMOVE):
        path = f'cleaned/{csv_file}'
        if not os.path.exists(path):
            print(f"File not found: {path}")
            continue
        
        with open(path, newline='') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
        
        original_count = len(rows)
        changes = []
        removals = []
        
        # Apply field corrections
        for cfile, name, town, field, value in CORRECTIONS:
            if cfile != csv_file:
                continue
            for row in rows:
                if row['Business Name'].strip() == name and row['Town'].strip() == town:
                    old_val = row[field]
                    row[field] = value
                    changes.append(f"  {name} ({town}): {field} '{old_val}' -> '{value}'")
                    break
        
        # Remove duplicates
        for dfile, name, town in DUPLICATES_TO_REMOVE:
            if dfile != csv_file:
                continue
            new_rows = []
            for row in rows:
                if row['Business Name'].strip() == name and row['Town'].strip() == town:
                    removals.append(f"  REMOVED: {name} ({town})")
                else:
                    new_rows.append(row)
            rows = new_rows
        
        # Write updated CSV
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        removed_count = original_count - len(rows)
        print(f"\n=== {csv_file} ===")
        print(f"  Rows: {original_count} -> {len(rows)} ({removed_count} removed)")
        if changes:
            print(f"  Corrections ({len(changes)}):")
            for c in changes:
                print(c)
        if removals:
            print(f"  Removals ({len(removals)}):")
            for r in removals:
                print(r)


def verify_duplicates_removed():
    """Check if any duplicates remain"""
    from collections import Counter
    for csv_file in ['presque_isle_area.csv', 'caribou_limestone.csv', 'houlton_region.csv', 'millinocket_area.csv', 'lincoln_area.csv']:
        with open(f'cleaned/{csv_file}') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Check for (name, town) duplicates
        keys = [(r['Business Name'].strip(), r['Town'].strip()) for r in rows]
        dupes = [(k, v) for k, v in Counter(keys).items() if v > 1]
        if dupes:
            print(f"\nREMAINING DUPLICATES in {csv_file}:")
            for (name, town), count in dupes:
                addrs = set(r['Street Address'].strip() for r in rows if r['Business Name'].strip() == name and r['Town'].strip() == town)
                print(f"  {name} ({town}) x{count} at {addrs}")
        

if __name__ == '__main__':
    apply_corrections()
    verify_duplicates_removed()
