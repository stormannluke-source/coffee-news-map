import json
import csv
import re
import os

# Load all findings
with open('audit_output/all_findings.json') as f:
    findings = json.load(f)

# Organize corrections
corrections = []  # (csv_file, business_name, match_town, field_updates, action)
duplicates = []   # (csv_file, business_name_to_remove)

for f in findings:
    v = f.get('verification', {})
    if v.get('status') != 'verified':
        continue
    
    name = f['name']
    town = f['town']
    csv_file = f['file']
    
    updates = {}
    
    # Phone correction
    csv_phone = f.get('phone', '')
    correct_phone = v.get('correct_phone', '')
    if correct_phone and correct_phone != 'UNVERIFIED' and correct_phone != csv_phone:
        updates['Phone'] = correct_phone
    
    # Address correction
    csv_addr = f.get('address', '')
    correct_addr = v.get('correct_address', '')
    if correct_addr and correct_addr != 'UNVERIFIED' and correct_addr != csv_addr:
        updates['Street Address'] = correct_addr
    
    # Name correction
    csv_name = v.get('correct_name', '')
    if csv_name and csv_name != 'UNVERIFIED' and csv_name != name:
        updates['Business Name'] = csv_name
    
    # Check if it's a duplicate (same address, same phone, different name)
    is_duplicate = v.get('notes', '').upper().find('DUPLICATE') >= 0
    
    if is_duplicate:
        duplicates.append((csv_file, name, town, v.get('notes', '')))
    elif updates:
        corrections.append((csv_file, name, town, updates, v.get('notes', '')))

print(f"=== CORRECTIONS TO APPLY: {len(corrections)} ===")
for csv_file, name, town, updates, notes in sorted(corrections):
    print(f"\n  [{csv_file}] {name} ({town})")
    for field, value in updates.items():
        print(f"    {field}: '{value}'")
    if notes:
        print(f"    Notes: {notes}")

print(f"\n=== DUPLICATES TO REMOVE: {len(duplicates)} ===")
for csv_file, name, town, notes in sorted(duplicates):
    print(f"  [{csv_file}] {name} ({town})")
    print(f"    Notes: {notes}")

# Save structured data
with open('audit_output/corrections_to_apply.json', 'w') as f:
    json.dump({'corrections': corrections, 'duplicates': duplicates}, f, indent=2)
