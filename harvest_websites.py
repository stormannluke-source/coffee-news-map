import csv, json, os, re, time
from ddgs import DDGS

PROGRESS_FILE = "website_progress.json"
FINDINGS_FILE = "website_findings.json"

SKIP_DOMAINS = {
    "facebook.com", "yelp.com", "bbb.org", "yellowpages.com", "whitepages.com",
    "mapquest.com", "foursquare.com", "twitter.com", "instagram.com",
    "linkedin.com", "pinterest.com", "tripadvisor.com", "manta.com",
    "hotfrog.com", "chamberofcommerce.com", "superpages.com",
    "merchantcircle.com", "birdeye.com", "cylex.us.com",
    "archive.org", "web.archive.org", "zmenu.com", "menutoeat.com",
    "restaurantguru.com", "restaurantji.com", "hoursmap.com",
    "usaypage.com", "phonelookup.com", "claritycheck.com",
    "npino.com", "ibegin.com", "city-data.com",
    "sicbase.com", "bizapedia.com", "411.info",
    "openingtimes.co", "allstays.com", "medicarelist.com",
    "locatefamily.com", "usbanklocations.com",
}

def is_good_url(url):
    if not url:
        return False
    domain = re.search(r'https?://([^/]+)', url)
    if not domain:
        return False
    domain = domain.group(1).lower()
    for skip in SKIP_DOMAINS:
        if skip in domain:
            return False
    return True

def search_quick(name, town, phone):
    result = {"website": "", "emails": [], "source": ""}
    
    digits = re.sub(r'[^\d]', '', phone)
    
    # Phase 1: phone search
    if len(digits) >= 10:
        try:
            ddgs = DDGS()
            for r in ddgs.text(f'"{phone}" Maine', max_results=5):
                url = r.get('href', '')
                if is_good_url(url) and not url.endswith('.pdf'):
                    result["website"] = url
                    result["source"] = "phone"
                    return result
        except:
            pass
    
    # Phase 2: name + town
    try:
        ddgs = DDGS()
        q = f'"{name[:40]}" "{town}" Maine'
        for r in ddgs.text(q, max_results=8):
            url = r.get('href', '')
            if 'facebook.com' in url:
                continue
            if is_good_url(url) and not url.endswith('.pdf'):
                result["website"] = url
                result["source"] = "name"
                return result
    except:
        pass
    
    return result

def normalize_key(name, town):
    n = re.sub(r'[^a-z0-9\s]', '', name.lower().strip())
    n = re.sub(r'\s+', ' ', n).strip()
    t = re.sub(r'[^a-z0-9\s]', '', town.lower().strip())
    t = re.sub(r'\s+', ' ', t).strip()
    return f"{n}|{t}"

def main():
    # Load all businesses from CSVs
    all_biz = []
    for region in ['presque_isle_area', 'caribou_limestone', 'houlton_region', 'millinocket_area', 'lincoln_area']:
        fp = f'cleaned/{region}.csv'
        with open(fp, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                row['region_file'] = region
                all_biz.append(row)
    
    print(f"Total businesses: {len(all_biz)}")
    
    progress = {}
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            progress = json.load(f)
    
    findings = {}
    if os.path.exists(FINDINGS_FILE):
        with open(FINDINGS_FILE) as f:
            findings = json.load(f)
    
    # Build todo list (only missing website or email, not already done)
    todo = []
    for b in all_biz:
        key = normalize_key(b['Business Name'], b['Town'])
        has_website = bool(b.get('Website', '').strip())
        has_email = bool(b.get('Email', '').strip())
        if has_website and has_email:
            continue
        if key in progress and progress[key].get("done"):
            continue
        todo.append((key, b['Business Name'], b.get('Phone', ''), b['Town'], b['region_file']))
    
    print(f"Need research: {len(todo)} (already done: {len(progress)})")
    
    for i, (key, name, phone, town, region) in enumerate(todo):
        print(f"[{i+1}/{len(todo)}] {name} | {town}")
        
        result = search_quick(name, town, phone)
        
        if result["website"]:
            print(f"  -> {result['website']}")
            findings[key] = result
        
        progress[key] = {"done": True, "finding": result}
        
        if (i+1) % 50 == 0:
            with open(FINDINGS_FILE, 'w') as f:
                json.dump(findings, f, indent=2)
            with open(PROGRESS_FILE, 'w') as f:
                json.dump(progress, f, indent=2)
            print(f"  Saved progress ({i+1}/{len(todo)})")
        
        time.sleep(1.0)
    
    with open(FINDINGS_FILE, 'w') as f:
        json.dump(findings, f, indent=2)
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)
    
    total_found = sum(1 for v in findings.values() if v.get('website'))
    print(f"\nDone! {total_found} websites found out of {len(todo)} searched")

if __name__ == '__main__':
    main()
