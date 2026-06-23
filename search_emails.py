import csv, re, time, sys, json, urllib.parse
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

def search_duckduckgo(query):
    url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}'
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        results = []
        for a in soup.select('a.result__a'):
            href = a.get('href', '')
            text = a.get_text(strip=True)
            results.append({'title': text, 'url': href})
        snippets = []
        for s in soup.select('.result__snippet'):
            snippets.append(s.get_text(strip=True))
        return results, snippets
    except Exception as e:
        return [], []

def extract_email_from_url(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        emails = EMAIL_RE.findall(r.text)
        # Filter out common false positives
        valid = []
        for e in emails:
            e = e.lower().strip()
            if any(ext in e for ext in ['.png', '.jpg', '.gif', '.css', '.js', '.svg', '.ico']):
                continue
            if e.startswith('@') or e.endswith('.'):
                continue
            if 'example' in e or 'domain' in e:
                continue
            valid.append(e)
        return valid
    except:
        return []

def main():
    businesses = []
    with open('/home/square1/Desktop/Coffee News/cleaned/houlton_region.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            businesses.append(row)
    
    results = {}
    total = len(businesses)
    
    for i, biz in enumerate(businesses):
        name = biz['Business Name'].strip()
        city = biz['City'].strip()
        current_email = biz.get('Email', '').strip()
        
        if current_email:
            continue
        
        query = f'{name} {city} Maine email'
        print(f'[{i+1}/{total}] Searching: {name} ({city})')
        
        links, snippets = search_duckduckgo(query)
        
        all_text = ' '.join(snippets)
        for link in links:
            all_text += ' ' + link['title']
        
        # Also fetch the first result page if it looks like a business website
        emails_found = set()
        for match in EMAIL_RE.findall(all_text):
            e = match.lower().strip()
            if any(ext in e for ext in ['.png', '.jpg', '.gif', '.css', '.js', '.svg', '.ico', '.woff', '.ttf']):
                continue
            if e.startswith('@') or e.endswith('.') or 'example' in e:
                continue
            emails_found.add(e)
        
        # Try to fetch the first result
        if links and not emails_found:
            first_url = links[0]['url']
            if 'duckduckgo' not in first_url and 'google' not in first_url:
                time.sleep(0.5)
                page_emails = extract_email_from_url(first_url)
                for e in page_emails:
                    emails_found.add(e)
        
        if emails_found:
            results[name] = list(emails_found)
            print(f'  -> FOUND: {", ".join(emails_found)}')
        else:
            results[name] = []
            print(f'  -> NOT FOUND')
        
        time.sleep(1)  # Rate limiting
    
    # Save results
    with open('email_search_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f'\nDone! Found {sum(1 for v in results.values() if v)} emails out of {len(results)} searched.')
    
    # Summary of found emails
    print('\n=== RESULTS ===')
    for name, emails in results.items():
        if emails:
            print(f'{name}: {emails[0]}')
        else:
            print(f'{name}: NOT FOUND')

if __name__ == '__main__':
    main()
