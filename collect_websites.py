import csv
import json
import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from ddgs import DDGS

OUTPUT_FILE = "website_findings.json"
PROGRESS_FILE = "website_progress.json"

SKIP_DOMAINS = {
    "facebook.com", "yelp.com", "bbb.org", "yellowpages.com",
    "mapquest.com", "foursquare.com", "twitter.com", "instagram.com",
    "linkedin.com", "pinterest.com", "tripadvisor.com",
    "manta.com", "hotfrog.com", "cylex.us.com", "chamberofcommerce.com",
    "superpages.com", "whitepages.com", "merchantcircle.com",
    "birdeye.com", "telephonedirectories.us", "allbiz.com",
    "archive.org", "web.archive.org",
}

CONTACT_PATHS = ["/contact", "/contact-us", "/about", "/about-us", "/contactus"]

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
})

def clean_url(url):
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    path = parsed.path.rstrip("/")
    return f"https://{domain}{path}"

def is_skip_domain(url):
    try:
        domain = urlparse(url).netloc.lower()
        for skip in SKIP_DOMAINS:
            if skip in domain:
                return True
        return False
    except:
        return True

def is_directory_site(url):
    bad_terms = ["reviews.", "directory.", "yellowpages", "superpages",
                 "merchantcircle", "chamberofcommerce", "manta", "hotfrog",
                 "cylex", "birdeye", "allbiz", "telephonedirectories"]
    domain = urlparse(url).netloc.lower()
    for t in bad_terms:
        if t in domain:
            return True
    return False

def extract_emails(html):
    emails = set()
    soup = BeautifulSoup(html, 'html.parser')
    for a in soup.find_all('a', href=re.compile(r'mailto:', re.I)):
        email = a['href'].replace('mailto:', '').split('?')[0].strip()
        if '@' in email and '.' in email.split('@')[1]:
            emails.add(email.lower())
    text = soup.get_text()
    found = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    for e in found:
        e = e.lower()
        domain = e.split('@')[1]
        if any(domain.endswith(ext) for ext in ['.png', '.jpg', '.gif', '.svg', '.css', '.js']):
            continue
        if 'example' in domain or 'domain' in domain:
            continue
        if 'noreply' in e or 'no-reply' in e or 'donotreply' in e:
            continue
        emails.add(e)
    bad = {"", "email@example.com", "test@test.com", "info@example.com", "webmaster@example.com"}
    return {e for e in emails if e not in bad}

def fetch(url, timeout=15):
    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True)
        if resp.status_code == 200 and resp.text:
            return resp.text
        return None
    except:
        return None

def find_with_phone(name, phone, town):
    result = {"website": "", "emails": [], "source": ""}
    if not phone:
        return result

    digits = re.sub(r'[^\d]', '', phone)
    if len(digits) < 7:
        return result

    query = f'"{phone}" Maine'
    try:
        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=10))
    except:
        return result

    for r in results:
        url = r.get('href', '')
        if not url or is_skip_domain(url) or is_directory_site(url):
            continue
        if url.endswith('.pdf') or url.endswith('.doc') or url.endswith('.docx'):
            continue

        html = fetch(url)
        if not html:
            continue

        name_words = set(name.lower().split())
        town_lower = town.lower()
        page_text = html.lower()
        name_in_page = any(w in page_text for w in name_words) if name_words else True
        town_in_page = town_lower in page_text if town_lower else True
        phone_in_page = digits in re.sub(r'[^\d]', '', page_text) if len(digits) >= 7 else False

        if not name_in_page and not phone_in_page:
            continue

        emails = extract_emails(html)
        result["website"] = url
        result["emails"] = sorted(emails)
        result["source"] = "phone_search"
        return result

    return result

def find_with_name(name, town):
    result = {"website": "", "emails": [], "source": ""}
    name_short = re.sub(r'\s+', ' ', name.strip())[:40]
    query = f'"{name_short}" "{town}" Maine -realty -realtor -zillow -craigslist'
    try:
        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=10))
    except:
        return result

    fb_url = ""
    for r in results:
        url = r.get('href', '')
        if not url:
            continue
        if is_directory_site(url):
            continue
        if is_skip_domain(url):
            if 'facebook.com' in url and not fb_url:
                fb_url = url
            continue
        if url.endswith('.pdf'):
            continue

        html = fetch(url)
        if not html:
            continue

        name_words = set(name.lower().split())
        town_lower = town.lower()
        page_text = html.lower()
        name_in_page = any(w in page_text for w in name_words) if name_words else True
        town_in_page = town_lower in page_text if town_lower else True

        if not name_in_page and not town_in_page:
            continue

        emails = extract_emails(html)

        for path in CONTACT_PATHS:
            contact_url = urljoin(url.rstrip('/') + '/', path.lstrip('/'))
            contact_html = fetch(contact_url)
            if contact_html:
                more_emails = extract_emails(contact_html)
                emails.update(more_emails)

        result["website"] = url
        result["emails"] = sorted(emails)
        result["source"] = "name_search"
        return result

    if fb_url:
        result["website"] = fb_url
        result["source"] = "facebook"

    return result

def find_website_and_email(name, phone, town):
    result = find_with_phone(name, phone, town)
    if result["website"]:
        return result
    return find_with_name(name, town)

def main():
    all_biz = []
    for region in ['presque_isle_area', 'houlton_region', 'millinocket_area', 'lincoln_area']:
        fp = f'cleaned/{region}.csv'
        with open(fp, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                row['Region'] = region
                all_biz.append(row)

    print(f"Total businesses: {len(all_biz)}")

    progress = load_progress()
    findings = {}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE) as f:
            findings = json.load(f)

    todo = []
    for b in all_biz:
        key = f"{normalize_name(b['Business Name'])}|{normalize_name(b['Town'])}"
        has_email = bool(b.get('Email', '').strip())
        has_website = bool(b.get('Website', '').strip())
        if has_email and has_website:
            continue
        todo.append((key, b['Business Name'], b.get('Phone', ''), b['Town'], b['Region']))

    print(f"Need research: {len(todo)}")

    for i, (key, name, phone, town, region) in enumerate(todo):
        if key in progress and progress[key].get("done"):
            if key not in findings:
                findings[key] = progress[key].get("finding", {})
            continue

        print(f"[{i+1}/{len(todo)}] {name} | {town}")

        result = find_website_and_email(name, phone, town)
        time.sleep(1.5)

        if result["emails"] or result["website"]:
            findings[key] = result
            if result["website"]:
                print(f"  -> {result['website']}")
            if result["emails"]:
                print(f"  -> {result['emails']}")

        with open(OUTPUT_FILE, 'w') as f:
            json.dump(findings, f, indent=2)

        progress[key] = {"done": True, "finding": result}
        save_progress(progress)

    total = len(findings)
    ws = sum(1 for v in findings.values() if v.get("website"))
    em = sum(1 for v in findings.values() if v.get("emails"))
    print(f"\nDone! {total} findings: {ws} websites, {em} new emails")

def normalize_name(name):
    n = name.lower().strip()
    n = re.sub(r'[^a-z0-9\s]', '', n)
    return re.sub(r'\s+', ' ', n).strip()

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {}

def save_progress(p):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(p, f, indent=2)

if __name__ == '__main__':
    main()
