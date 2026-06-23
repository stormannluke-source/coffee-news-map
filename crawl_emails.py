import json, re, time, requests

EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
RATE_DELAY = 0.5
SAVE_EVERY = 20
CONNECT_TIMEOUT = 3.1
READ_TIMEOUT = 5.0

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})
session.max_redirects = 3

SKIP_DOMAINS = {
    'sentry-next.wixpress.com', 'sentry.wixpress.com', 'wixpress.com',
    'your@email.com',
}

def fetch(url):
    if not url.startswith('http'):
        url = 'https://' + url
    try:
        resp = session.get(url, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        return resp.text
    except:
        pass
    return None

def extract_emails(html, domain=''):
    if not html:
        return set()
    found = set()
    bad_exts = ('.png', '.jpg', '.gif', '.css', '.js', '.svg', '.ico', '.woff', '.webp', '.avif')
    skip_keywords = ('example', 'domain', 'your@', 'sentry-', 'sentry.')
    for m in EMAIL_RE.finditer(html):
        e = m.group(0).lower().strip().rstrip('.')
        if any(e.endswith(ext) for ext in bad_exts):
            continue
        if any(k in e for k in skip_keywords):
            continue
        if e in SKIP_DOMAINS:
            continue
        found.add(e)

    # If the only email found is generic (domain-based catch-all), skip it
    filtered = {e for e in found if domain not in e.split('@')[1] or len(found) <= 2}
    return filtered or found

with open('cleaned/all_businesses.json') as f:
    businesses = json.load(f)

candidates = [(i, b) for i, b in enumerate(businesses)
              if b.get('website', '').strip() and not b.get('email', '').strip()]

total = len(candidates)
print(f'Crawling {total} websites for emails...')

results = {}
try:
    with open('email_crawl_progress.json') as f:
        results = json.load(f)
    print(f'Resuming from {len(results)} previously crawled')
except:
    pass

already_done = set(results.keys())
crawled_cnt = 0
found_cnt = sum(1 for v in results.values() if v)

for idx, (biz_idx, biz) in enumerate(candidates):
    key = biz['key']
    if key in already_done:
        continue

    url = biz['website']
    name = biz['name']
    html = fetch(url)
    emails = extract_emails(html) if html else set()

    results[key] = list(emails) if emails else []
    if emails:
        found_cnt += 1
        print(f'  ✓ {name[:35]:35s} | {list(emails)[0]}', flush=True)
    else:
        print(f'  ... {name[:35]:35s} | no email', flush=True)

    crawled_cnt = len([v for v in results.values() if v is not None])
    if crawled_cnt % SAVE_EVERY == 0 and crawled_cnt > 0:
        with open('email_crawl_progress.json', 'w') as f:
            json.dump(results, f, indent=2)
        print(f'  [saved: {crawled_cnt} crawled, {found_cnt} found]', flush=True)

    time.sleep(RATE_DELAY)

with open('email_crawl_progress.json', 'w') as f:
    json.dump(results, f, indent=2)

total_found = sum(1 for v in results.values() if v)
total_emails = sum(len(v) for v in results.values())
print(f'\n=== DONE ===')
print(f'Crawled: {len(results)}')
print(f'Businesses with email found: {total_found}')
print(f'Total emails collected: {total_emails}')
