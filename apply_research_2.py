import csv
import re

EMAIL_UPDATES = {
    # === Millinocket Area - New Research (June 2026) ===
    "crandall's hardware|east millinocket": "info@crandallshardware.com",
    "ellis family market|east millinocket": "peter.ellis@hannaford.com",
    "ellis family market|patten": "joellis@hannaford.com",
    "appalachian trail lodge|millinocket": "info@appalachiantrailhostel.com",
    "gather inn|millinocket": "gatherinn.me@gmail.com",
    "magic city real estate|millinocket": "magiccityrealestate@outlook.com",
    "mt. chase lodge|shin pond": "info@mtchaselodge.com",

    # === Lincoln Area - New Research (June 2026) ===
    "marble creek acres winery & cidery|lee": "mainecellars@gmail.com",
}

def normalize(s):
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9\s]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s

def make_key(name, town):
    return f"{normalize(name)}|{normalize(town)}"

def preprocess():
    normalized = {}
    for raw_key, email in EMAIL_UPDATES.items():
        parts = raw_key.split('|')
        if len(parts) == 2:
            normalized[make_key(parts[0], parts[1])] = email
    return normalized

def main():
    normalized = preprocess()
    total_applied = 0

    for region in ['millinocket_area', 'lincoln_area']:
        fp = f'cleaned/{region}.csv'
        with open(fp, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = reader.fieldnames

        updated = 0
        for row in rows:
            key = make_key(row['Business Name'], row['Town'])
            if key in normalized and not row.get('Email', '').strip():
                row['Email'] = normalized[key]
                updated += 1
                print(f"  {row['Business Name']} ({row['Town']}) -> {normalized[key]}")

        if updated:
            with open(fp, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

        total_applied += updated
        print(f'{region}: Added {updated} emails')

    print(f'\nTotal emails added: {total_applied}')

if __name__ == '__main__':
    main()
