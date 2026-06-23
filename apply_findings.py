import csv
import json
import os
import re
from glob import glob

def normalize(s):
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9\s]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def make_key(name, town):
    return f"{normalize(name)}|{normalize(town)}"

def load_batch_results():
    findings = {}
    results_files = sorted(glob('batches/batch_*_results.json'))
    for f in results_files:
        with open(f) as fh:
            data = json.load(fh)
        for entry in data:
            key = make_key(entry.get('name', ''), entry.get('town', ''))
            if key:
                findings[key] = entry
    print(f"Loaded {len(findings)} findings from {len(results_files)} result files")
    return findings

def main():
    findings = load_batch_results()

    regions = ['presque_isle_area', 'caribou_limestone', 'houlton_region', 'millinocket_area', 'lincoln_area']
    total_ws = 0
    total_em = 0

    for region in regions:
        fp = f'cleaned/{region}.csv'
        with open(fp, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = reader.fieldnames

        updated_ws = 0
        updated_em = 0
        for row in rows:
            key = make_key(row['Business Name'], row.get('Town', ''))
            if key in findings:
                fdata = findings[key]
                # Apply website if empty
                if fdata.get('website') and not row.get('Website', '').strip():
                    row['Website'] = fdata['website']
                    updated_ws += 1
                # Apply email if empty
                if fdata.get('email') and not row.get('Email', '').strip():
                    row['Email'] = fdata['email']
                    updated_em += 1

        if updated_ws or updated_em:
            with open(fp, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

        total_ws += updated_ws
        total_em += updated_em
        print(f'{region}: +{updated_ws} websites, +{updated_em} emails')

    print(f'\nTotal: +{total_ws} websites, +{total_em} emails')

if __name__ == '__main__':
    main()
