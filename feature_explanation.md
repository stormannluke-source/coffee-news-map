# Coffee News Business Directory — Feature Overview

## Notes on Businesses

Each business on the map can have a **personal note** attached. This is useful for:

- Recording notes from a site visit ("Spoke with owner Jane, interested in September ad")
- Tracking contact preferences ("Prefers email over phone")
- Noting follow-up actions ("Call back about menu change")
- Any other notes you want to associate with a specific business

**How it works:**
- Click a business marker → the popup shows a **Note** section with any existing note
- Add or edit the note inline — it saves automatically to your browser's local storage
- Businesses with notes show a small **dot indicator** on their marker so you can spot them on the map
- The **Notes Log** tab lists all businesses that have notes, with their content
- Notes persist across browser restarts — they're stored on your computer
- Notes can be **exported as a JSON file** for backup or to transfer to another computer

---

## Visit Tracking

You can **mark businesses as visited** and record when you visited them.

**How it works:**
- Click "Mark Visited" on a business popup → the date is recorded
- A second click marks it as visited again with a new date
- Previously visited businesses show a **checkmark indicator** on their marker
- The **Visit Log** tab shows your visit history sorted by date (most recent first)
- Visit data is stored locally in your browser
- Can be exported/imported alongside notes

---

## Route Planning

The map includes a full **route planner** for planning driving routes between businesses.

**How it works:**
- **Add stops**: Click any business marker to add it to your route
- **Reorder**: Drag and drop stops in the route list to reorder them
- **Optimize**: Click "Optimize Route" to automatically reorder stops in the most efficient driving order
- **Directions**: Shows distance and estimated drive time for each leg of the trip
- **Map view**: The route draws as a blue line on the map; numbered markers show stop order
- **Print**: Print a route sheet with turn-by-turn information

### Saved Routes

Routes can be **saved and reloaded** later.

- **Save**: Give your route a name and save it
- **Load**: Pick from a list of previously saved routes
- **Delete**: Remove routes you no longer need
- **Export**: Download all saved routes as a JSON file
- **Import**: Restore routes from a previously exported file
- All saved routes are stored in your browser's local storage

### Regular / Frequently Used Routes

For routes you drive repeatedly (e.g., "Monday breakfast delivery run", "Weekly church circuit"):
- Save the route once with a descriptive name
- Load it at the start of each trip
- Stops can be reordered or removed as needed for that day without affecting the saved version

### Route Planning Tips

- **Start from anywhere**: Click your current location on the map, then add businesses in the order that makes sense
- **Use with filters**: Filter by region or town, then add businesses from the filtered view to build targeted routes
- **Combine with notes**: If you have notes about specific businesses (e.g., "Prefers morning visits"), use the Notes Log to plan your stop order

---

## Data Privacy

- **Everything stays on your computer**: Notes, visit history, and saved routes are stored in your browser's local storage
- **No account needed**: No sign-up, no passwords, no server
- **No data sent anywhere**: Your notes are never transmitted over the internet
- **Backup/Transfer**: Use the Export button to download all your data as a JSON file. Import on another computer to pick up where you left off.
- **Clearing browser data will erase it**: If you clear your browser's cache/storage, your notes and saved routes will be lost. Always export before clearing.

---

## File Structure

| File | Purpose |
|---|---|
| `index.html` | The map application — open this file in a browser |
| `feature_explanation.md` | This document |
| `cleaned/all_businesses.json` | Business directory data (regenerated from CSVs) |
| `coordinates.json` | Geocoded coordinates for each business |
| `cleaned/*.csv` | Regional business lists (source data) |

The map is a **self-contained HTML file** — no server required. Just double-click `index.html` to open it.
