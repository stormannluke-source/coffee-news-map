import json, re, sys

BIZ_FILE = 'cleaned/all_businesses.json'
COORDS_FILE = 'coordinates.json'
HTML_FILE = 'index.html'

with open(BIZ_FILE, encoding='utf-8') as f:
    biz_data = json.load(f)

with open(COORDS_FILE, encoding='utf-8') as f:
    coords_data = json.load(f)

with open(HTML_FILE, encoding='utf-8') as f:
    html = f.read()

# -------------------------------------------------------------------
# Replace INLINED_BIZ — a JS array [...]
# Marker in HTML: `var INLINED_BIZ = [`
# json.dumps(biz_data) produces `[{...}, {...}]` — strip outer brackets
# -------------------------------------------------------------------
biz_marker_start = 'var INLINED_BIZ = ['
biz_marker_end = '];'

biz_idx = html.find(biz_marker_start)
if biz_idx == -1:
    print('ERROR: var INLINED_BIZ not found')
    sys.exit(1)

# Find the end of the current array (next ]; that closes the array)
biz_end_idx = html.find(biz_marker_end, biz_idx)
if biz_end_idx == -1:
    print('ERROR: ]; not found after var INLINED_BIZ')
    sys.exit(1)

biz_json_str = json.dumps(biz_data, indent=2, ensure_ascii=False)
# Strip outer [ and ] from json array, keeping inner content
biz_inner = biz_json_str[1:-1].strip()
new_biz_section = biz_marker_start + '\n' + biz_inner + '\n' + biz_marker_end

html = html[:biz_idx] + new_biz_section + html[biz_end_idx + len(biz_marker_end):]

# -------------------------------------------------------------------
# Replace INLINED_COORDS — a JS object {...}
# Marker in HTML: `var INLINED_COORDS = {`
# json.dumps(coords_data) produces `{"key": {...}}` — strip outer braces
# -------------------------------------------------------------------
coord_marker_start = 'var INLINED_COORDS = {'
coord_marker_end = '};'

coord_idx = html.find(coord_marker_start)
if coord_idx == -1:
    print('ERROR: var INLINED_COORDS not found')
    sys.exit(1)

coord_end_idx = html.find(coord_marker_end, coord_idx)
if coord_end_idx == -1:
    print('ERROR: }; not found after var INLINED_COORDS')
    sys.exit(1)

coord_json_str = json.dumps(coords_data, indent=2, ensure_ascii=False)
# Strip outer { and } from json object, keeping inner content
coord_inner = coord_json_str[1:-1].strip()
new_coord_section = coord_marker_start + '\n' + coord_inner + '\n' + coord_marker_end

html = html[:coord_idx] + new_coord_section + html[coord_end_idx + len(coord_marker_end):]

# -------------------------------------------------------------------
# Validation
# -------------------------------------------------------------------
# Count entries by parsing the arrays
biz_count = html.count('"key": "')
coord_count = html.count('"lat":')
print(f'Inlined INLINED_BIZ entries (by "key" count):  {biz_count}')
print(f'Inlined INLINED_COORDS entries (by "lat" count): {coord_count}')

# Check apostolic church website
if 'apostolic_church_in_jesus_name_ashland' in html:
    m = re.search(r'"key":\s*"apostolic_church_in_jesus_name_ashland".*?"website":\s*"([^"]*)"', html, re.DOTALL)
    if m:
        site = m.group(1)
        wendy_free = site == '' or 'malls.fandom.com' not in site
        print(f'Apostolic Church website: "{site}" → {"OK" if wendy_free else "WENDYS LINK STILL PRESENT!"}')

# Scan for known stale bad-URL patterns
bad_patterns = ['malls.fandom.com', 'telephonedirectories.us', 'cybo.com', 'intelius.com',
                'truthfinder.com', 'allbiz.com', '2findlocal.com', 'phonelookup.com',
                'usphonebook.com', 'adsinterlock.com', 'restaurantguru.com',
                'themainemenu.com', 'archives.com/genealogy', 'processingbordeaux.org',
                'opengovca.com', 'tattooed.co', 'cityunwrapped.com',
                'bukutelepon.cybo.com', 'wellness.com/dir', 'usarestaurants.info',
                'furniture.com/stores', 'weather.gov', 'wikipedia.org']
found_bad = 0
for p in bad_patterns:
    # Only count in the INLINED_BIZ section
    biz_section = html[biz_idx:coord_idx]
    count = biz_section.count(p)
    if count > 0:
        found_bad += count
        print(f'  STALE: {p} found {count}x in INLINED_BIZ')

if found_bad == 0:
    print(f'No stale bad URLs found in INLINED_BIZ ✓')

with open(HTML_FILE, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'\nDone. index.html updated.')
