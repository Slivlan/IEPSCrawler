import urllib
import selenium
from urllib import robotparser
import psycopg2
import threading
import concurrent.futures

domains = ["gov.si", "evem.gov.si", "e-uprava.gov.si", "e-prostor.gov.si"]
request_rate = 5
user_agent = "fri-ieps-nasagrupa"

def put_site_in_db(domain):

    try:
        conn = psycopg2.connect("host=167.71.67.220 dbname=crawler user=crawler password=tojegeslo")
        conn.autocommit = True
        cur = conn.cursor()
        url = "http://{}/robots.txt".format(domain)
        robots_sitemap_data = get_robots_sitemap_data(url)
        cur.execute("SELECT domain FROM crawldb.site WHERE domain = %s", (domain,))
        rows = cur.fetchall()
        if not rows:
            cur.execute("INSERT INTO crawldb.site (domain, robots_content, sitemap_content) VALUES (%s, %s, %s)", (domain, robots_sitemap_data[0], robots_sitemap_data[1]))

    except Exception as e:
        print(e)

    finally:
        cur.close()
        conn.close()

def get_robots_sitemap_data(url):
    #TODO: return (sitemap_data, robots_data)

    rp = urllib.robotparser.RobotFileParser(url=url)
    rp.read()
    # if rp.request_rate() > 5:
    #     request_rate = rp.request_rate(user_agent)

    s = rp.site_maps()

    request = urllib.request.Request(
        url,
        headers={'User-Agent': user_agent}
    )

    with urllib.request.urlopen(request) as response:
        robots_data = response.read().decode("utf-8")

    request = urllib.request.Request(
        s,
        headers={'User-Agent': user_agent}
    )

    with urllib.request.urlopen(request) as response:
        sitemap_data = response.read().decode("utf-8")

    return (robots_data, sitemap_data)

lock = threading.Lock()

with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    print(f"\n ... executing workers ...\n")
    for domain in domains:
        executor.submit(put_site_in_db, domain)