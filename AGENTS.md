# Coffee News of Aroostook — Project Guide

## Project Overview

Business directory database for the **Coffee News of Aroostook**, a free weekly community newspaper serving Aroostook County, Maine. Contains **1141** unique business listings across 4 regions.

**Goal:** Maintain accurate, up-to-date business contact information for publication reference, and provide an interactive map for browsing.

**Data Accuracy (as of June 22, 2026):**
- Phone numbers: 1136/1141 (99.6%)
- Street addresses: 1141/1141 (100%)
- Email addresses: 197/1141 (17.3%)
- Websites: 587/1141 (51.4%)
- Geocoded (lat/lng): 1141/1141 (100%)
- Google Geocoding API sweep: 962 ROOFTOP (84.3%), 177 road/town-level — cost $5.71
- All data synced: 1141 entries, 1141 coordinates, 0 orphans
- Cannabis dispensaries: 20
- Suitable for ad placement: 863/1141 (75.6%)
- Circle K names normalized: 7 variants → consistent naming

---

## File Structure

```
Coffee News/
├── AGENTS.md                           ← This file
├── business_lists/                     ← Original source files (8-col CSVs)
│   ├── presque_isle_area_businesses.csv
│   ├── houlton_region_businesses.csv
│   ├── millinocket_area_businesses.csv
│   └── lincoln_area_businesses.csv
├── cleaned/                            ← Deduplicated, cleaned output (4 CSV regions)
│   ├── presque_isle_area.csv           ← 490 businesses
│   ├── houlton_region.csv              ← 287 businesses
│   ├── millinocket_area.csv            ← 165 businesses
│   ├── lincoln_area.csv                ← 197 businesses
│   └── all_businesses.json             ← Master JSON for map (1139 entries)
├── coordinates.json                    ← Geocoded lat/lng (1139 entries)
├── consolidate.py                      ← Consolidation & deduplication
├── geocode.py                          ← Nominatim geocoding with town centers
├── regenerate_json.py                  ← Regenerates JSON from cleaned CSVs
├── apply_research.py                   ← Applies phone research findings
├── apply_emails.py                     ← Applies email research findings
├── apply_all_findings.py               ← Applies website & email findings
├── apply_findings.py                   ← Reads batches/*_results.json and applies to CSVs
├── filter_businesses.py                ← Removes no-phone/no-address entries
├── clean_coords.py                     ← Removes orphaned coordinate entries
├── collect_websites.py                 ← Automated website/email harvester (DuckDuckGo)
├── add_missing.py                      ← Adds missing businesses from chamber/Google research
├── crawl_emails.py                     ← Email harvester from known websites
├── geocode_recovery.py                 ← Targeted geocode recovery tool
├── regeocode.py                        ← Re-geocode audit (Phase 1: address query)
├── regeocode_phase2.py                 ← Re-geocode audit (Phase 2: name+town retry)
├── regeocode_checkpoint.json           ← Phase 1 checkpoint (resumable)
├── regeocode_phase2_checkpoint.json    ← Phase 2 checkpoint (resumable)
├── regeocode_report.txt                ← Precision audit report (363 entries need manual fix)
├── fix_bad_coords.py                   ← Fixed 13 misplaced coordinates via Nominatim
├── add_dispensaries.py                 ← Added 18 missing cannabis dispensaries to CSVs
├── geocode_new.py                      ← Geocode new entries (Nominatim + town center fallback)
├── precise_geocode_v2.py               ← Census Geocoder precision improvement (232 coordinates improved)
├── batches/                            ← Business batch files for parallel research
├── index.html                          ← Interactive Leaflet.js map (self-contained)
├── feature_explanation.md              ← Notes/visits/routes feature documentation
└── README.md
```

---

## CSV Schema (11-Column Standard)

| Column | Description |
|---|---|
| `Business Name` | Full legal or DBA name |
| `Street Address` | Physical street address |
| `City` | City/town name |
| `State` | Two-letter state abbreviation (always ME) |
| `Zip` | 5-digit ZIP code |
| `Phone` | Formatted as (207) XXX-XXXX |
| `Email` | Email address |
| `Website` | Website URL |
| `Category` | Business type (Grocery, Restaurant, etc.) |
| `Town` | Geographic sub-region/township |
| `SuitableForAds` | Yes/No — walk-in foot traffic suitable for ad placement |

---

## Regions

| Region | Towns Covered | Businesses |
|---|---|---|
| Presque Isle Area | Presque Isle, Caribou, Limestone, Fort Fairfield, Mars Hill, Mapleton, Washburn, Ashland | 490 (2 recovered - 1 duplicate removed) |
| Houlton Region | Houlton, Hodgdon, Littleton, Monticello, Linneus, Oakfield, Smyrna, New Limerick, Bridgewater, Island Falls, Dyer Brook | 287 (1 duplicate removed) |
| Millinocket Area | Millinocket, East Millinocket, Medway, Sherman, Patten, Mount Chase, Shin Pond | 165 |
| Lincoln Area | Lincoln, Howland, Enfield, Burlington, Chester, Winn, Mattawamkeag, Lee, Springfield, Greenbush, Lowell | 197 |

---

## Deduplication Rules

1. **Match criteria**: Business Name (case-insensitive, ignoring punctuation) + City
2. **Merge strategy**: For each field, prefer non-blank. If both non-blank and differ, prefer the more complete version.
3. **Priority**: `business_lists/` files > root-level files
4. **Exact duplicates** collapsed into one.

---

## Phone Number Formatting

`(207) XXX-XXXX` or `(XXX) XXX-XXXX`. Strip formatting, then reformat. If area code is missing and number is 7 digits, assume 207. Toll-free: `(888)`, `(800)`, `(866)`, `(855)`, `(877)`.

---

## Geocoding Rules

- Uses **Nominatim** (OpenStreetMap) API with town center fallbacks
- Rate limited to 1 request/second
- Town centers pre-set for all 35 communities
- Coordinates keyed by composite slug: `normalizeKey(name + town)` — never use name alone (causes collisions for chains like Family Dollar in multiple towns)
- All scripts use `socket.setdefaulttimeout(5)` + bare `except:` for graceful failure
- **Never use state-wide queries** ("Street Name, Maine") — caused ~55 cross-state misplacements. Town name must always be included.

---

## Map Features (index.html)

- **Leaflet.js** with OpenStreetMap tiles
- **Default filter**: Only suitable-for-ads businesses shown (861 of 1139) — churches, schools, campgrounds excluded by default
- Hierarchical filtering: Region → Town → Category → Search
- Active filter badges: pill-shaped tags showing current filters, dismissible individually
- Extended search: searches across name, address, town, category, and **phone number**
- **Filter count badges**: (N) counts on all dropdown options (region, town, category)
- Category color dots in Browse list table
- Color-coded markers with category SVG icons (see below)
- Notes (textarea per business, saved to localStorage, red dot indicator) with **follow-up date** support
- Visit tracking (date-stamped, green checkmark indicator)
- Saved routes (named, persist in localStorage, exportable as JSON)
- Export/import all notes, visits, routes as JSON for backup/transfer
- **4-region CSV download**: 📥 CSV button in header downloads per-region business lists
- **Copy address/phone**: 📋 clipboard buttons in detail pane
- **Offline banner**: red bar when no internet connection
- Reset button — clears all filters + active route
- Console diagnostics on page load (business/coord counts)
- Legend: bottom-right color key
- Responsive: works on mobile

### Marker Colors

| Color | Categories |
|---|---|
| Blue `#3498db` | Government/Education/Library |
| Green `#27ae60` | Grocery/Restaurant/Food |
| Red `#e74c3c` | Auto/Auto Parts/Repair |
| Purple `#8e44ad` | Healthcare/Dental/Vet |
| Orange `#f39c12` | Retail/Gift/Hardware |
| Brown `#cd7f32` | Lodging/Hotel/Motel/Campground |
| Yellow `#f1c40f` | Religion/Churches |
| Gray `#95a5a6` | Services/Other |

---

## Running

```bash
python3 consolidate.py            # Regenerate JSON from cleaned CSVs
python3 regenerate_json.py         # Regenerate all_businesses.json (includes key field)
python3 geocode.py                 # Geocode (or re-geocode)
python3 apply_research.py          # Apply phone research findings
python3 filter_businesses.py       # Remove no-phone/no-address businesses
python3 clean_coords.py            # Remove orphaned coordinates
python3 add_missing.py             # Add missing businesses

# Open map (no server needed — double-click index.html, or:)
python3 -m http.server 8000        # then visit http://localhost:8000
```

---

## Completed Work

- **1141 businesses** in directory, **863 (75.6%) suitable for ads**, **20 cannabis dispensaries**
- **Full data accuracy audit** completed — 7 data corruption errors fixed (fabricated addresses, wrong phone numbers). Most notable: Bangor Savings Bank Howland (72 Billings Ln → 22 Main St), Daigle Oil (6 Norton Ln → 50 Bangor St), F.A. Peabody Insurance (1 Peabody Ave → 29 North St)
- **28 town-only addresses** resolved — all have street addresses now
- **Chain deep dive**: 13 missing chains added (Harbor Freight, Dollar Tree, Subway FF, Advance Auto FF, Dollar General FF/Washburn/Millinocket, NAPA Caribou, O'Reilly Houlton, Tractor Supply Houlton, Taco Bell/Family Dollar/Walgreens Lincoln). All 30+ towns checked systematically — 29 towns confirmed with zero missing chains
- **16 Circle K locations** added across Houlton, Lincoln, Caribou, Presque Isle, Oakfield
- **Geocode bug fixed**: `clean_coords.py` was using `normalize_key(biz['name'])` instead of `make_key(name, town)` — fixed to use composite key
- **Cross-state coordinate errors fixed**: Lowell Baptist Church (MI→ME), St. John's/Bethany Baptist (MI→ME), Art's Appliance (NY→ME), Northwoods Sporting Journal/R.N. French (CT/NH→ME), Littleton Baptist (NH→ME)
- **Re-geocode audit (Phase 1 & 2)**: All 1122 entries re-queried via Nominatim with `addresstype` classification. 113 coordinates improved (63 via address query + 50 via name+town retry). Final: 650 building-level precise (57.9%), 363 road/town-level (32.4%), 112 skipped/no-address (10.0%). Report in `regeocode_report.txt`.
- **Handy Stop Howland fix**: Coordinates corrected from road-center (45.23643, -68.65696) to building at Bridge St/Coffin St intersection (45.2370, -68.6598) — corner building marked as "2 Coffin St."
- **Comprehensive coordinate error sweep**: Scanned all 1122 entries via distance-from-town-center check. Found and fixed 14 errors: 10 outside Maine (Ethiopia, Uganda, Japan, Bhutan, Scotland, London, Ontario, Iowa, Missouri, Texas border), 3 wrong-Maine-town (Marden's PI→Lincoln, True Value Boothbay→Lincoln, St. Thomas Camden→Winn), 1 border case (Sacred Heart Church at Lee Academy→Winn).
- **Census Geocoder precision sweep**: All 363 road-level entries re-queried via US Census Geocoder API. 232 coordinates improved to building-level precision. 9 bad matches caught and reverted via Nominatim. 10 entries fixed that were >20km from town center (Census returned wrong location for chain businesses). Final: 0 outside Maine, 0 missing addresses, 0 missing coords, 1140/1140 sync.
- **Chain business coordinate fix**: Found 10 entries >20km from their town center due to Census Geocoder matching chain business names (Dollar General, Advance Auto Parts, Bangor Savings Bank, Dead River Company, Katahdin Trust Company, United Baptist Church, F.A. Peabody Insurance, Circle K, H&R Block) to the wrong town's branch. All 10 fixed via Nominatim with full address+ZIP queries.
- **18 cannabis dispensaries added**: Lincoln (5), Presque Isle (5), Caribou (2), Houlton (4), Millinocket (2), Howland (1). All geocoded via Nominatim — 17/18 building-level, 1 town center (Brothers Cannabis).
- **Email crawl**: 28 legitimate emails found (+15%, from 208 to 236). 240 websites crawled; garbage emails filtered (telephonedirectories.us, noaa.gov, yandex.ru, etc.)
- **Phone number search**: 51 phones found across 2 passes (+5%)
- **DuckDuckGo website harvest**: 245 new websites applied (466→711, +52%, later ~128 bad entries purged to 587)
- **3 missing addresses found**: Cigaret Shopper (64 North St, Houlton), Serendipitous Dragonfly (79 Main St, Houlton), Smith Bros. Plumbing & Heating (32 High St, Houlton) — all geocoded via Nominatim, all three now have building-level coordinates
- **Map features**: Category filter, extended search (name/address/town/category), active filter badges with dismiss, category color dots in Browse list, suitable-for-ads default filter, notes/visits/routes (localStorage), export/import, reset button, console diagnostics
- **Category SVG icons**: Markers now show category-specific SVG icons (building, cup, bag, heart, wrench, home, star) inside the colored circle
- **Voice search**: Microphone button in search bar uses Web Speech API (webkitSpeechRecognition). Shows listening indicator, populates search on result. Pressing 🎤 while listening stops recording. `rec.stop()` called on result + 10s safety timeout prevents mic from staying on indefinitely
- **Auto-geolocate**: On page load, checks `navigator.permissions` — if geolocation was previously granted, auto-locates and adds user marker without user action
- **Route planner upgrades**: "📍 Navigate" button launches native maps in turn-by-turn navigation mode — Apple Maps `dirflg=d` (iOS), Google Maps `dir_action=navigate` (Android) — with all stops as waypoints. Per-stop driving distances/times from OSRM shown inline in route list (falls back to Haversine straight-line before optimization).
- **OSRM bug fix**: `coordsStr` variable was undefined in `optimizeRoute()` — OSRM calls silently failed. Added missing coordinate string construction.
- **Voice search mic safety**: Added `rec.stop()` on result + 10s `AbortController`-style safety timeout so microphone never stays on indefinitely.
- **Smart default zoom**: Initial zoom increased to 9 (from 8), plus `fitBounds` on first data load for tighter auto-fit
- **Smooth bottom sheet**: GPU-accelerated `transform: translateY()` instead of `height` for 60fps on iOS/Android. Real-time finger-following during swipe with rubber-band resistance. Computes target position dynamically from CSS classes — works on all screen sizes.
- **Data sanity audit**: Systematic check of all 1142 entries. Fixed 5 corrupted emails (phone/data fused into email fields), 2 wrong ZIP codes, removed 3 duplicates (BigRock Mountain/Old Post Cafe/Clark's Auto Sales Linneus), renamed Howland-Enfield FCU → The County FCU - Howland (5 years out of date), updated Handy Stop address to 2 Coffin St
- **Mobile UX improvements (Tier 1)**: Touch targets bumped to WCAG-friendly sizes (header buttons 40px, sidebar tabs 10×8px, drag handle 8px). `prefers-reduced-motion` media query disables bottom sheet animation for vestibular disorders.
- **Mobile UX improvements (Tier 2)**: 150ms debounce on browse list search + 150ms debounce on filter dropdown changes — prevents redundant 863-row rebuilds. Marker tap now shows detail pane in bottom sheet instead of route tab. OSRM fetch has 10s AbortController timeout. Loading spinner shown on initial page load.
- **Mobile UX improvements (Tier 3)**: Filters scroll horizontally on ≤480px screens at 10px font. Legend moved to top-right on mobile (no longer overlaps map center). Full-screen map toggle button hides header/filters/sidebar. Leaflet popup constrained to 75vw on mobile.
- **Filter state persistence**: Selected region/town/category/search/sort saved to localStorage, restored on page reload.
- **Detail pane UX**: Auto-scrolls sidebar content to top on tab switch. Closing detail auto-collapses bottom sheet to peek. Swipe-right gesture on detail pane goes back to browse list.
- **Bug fix pass (Jun 23, 2026)**: Fixed toast() undefined (voice search), notes localStorage key typo (coffeNews_notes→coffeeNews_notes) with legacy migration, geolocate crash (addUserLocationMarker, permissions guards, GEO_OPTS), navigateBtn stuck disabled after OSRM (re-enabled in .then/.catch), QuotaExceededError handling (toast on setItem failure). Added global error boundary (window.onerror/unhandledrejection → toast). Fixed startup ordering (loadSavedData before initMap). Added .gitignore.
- **Category filter grouped into 8 legend groups**: Replaced ~30 raw category options with 8 broad groups matching the map legend. Retail/Gift/Hardware kept as its own group (orange) since Cannabis Dispensary and similar businesses use that color.
- **UX improvement batch (Jun 23, 2026)**: 8 improvements in one pass:
  - **Location remnants removed**: Nearest sort, distance column, "X miles from you" text, route origin param, dead userLat/userLng vars all cleaned up
  - **Copy address/phone**: 📋 clipboard buttons in detail pane with HTTP fallback (prompt)
  - **Delete confirmation**: confirm() dialogs before note/visit deletion
  - **Filter count badges**: (N) counts on quick-filter pills + region/town/category dropdown options, updated on every filter change
  - **Phone search**: getFilteredBusinesses now matches against phone digits (strip non-numeric)
  - **OSRM retry**: fetchWithRetry wrapper (2 retries, 1s delay), keeps current stop order on total failure
  - **Offline banner**: red bar at top toggled by navigator.onLine + online/offline events
  - **Follow-up dates**: date input in note editor (detail pane + notes tab), ⏰ Follow-ups filter button in Notes tab, sorted by follow-up date ascending
  - **4 regional CSVs**: 📥 CSV header button with dropdown menu, one download per region, proper UTF-8 BOM + CSV escaping
- **Sticky hover fix (touch devices)**: All 18 `:hover` CSS rules wrapped in `@media (hover: hover)`, plus global `-webkit-tap-highlight-color: transparent` to prevent iOS Safari persistent gray tap highlight on buttons/tabs/list rows
- **Quick-filter pills removed**: Category dropdown is the sole business-type filter. Removed HTML/CSS/JS for the 9 quick-filter pills (All · Food · Shopping · Health · Auto · Services · Lodging · Religion). Simplified filter UI — Region/Town/Category/Search/Reset in top bar.
- **Filter popover on mobile**: Filter controls hide behind a "🔍 Filter" button on both portrait mobile and landscape. Tapping shows a popover below the header. Desktop (width > 700px) keeps filters visible inline as before.
- **Header buttons moved to left**: 📋 List, 📍 Route, 📝 Notes, 🔍 Filter, 📥 CSV now sit between the title and the filter bar on the left side of the header.
- **Preloaded routes**: 📋 Preloaded Routes section in Route tab with 24 per-town routes (all suitable-for-ads businesses sorted by distance from town center, closest first) and 5 cross-town corridor routes (top 5 per town). One-tap load, no manual route building needed.
- **Leg distances in route list**: Each stop shows distance from previous stop (~straight-line by default, actual driving distance/time after Optimize). Lets salesperson decide if an outlier stop is worth the drive.
- **Landscape UX overhaul**: 4 improvements for horizontal phone use:
  - **Right-side panel**: Sidebar switches from bottom sheet to a right-side panel (45vw, max 340px) in landscape, so map and sidebar are visible simultaneously
  - **Collapsed filter popover**: Filter controls hide behind a single "🔍 Filter" button; tapping it shows a popover below the header with all dropdowns
  - **Compact sidebar**: No full-screen overlay — sidebar stays at 45vw leaving 55vw for the map
  - **Auto-hide header**: Header auto-hides after 3s idle in landscape, reappears on any tap/touch

---

## Smartphone Cross-Compatibility — Fixes Applied (Jun 23, 2026)

All known cross-compatibility issues resolved in a single sweep. See Completed Work below for full details.

| Issue | Fix | Status |
|---|---|---|
| Bottom sheet drag stutter | Changed `.sidebar-tabs` `touch-action: none` → `pan-y` to avoid Leaflet handler conflict | ✅ |
| Bottom sheet snap position drift | Dynamic `getBoundingClientRect()` + `--safe-bottom` padding | ✅ |
| Map tap vs bottom sheet tap | Added `.leaflet-marker-icon`/`.leaflet-popup` guards in click-outside; button/input/select guards in drag handler | ✅ |
| Voice search mic icon stuck | `isListening` set before `rec.start()`; try/catch guards; Samsung Internet `onend` race handled | ✅ |
| Filter dropdowns clipped (landscape) | Form font-sizes 8px→11px; `overflow-y:visible` on `#filters` | ✅ |
| Full-screen map exit button overlap | Moved from `top:8px` to `bottom:16px + var(--safe-bottom)` | ✅ |
| PWA add-to-home-screen splash | Generated PNG icons (180, 192, 512) via Pillow; manifest refs updated | ✅ |
| Safari zoom on input focus | `@supports -webkit-touch-callout` forces `font-size: 16px !important` on inputs | ✅ |
| Print route layout | Populate `.print-route-table` with stops + leg distances before `window.print()` | ✅ |

---

## Remaining Work

1. **5 businesses missing phone numbers** (web search exhaustive): Dollar General Fort Fairfield (non-207 number rejected), Lowell Baptist Church, Bittersweet Thyme, Bittersweet Thyme Cafe, Anciently Marked Tattoo Art Studio. Resolvable only by phone call or in-person visit.
2. **Email research**: 197/1141 (17.3%). Further improvement requires phone calls.
3. **Website research**: 587/1141 (51.4%). Remaining ~554 likely don't maintain a web presence.
4. **Wendy's Houlton**: Permitted Jul 2025, not yet open as of Jun 2026. Monitor periodically.
5. **363 road/town-level geocodes**: ~1-2km precision on rural routes. Most address queries already exhausted. ~92 of these are town-center fallbacks (~1-2km spread). Further precision requires manual coordinate placement.
6. **Brothers Cannabis Lincoln**: Coordinates are at town center (Nominatim couldn't resolve "Unit 2" in address). Needs manual building-level placement.
7. **Churches currently excluded** from suitable-for-ads (client requested). Confirm this is still desired.
8. **Chain naming normalization**: NAPA (4 variants), Dunkin' Donuts → Dunkin' (2 entries still use old name), Circle K naming inconsistencies (7+ variants across 16 locations).
9. **Tile error handling**: Show fallback when map tiles fail to load.
10. **Route auto-save**: Automatically save route as named entry on creation.
