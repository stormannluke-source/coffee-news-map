import json, re, time, requests, urllib.parse
from bs4 import BeautifulSoup

PHONE_RE = re.compile(r'(?:\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})')
RATE_DELAY = 1.0

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

def search_ddg(query):
    try:
        r = session.get('https://html.duckduckgo.com/html/', params={'q': query}, timeout=5)
        return r.text
    except:
        return ''

def fetch_page(url):
    try:
        r = session.get(url, timeout=(3, 5))
        return r.text
    except:
        return ''

def extract_207_phones(text):
    phones = set()
    for m in PHONE_RE.finditer(text):
        p = m.group(0).strip()
        digits = re.sub(r'\D', '', p)
        if len(digits) == 10 and digits.startswith('207'):
            formatted = f'({digits[:3]}) {digits[3:6]}-{digits[6:]}'
            phones.add(formatted)
    return phones

def get_top_links(html, n=3):
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for a in soup.select('a.result__a'):
        href = a.get('href', '')
        if href and not any(s in href for s in ['duckduckgo', 'google.com', 'youtube.com', 'facebook.com']):
            links.append(href)
    return links[:n]

with open('cleaned/all_businesses.json') as f:
    bizs = json.load(f)

missing = [b for b in bizs if not b.get('phone', '').strip()]
print(f'Searching {len(missing)} businesses...')

results = {}
for i, biz in enumerate(missing):
    name = biz['name']
    town = biz.get('town', '') or biz.get('city', '')
    phones = set()

    # Search DDG, extract 207 numbers from snippets
    html = search_ddg(f'"{name}" {town} Maine phone')
    phones.update(extract_207_phones(html))

    # If none, fetch top result pages
    if not phones:
        links = get_top_links(html)
        for link in links:
            page = fetch_page(link)
            phones.update(extract_207_phones(page))
            if phones:
                break
            time.sleep(0.5)

    if phones:
        best = list(phones)[0]
        results[biz['key']] = best
        print(f'  ✓ {name[:35]:35s} | {best}', flush=True)
    else:
        print(f'  ... {name[:35]:35s} | no phone found', flush=True)

    time.sleep(RATE_DELAY)

with open('phone_search_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f'\nFound: {len(results)}/{len(missing)}')
