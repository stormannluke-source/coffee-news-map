import csv
import json
import re

EMAIL_UPDATES = {
    "s.w. collins co.|caribou": "marketing@swcollins.com",
    "caribou country club|caribou": "proshop@caribougolf.com",
    "caribou area chamber of commerce|caribou": "ccac@cariboumaine.net",
    "nylander museum|caribou": "info@cariboumaine.org",
    "caribou recreation department|caribou": "gmarquis@cariboumaine.org",
    "mike's family market|limestone": "info@aroostookonline.com",
    "loring development authority|limestone": "LDA@Loring.org",
    "limestone community school|limestone": "blothrop@lcseagles.org",
    "maine school of science and mathematics|limestone": "admissions@mssm.org",
    "presque isle animal hospital|presque isle": "piah@piah.biz",
    "aroostook mall|presque isle": "management@aroostookcentremall.com",
    "university of maine at presque isle (umpi)|presque isle": "umpi-admissions@maine.edu",
    "bigrock mountain|mars hill": "info@bigrockmaine.com",
    "fort fairfield town office|fort fairfield": "ahuotari@fortfairfield.org",
    "fort fairfield public library|fort fairfield": "library@fortfairfield.org",
    "the county federal credit union|fort fairfield": "stacy.edgecomb@countyfcu.org",
    "katahdin trust company|ashland": "customerservice@katahdintrust.com",
    "millinocket regional hospital|millinocket": "info@mrhme.org",
    "katahdin chamber of commerce|millinocket": "members@katahdinmaine.com",
    "millinocket memorial library|millinocket": "info@millinocketlib.org",
    "hillcrest golf club|millinocket": "golfhillcrest@hotmail.com",
    "new england outdoor center|millinocket": "info@neoc.com",
    "baxter park inn|millinocket": "stay@baxterparkinn.com",
    "eastmill federal credit union|east millinocket": "info@eastmillfcu.org",
    "patten lumbermen's museum|patten": "curator@lumbermensmuseum.org",
    "katahdin area trails|millinocket": "info@katahdinareatrails.org",
    "shin pond village|shin pond": "reserve@shinpond.com",
    "mt. chase lodge|mount chase": "info@mtchaselodge.com",
    "lincoln regional veterinary hospital|lincoln": "lrvhinfo@gmail.com",
    "penobscot valley hospital|lincoln": "info@pvhme.org",
    "bangor savings bank|lincoln": "bangorsupport@bangor.com",
    "lincoln news|lincoln": "news@lincnews.com",
    "town of lincoln|lincoln": "awoodard@lincolnmaine.org",
    "howland-enfield federal credit union|howland": "info@howlandenfieldfcu.com",
    "houlton community golf club|houlton": "houltongolf@gmail.com",
    "temple theater|houlton": "movies@templehoulton.com",
    "shiretown inn and suites|houlton": "info@shiretowninnandsuites.com",
    "pioneer broadband|houlton": "sales@pioneerbroadband.net",
    "houlton water company|houlton": "sherman@hwco.org",
    "region 2 school of applied technology|houlton": "alondon@regiontwo.org",
    "town of houlton|houlton": "town.clerk@houlton-maine.com",
    "houlton band of maliseet indians|littleton": "tribal.courts@maliseets.com",
    "jerry's food store / jerry's thriftway|island falls": "jerrysfoodstore848@hotmail.com",
    "island falls animal health clinic|island falls": "IFAHC@protonmail.com",
    "birch point campground & cottages|island falls": "edpoint@pivot.net",
    "katahdin federal credit union|island falls": "info@katahdinfcu.org",
    "houlton community golf course|new limerick": "houltongolf@gmail.com",
    "katahdin trust company|presque isle": "customerservice@katahdintrust.com",
    "katahdin trust co.|limestone": "customerservice@katahdintrust.com",
    "katahdin trust co.|houlton": "customerservice@katahdintrust.com",
    "katahdin trust company|oakfield": "customerservice@katahdintrust.com",
    "katahdin trust company|patten": "customerservice@katahdintrust.com",
    "katahdin trust company|caribou": "customerservice@katahdintrust.com",
    "fort fairfield utilities district|fort fairfield": "bparker@ffud.org",

    # === Presque Isle Area new research (June 2026) ===
    "carroll's auto sales (chevrolet/gmc)|presque isle": "sales@carrollsautosales.com",
    "northern maine motors|presque isle": "ryan@northernmainemotors.com",
    "hampton inn presque isle|presque isle": "PQIMA_hampton@hilton.com",
    "the northeastland hotel|presque isle": "rooms@thenortheastlandhotel.com",
    "aroostook county federal savings and loan|presque isle": "customerservice@yourhomebank.com",
    "gram russo's italian restaurant|presque isle": "cicc3733@aol.com",
    "graves' shop 'n save|presque isle": "penny.leblanc@delhaize.com",
    "s.w. collins co.|presque isle": "marketing@swcollins.com",

    # === Caribou/Limestone new research (June 2026) ===
    "best western caribou inn|caribou": "info@caribouinn.com",
    "caribou inn & convention center|caribou": "info@caribouinn.com",
    "caribou fire department|caribou": "firechief@cariboumaine.org",
    "caribou florist & greenhouse|caribou": "noyesflowers@gmail.com",
    "caribou police department|caribou": "policechief@cariboumaine.org",
    "caribou public library|caribou": "librarydirector@cariboumaine.org",
    "caribou theater|caribou": "cariboutheatres@yahoo.com",
    "the caribou theater|caribou": "cariboutheatres@yahoo.com",
    "caribou town office|caribou": "dbrissette@cariboumaine.org",
    "greenhouse restaurant|caribou": "info@caribouinn.com",
    "highway tire inc.|caribou": "highwaytireandauto@gmail.com",
    "lancaster-morgan funeral home|caribou": "dhunter@lancastermorgan.com",
    "north country animal hospital|caribou": "NCAH@yourvetdoc.com",
    "noyes flower & plant shoppe|caribou": "noyesflowers@gmail.com",
    "noyes flower and plant shoppe|caribou": "noyesflowers@gmail.com",
    "old iron inn bed & breakfast|caribou": "kateandkevin@oldironinn.com",
    "aroostook savings & loan|caribou": "customerservice@yourhomebank.com",

    # === Houlton region new research (June 2026) ===
    "#9 lake outfitters|bridgewater": "email@9lakeoutfitters.com",
    "bradbury barrel company|bridgewater": "info@bradburybarrel.com",
    "forticor farms|hodgdon": "info@forticorfarms.com",
    "hidden spring winery|houlton": "hiddenspring@mail.com",
    "j & j cedar mill|bridgewater": "info@jjcedarmill.com",

    # === Millinocket/Lincoln new research (June 2026) ===
    "crandall's hardware|east millinocket": "info@crandallshardware.com",
    "ellis family market|east millinocket": "peter.ellis@hannaford.com",
    "appalachian trail lodge|millinocket": "info@appalachiantrailhostel.com",
    "gather inn|millinocket": "gatherinn.me@gmail.com",
    "magic city real estate|millinocket": "magiccityrealestate@outlook.com",
    "ellis family market|patten": "joellis@hannaford.com",
    "mt. chase lodge|mount chase": "info@mtchaselodge.com",
    "marble creek acres winery & cidery|lee": "mainecellars@gmail.com",
}

def normalize(s):
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9\s]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s

def make_key(name, town):
    return f"{normalize(name)}|{normalize(town)}"

def preprocess():
    normalized = {}
    for raw_key, email in EMAIL_UPDATES.items():
        parts = raw_key.split('|')
        if len(parts) == 2:
            normalized[make_key(parts[0], parts[1])] = email
    return normalized

def main():
    normalized = preprocess()
    total_applied = 0

    for region in ['presque_isle_area', 'houlton_region', 'millinocket_area', 'lincoln_area']:
        fp = f'cleaned/{region}.csv'
        with open(fp, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = reader.fieldnames

        updated = 0
        for row in rows:
            key = make_key(row['Business Name'], row['Town'])
            if key in normalized and not row.get('Email', '').strip():
                row['Email'] = normalized[key]
                updated += 1

        if updated:
            with open(fp, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

        total_applied += updated
        print(f'{region}: Added {updated} emails')

    print(f'\nTotal emails added: {total_applied}')

if __name__ == '__main__':
    main()
