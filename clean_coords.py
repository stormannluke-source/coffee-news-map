import json

def main():
    with open('cleaned/all_businesses.json') as f:
        businesses = json.load(f)

    with open('coordinates.json') as f:
        all_coords = json.load(f)

    # Build set of keys for surviving businesses (use the 'key' field from JSON)
    active_keys = set()
    for b in businesses:
        active_keys.add(b.get('key', ''))

    # Keep only coords for active businesses
    coords = {}
    removed = 0
    for key, val in all_coords.items():
        if key in active_keys:
            coords[key] = val
        else:
            removed += 1

    with open('coordinates.json', 'w') as f:
        json.dump(coords, f, indent=2)

    print(f'Coordinates cleaned: {len(coords)} kept, {removed} removed')

if __name__ == '__main__':
    main()
