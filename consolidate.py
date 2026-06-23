import csv
import json
import os
import re
from collections import OrderedDict

OUTPUT_DIR = "cleaned"

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
    return None

def normalize_phone(phone):
    if not phone:
        return ""
    digits = re.sub(r'[^\d]', '', phone)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    elif len(digits) == 7:
        return f"(207) {digits[:3]}-{digits[3:]}"
    return phone.strip()

def normalize_name(name):
    name = name.strip().strip('"').strip()
    name = re.sub(r'\s+', ' ', name)
    return name

def name_key(name):
    key = name.lower()
    key = re.sub(r'[^a-z0-9]', '', key)
    return key

def read_csv_8col(filepath):
    rows = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

FILES_8COL = [
    "business_lists/presque_isle_area_businesses.csv",
    "business_lists/houlton_region_businesses.csv",
    "business_lists/millinocket_area_businesses.csv",
    "business_lists/lincoln_area_businesses.csv",
]

FILES_7COL = [
    "business_directory.csv",
    "caribou_limestone_business_directory.csv",
]

def convert_7col_to_8col(filepath, source_region):
    rows = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            new_row = {
                "Business Name": normalize_name(row.get("Business Name", "")),
                "Street Address": row.get("Street Address", "").strip(),
                "City": row.get("City", "").strip(),
                "State": row.get("State", "").strip(),
                "Zip": row.get("Zip", "").strip(),
                "Phone": normalize_phone(row.get("Phone", "")),
                "Email": "",
                "Website": "",
                "Category": row.get("Category", "").strip(),
                "Town": row.get("City", "").strip(),
            }
            rows.append(new_row)
    return rows

def load_all():
    all_rows = []
    source_info = {}

    # Load 8-col files
    for fp in FILES_8COL:
        rows = read_csv_8col(fp)
        for r in rows:
            r["Business Name"] = normalize_name(r.get("Business Name", ""))
            r["Phone"] = normalize_phone(r.get("Phone", ""))
            r["Street Address"] = r.get("Street Address", "").strip()
            r["City"] = r.get("City", "").strip()
            r["State"] = r.get("State", "").strip()
            r["Zip"] = r.get("Zip", "").strip()
            r["Email"] = r.get("Email", "").strip()
            r["Website"] = r.get("Website", "").strip()
            r["Category"] = r.get("Category", "").strip()
            r["Town"] = r.get("Town", "").strip()
            if not r["Town"]:
                r["Town"] = r["City"]
            all_rows.append(r)
            source_info[id(r)] = "business_lists"

    for fp in FILES_7COL:
        rows = convert_7col_to_8col(fp, None)
        for r in rows:
            if not r["Town"]:
                r["Town"] = r["City"]
            all_rows.append(r)
            source_info[id(r)] = "root"

    return all_rows, source_info

def deduplicate(rows, source_info):
    deduped = OrderedDict()

    for r in rows:
        nk = name_key(r["Business Name"])
        town = r["Town"].strip().lower() if r["Town"] else ""
        city = r["City"].strip().lower() if r["City"] else ""
        match_key = f"{nk}|{town or city}"

        if match_key in deduped:
            existing = deduped[match_key]
            existing_source = source_info.get(id(existing), "root")
            new_source = source_info.get(id(r), "root")

            for field in ["Business Name", "Street Address", "City", "State", "Zip", "Phone", "Email", "Website", "Category", "Town"]:
                existing_val = existing.get(field, "")
                new_val = r.get(field, "")
                if not existing_val and new_val:
                    existing[field] = new_val
                elif existing_val and new_val and existing_val != new_val:
                    # Prefer the more complete or standardized version
                    if existing_source == "root" and new_source == "business_lists":
                        existing[field] = new_val
                    elif len(new_val) > len(existing_val):
                        existing[field] = new_val
        else:
            deduped[match_key] = dict(r)

    return list(deduped.values())

def sanitize_for_json(val):
    if val is None:
        return ""
    val = val.strip()
    val = val.replace('\\', '\\\\')
    val = val.replace('"', '\\"')
    val = val.replace('\n', '\\n')
    val = val.replace('\r', '')
    val = val.replace('\t', ' ')
    return val

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading all CSV files...")
    all_rows, source_info = load_all()
    print(f"  Total pre-dedup rows: {len(all_rows)}")

    print("Deduplicating...")
    clean_rows = deduplicate(all_rows, source_info)
    print(f"  Total post-dedup rows: {len(clean_rows)}")

    # Assign regions
    for r in clean_rows:
        town = r.get("Town", "").strip()
        if town:
            r["Region"] = get_region(town) or "Other"
        else:
            r["Region"] = "Other"

    # Group by region
    region_groups = {}
    for r in clean_rows:
        region = r["Region"]
        if region not in region_groups:
            region_groups[region] = []
        region_groups[region].append(r)

    # Sort rows within each region by Town, then Business Name
    for region in region_groups:
        region_groups[region].sort(key=lambda x: (x.get("Town", ""), x.get("Business Name", "")))

    # Write region CSVs
    fieldnames = ["Business Name", "Street Address", "City", "State", "Zip", "Phone", "Email", "Website", "Category", "Town"]

    for region, rows in region_groups.items():
        safe_name = region.lower().replace("/", "_").replace(" ", "_")
        fp = os.path.join(OUTPUT_DIR, f"{safe_name}.csv")
        with open(fp, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(rows)
        print(f"  Wrote {len(rows)} rows -> {fp}")

    # Write master JSON
    master = []
    for r in clean_rows:
        entry = {
            "name": sanitize_for_json(r.get("Business Name", "")),
            "address": sanitize_for_json(r.get("Street Address", "")),
            "city": sanitize_for_json(r.get("City", "")),
            "state": sanitize_for_json(r.get("State", "")),
            "zip": sanitize_for_json(r.get("Zip", "")),
            "phone": sanitize_for_json(r.get("Phone", "")),
            "email": sanitize_for_json(r.get("Email", "")),
            "website": sanitize_for_json(r.get("Website", "")),
            "category": sanitize_for_json(r.get("Category", "")),
            "town": sanitize_for_json(r.get("Town", "")),
            "region": sanitize_for_json(r.get("Region", "")),
        }
        master.append(entry)

    json_fp = os.path.join(OUTPUT_DIR, "all_businesses.json")
    with open(json_fp, 'w', encoding='utf-8') as f:
        json.dump(master, f, indent=2, ensure_ascii=False)
    print(f"  Wrote {len(master)} entries -> {json_fp}")

    # Summary
    print(f"\nSummary:")
    print(f"  Total unique businesses: {len(clean_rows)}")
    for region, rows in sorted(region_groups.items()):
        towns = set(r.get("Town", "") for r in rows)
        print(f"  {region}: {len(rows)} businesses in {len(towns)} towns")
    print(f"\nDone.")

if __name__ == "__main__":
    main()
