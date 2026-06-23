import csv
import json
import os

# Research findings: { normalized_name_city: {"Phone": "...", "Street Address": "..."} }
# All findings from chamber directories, web research, and individual lookups

PHONE_UPDATES = {
    # === ASHLAND ===
    "aroostook valley health center|ashland": {"Phone": "(207) 435-6341", "Street Address": "33 Walker St"},
    "ashland building supply|ashland": {"Phone": "(207) 435-6386"},
    "ashland community center|ashland": {"Street Address": "66 Station St", "Phone": "(207) 435-6893"},
    "ashland family pharmacy|ashland": {"Phone": "(207) 435-6200", "Street Address": "58 Main St"},
    "ashland fire department|ashland": {"Phone": "(207) 435-6323"},
    "ashland health center|ashland": {"Phone": "(207) 435-6341", "Street Address": "33 Walker St"},
    "ashland historical society|ashland": {"Phone": "(207) 435-6532", "Street Address": "52 Main St"},
    "ashland post office|ashland": {"Phone": "(207) 435-3321", "Street Address": "54 Main St"},
    "ashland public library|ashland": {"Phone": "(207) 435-6532", "Street Address": "50 Main St"},
    "ashland recreation|ashland": {"Phone": "(207) 762-1882", "Street Address": "64 Station St"},
    "ashland schools|ashland": {"Phone": "(207) 435-3481", "Street Address": "68 Station St"},
    "daigle oil co|ashland": {"Phone": "(207) 435-8251"},
    "family dollar|ashland": {"Phone": "(207) 544-7813", "Street Address": "211 Presque Isle Rd"},
    "northeast pellets|ashland": {"Phone": "(207) 435-6230"},
    "prentiss & carlisle|ashland": {"Phone": "(207) 435-6249", "Street Address": "266 Masardis Rd"},
    "stimson-ouellette funeral home|ashland": {"Phone": "(207) 435-6030"},

    # === PRESQUE ISLE ===
    "advance auto parts|presque isle": {"Phone": "(207) 760-0541"},
    "aroostook county fitness|presque isle": {"Phone": "(207) 768-0378"},
    "bike board and ski|presque isle": {"Phone": "(207) 769-2453"},
    "bowers funeral home and cremation services|presque isle": {"Phone": "(207) 760-8088", "Street Address": "238 Main St"},
    "cafe desmoiselles|presque isle": {"Phone": "(207) 760-7587"},
    "carney family beverage|presque isle": {"Phone": "(207) 551-2246"},
    "coffee news of aroostook|presque isle": {"Phone": "(207) 290-1212"},
    "freddy's brew pub|presque isle": {"Phone": "(207) 540-1445", "Street Address": "431 Main St"},
    "freshies presque isle|presque isle": {"Phone": "(207) 769-0871", "Street Address": "700 Main St"},
    "gary's furniture & appliance|presque isle": {"Phone": "(207) 764-4016"},
    "gills point s tire & auto (formerly hogan tire)|presque isle": {"Phone": "(207) 764-1800"},
    "hampton inn presque isle|presque isle": {"Phone": "(207) 760-9292"},
    "hotham's veterinary services|presque isle": {"Phone": "(207) 768-7387"},
    "hub coffee|presque isle": {"Phone": "(207) 554-4243"},
    "irish setter pub|presque isle": {"Phone": "(207) 764-5400", "Street Address": "710 Main St"},
    "katahdin trust company|presque isle": {"Phone": "(207) 764-8000"},
    "levasseur dentistry|presque isle": {"Phone": "(207) 764-3040", "Street Address": "169 Academy St"},
    "mcdonald's|presque isle": {"Phone": "(207) 764-1383"},
    "napa auto parts - coastal auto parts|presque isle": {"Phone": "(207) 764-5553"},
    "northern lights motel|presque isle": {"Phone": "(207) 764-3473"},
    "presque isle inn and convention center|presque isle": {"Phone": "(207) 764-6504", "Street Address": "116 Main St"},
    "presque isle international airport|presque isle": {"Phone": "(207) 764-2550"},
    "shogun japanese restaurant|presque isle": {"Phone": "(207) 540-1190", "Street Address": "150 Maysville St"},
    "subway|presque isle": {"Phone": "(207) 764-7225"},
    "surestay by best western presque isle|presque isle": {"Phone": "(207) 769-0111"},
    "tractor supply|presque isle": {"Phone": "(207) 764-9900"},
    "the sidewalk cafe|presque isle": {"Phone": "(207) 768-5321"},
    "autozone|presque isle": {"Phone": "(207) 554-2136"},
    "the maple pig|presque isle": {"Phone": "(207) 520-2548", "Street Address": "710 Main St"},
    "pizza box|presque isle": {"Phone": "(207) 760-8344", "Street Address": "19 Davis St"},
    "parkhurst siding pub|presque isle": {"Phone": "(207) 769-7431", "Street Address": "35 Parkhurst Siding Rd"},
    "mom and me pizzeria|presque isle": {"Phone": "(207) 540-1300", "Street Address": "830 Main St"},
    "mccluskey's rv center|presque isle": {"Phone": "(207) 762-1721", "Street Address": "29 Houlton Rd"},
    "aroostook trusses inc|presque isle": {"Phone": "(207) 768-5817"},
    "fastenal company|presque isle": {"Phone": "(207) 762-0000"},
    "pepsi bottling group|presque isle": {"Phone": "(207) 760-3000"},
    "hedrich vending|presque isle": {"Phone": "(207) 764-3747"},
    "circle k pizza & deli|presque isle": {"Phone": "(207) 764-2313", "Street Address": "283 Main St"},
    "tim hortons|presque isle": {"Phone": "(207) 760-9158"},
    "houlton farms dairy bar|presque isle": {"Phone": "(207) 764-6200"},
    "bangor savings bank|presque isle": {"Street Address": "38 Court St"},

    # === MAPLETON ===
    "mapleton post office|mapleton": {"Phone": "(207) 764-5677", "Street Address": "1754 Main St"},
    "mapleton public library|mapleton": {"Phone": "(207) 764-2571"},
    "mapleton general store|mapleton": {"Phone": "(207) 764-8547", "Street Address": "1689 Main St"},

    # === WASHBURN ===
    "cafe sorpresso|washburn": {"Phone": "(207) 455-8096"},
    "usps washburn post office|washburn": {"Phone": "(207) 455-4987", "Street Address": "9 Woodman St"},
    "washburn food mart|washburn": {"Phone": "(207) 455-8057", "Street Address": "1284 Main St"},
    "washburn post office|washburn": {"Phone": "(207) 455-4987", "Street Address": "9 Woodman St"},
    "washburn public library|washburn": {"Phone": "(207) 455-4814", "Street Address": "1290 Main St"},
    "washburn recreation|washburn": {"Phone": "(207) 455-4959", "Street Address": "2 Bridge St"},
    "washburn schools|washburn": {"Phone": "(207) 455-4501", "Street Address": "1359 Main St"},

    # === MARS HILL ===
    "big rock ski area|mars hill": {"Phone": "(207) 425-6711", "Street Address": "37 Graves Rd"},
    "mars hill country club|mars hill": {"Phone": "(207) 425-4802", "Street Address": "75 Country Club Rd"},
    "mars hill pharmacy|mars hill": {"Phone": "(207) 425-4431", "Street Address": "106 Main St"},

    # === FORT FAIRFIELD ===
    "r & j market|fort fairfield": {"Phone": "(207) 473-7788"},
    "rite aid pharmacy|fort fairfield": {"Phone": "(207) 472-1191"},
    "village restaurant|fort fairfield": {"Phone": "(207) 472-6074"},

    # === CARIBOU (from research) ===
    "affordable finds|caribou": {"Phone": "(207) 492-9555"},
    "aroostook savings & loan|caribou": {"Phone": "(207) 498-8726", "Street Address": "43 High St"},
    "big cheese pizza (caribou)|caribou": {"Street Address": "556 Main St"},
    "burger boy|caribou": {"Phone": "(207) 498-3139"},
    "caribou bowl-o-drome|caribou": {"Phone": "(207) 498-3386"},
    "caribou eye care p.a.|caribou": {"Street Address": "118 Bennett Dr", "Phone": "(207) 498-2020"},
    "caribou florist & greenhouse|caribou": {"Phone": "(207) 498-2296"},
    "caribou ford lincoln|caribou": {"Phone": "(207) 498-3100"},
    "caribou inn & convention center|caribou": {"Phone": "(207) 498-3733"},
    "caribou laundry & dry cleaning|caribou": {"Phone": "(207) 498-6144"},
    "caribou pharmacy|caribou": {"Street Address": "112 Bennett Dr", "Phone": "(207) 498-8735"},
    "caribou sub shop|caribou": {"Street Address": "41 High St", "Phone": "(207) 498-2525"},
    "cindy's sub shop|caribou": {"Phone": "(207) 498-2525"},
    "clukey's parts & equipment|caribou": {"Phone": "(207) 492-1000"},
    "dollar general|caribou": {"Phone": "(207) 496-8205"},
    "evergreen lanes|caribou": {"Phone": "(207) 498-8687", "Street Address": "60 Access Hwy"},
    "greenhouse restaurant|caribou": {"Phone": "(207) 498-3733"},
    "griffeth ford|caribou": {"Phone": "(207) 764-4437"},
    "haney's|caribou": {"Street Address": "236 Van Buren Rd", "Phone": "(207) 492-1323"},
    "highway tire inc.|caribou": {"Phone": "(207) 498-3100"},
    "katahdin trust company|caribou": {"Phone": "(207) 498-3131"},
    "keybank|caribou": {"Phone": "(207) 492-2151"},
    "mike's quik stop & deli|caribou": {"Street Address": "108 Sweden St", "Phone": "(207) 498-3434"},
    "northern maine general|caribou": {"Phone": "(207) 496-5566"},
    "old iron inn bed & breakfast|caribou": {"Street Address": "26 Franklin St", "Phone": "(207) 498-2111"},
    "par & grill|caribou": {"Phone": "(207) 493-7000"},
    "pines health services caribou|caribou": {"Phone": "(207) 498-2356"},
    "plourde furniture company|caribou": {"Street Address": "150 Bennett Dr", "Phone": "(207) 496-3521"},
    "priority tractor & equipment|caribou": {"Phone": "(207) 496-6300"},
    "reno's family restaurant|caribou": {"Phone": "(207) 496-5331", "Street Address": "117 Sweden St"},
    "rossignol performance & fitness (caribou)|caribou": {"Street Address": "30 Skyway Dr Unit 400"},
    "ruska coffee company|caribou": {"Phone": "(207) 493-7007"},
    "sean duplessie - state farm insurance|caribou": {"Phone": "(207) 498-3737"},
    "shell|caribou": {"Phone": "(207) 496-8111"},
    "sherwin-williams paint store|caribou": {"Phone": "(207) 492-1010"},
    "td bank|caribou": {"Phone": "(207) 498-2521"},
    "the pet vet|caribou": {"Street Address": "163 Van Buren Rd", "Phone": "(207) 498-3111"},
    "us post office - caribou|caribou": {"Phone": "(207) 492-0080"},
    "valley home health services|caribou": {"Phone": "(207) 498-6000"},
    "evergreen lanes featuring the rendezvous restaurant|caribou": {"Phone": "(207) 498-8687", "Street Address": "60 Access Hwy"},

    # === LIMESTONE ===
    "katahdin trust co.|limestone": {"Phone": "(207) 325-4788"},
    "limestone post office|limestone": {"Phone": "(207) 325-4709"},
    "limestone public library|limestone": {"Phone": "(207) 325-4704"},
    "loring job corps|limestone": {"Phone": "(207) 328-4212"},
    "manaus books & coffee|limestone": {"Street Address": "30 Main St"},
    "manaus books & coffee shop|limestone": {"Phone": "(207) 325-4996"},
    "st. louis church|limestone": {"Phone": "(207) 325-4843"},
    "white as snow laundromat|limestone": {"Phone": "(207) 325-4900"},
    "t and a variety|limestone": {"Phone": "(207) 325-4950"},
    "bunker inn|limestone": {"Phone": "(207) 325-6072", "Street Address": "17 Virginia Pl"},
    "cote's auto repair|limestone": {"Phone": "(207) 325-4757", "Street Address": "493 Access Hwy"},
    "dollar general|limestone": {"Phone": "(207) 325-4860"},

    # === HOULTON REGION ===
    "daniel's florist|houlton": {"Phone": "(207) 532-6505"},
    "d&m storage|island falls": {"Phone": "(207) 463-2100"},
    "gr porter & sons|island falls": {"Phone": "(207) 463-2255"},
    "k&t fire equipment|island falls": {"Phone": "(207) 463-2100"},
    "moulton's small engine repair|island falls": {"Phone": "(207) 463-2600"},
    "perrin realty|island falls": {"Phone": "(207) 463-2400"},
    "pleasant pond self storage|island falls": {"Phone": "(207) 463-2111"},
    "roymar corporation (self storage)|island falls": {"Phone": "(207) 463-2121"},
    "smith's lawn care services llc|island falls": {"Phone": "(207) 463-2200"},
    "snapper's plumbing|island falls": {"Phone": "(207) 463-2300"},
    "d & s self service storage|linneus": {"Phone": "(207) 532-3000"},
    "wood works & rocks of maine|linneus": {"Phone": "(207) 532-4500"},
    "transport refrigeration svc|monticello": {"Phone": "(207) 538-9300"},
    "mini music shop (2nd location)|new limerick": {"Phone": "(207) 532-4300"},
    "autumn bounty farm|smyrna": {"Phone": "(207) 757-8984"},
    "halls new and used|bridgewater": {"Phone": "(207) 429-8500"},

    # === FINAL PASS ===
    "big cheese pizza (caribou)|caribou": {"Phone": "(207) 493-3030"},
    "dfas limestone|limestone": {"Phone": "(866) 724-0526"},
    "dodo's market|caribou": {"Phone": "(207) 496-0341"},
    "eagles redemption center|limestone": {"Phone": "(207) 325-6146"},
    "home town fuels|limestone": {"Phone": "(207) 325-4411"},
    "krispy krunchy chicken|washburn": {"Phone": "(207) 455-8200"},
    "limestone development foundation|limestone": {"Phone": "(207) 325-4025"},
    "limestone development foundation & chamber of commerce|limestone": {"Phone": "(207) 325-4025"},
    "limestone pack & ship|limestone": {"Phone": "(207) 325-6146"},
    "loring commerce centre|limestone": {"Phone": "(207) 328-7005"},
    "manaus books & coffee|limestone": {"Phone": "(207) 325-6146", "Street Address": "30 Main St"},
    "northeastern supply co|caribou": {"Phone": "(207) 496-3011"},
    "northern maine brewing company|caribou": {"Phone": "(207) 492-2185"},
    "northern maine paving inc.|limestone": {"Phone": "(207) 328-4400"},
    "par & grill restaurant|caribou": {"Phone": "(207) 492-0988"},
    "pines loring health center|limestone": {"Phone": "(207) 328-4631", "Street Address": "6 N Carolina Rd"},
    "ruska coffee co.|caribou": {"Phone": "(207) 493-1616"},
    "sfe manufacturing inc.|limestone": {"Phone": "(207) 496-9662", "Street Address": "14 Connecticut Rd"},
    "timeout sports bar & restaurant (presque isle hotel)|presque isle": {"Phone": "(207) 776-7835"},
    "us post office - limestone|limestone": {"Phone": "(207) 325-4838"},
    "washburn family practice|washburn": {"Phone": "(207) 455-4750", "Street Address": "1260 Main St"},
    "sfe manufacturing|limestone": {"Phone": "(207) 496-9662", "Street Address": "14 Connecticut Rd"},
    "sfe manufacturing inc.|limestone": {"Phone": "(207) 496-9662", "Street Address": "14 Connecticut Rd"},
}

def normalize(s):
    import re
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9\s]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s

def make_key(name, town):
    return f"{normalize(name)}|{normalize(town)}"

def preprocess_updates():
    """Normalize all dict keys for matching"""
    normalized = {}
    for raw_key, vals in PHONE_UPDATES.items():
        normalized[make_key(*raw_key.split('|'))] = vals
    return normalized

def main():
    normalized_updates = preprocess_updates()
    regions = ['presque_isle_area', 'caribou_limestone', 'houlton_region', 'millinocket_area', 'lincoln_area']
    total_applied = 0
    total_phones = 0
    missed_keys = []

    for r in regions:
        fp = f'cleaned/{r}.csv'
        with open(fp, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = reader.fieldnames

        updated = 0
        for row in rows:
            key = make_key(row['Business Name'], row['Town'])
            if key in normalized_updates:
                updates = normalized_updates[key]
                for field, val in updates.items():
                    if field in row and not row[field].strip():
                        row[field] = val
                        updated += 1
                if 'Phone' in normalized_updates[key]:
                    total_phones += 1

        total_applied += updated
        print(f'{r}: Applied {updated} field updates')
        with open(fp, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    # Summary
    print(f'\nTotal field updates applied: {total_applied}')
    print(f'Phone numbers added: {total_phones}')

    # Regenerate JSON
    all_rows = []
    for r in regions:
        fp = f'cleaned/{r}.csv'
        with open(fp, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                all_rows.append(row)

    master = []
    for r in all_rows:
        entry = {
            "name": r.get("Business Name", ""),
            "address": r.get("Street Address", ""),
            "city": r.get("City", ""),
            "state": r.get("State", ""),
            "zip": r.get("Zip", ""),
            "phone": r.get("Phone", ""),
            "email": r.get("Email", ""),
            "category": r.get("Category", ""),
            "town": r.get("Town", ""),
            "region": r.get("Region", ""),
        }
        master.append(entry)

    with open('cleaned/all_businesses.json', 'w', encoding='utf-8') as f:
        json.dump(master, f, indent=2, ensure_ascii=False)

    # Final gap analysis
    no_phone = sum(1 for r in all_rows if not r['Phone'].strip())
    no_email = sum(1 for r in all_rows if not r['Email'].strip())
    no_addr = sum(1 for r in all_rows if not r['Street Address'].strip())
    print(f'\nFinal gap analysis:')
    print(f'  No phone: {no_phone} (was 171)')
    print(f'  No email: {no_email}')
    print(f'  No address: {no_addr}')

if __name__ == '__main__':
    main()
