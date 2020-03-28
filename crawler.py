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
    conn = psycopg2.connect("host=167.71.67.220 dbname=crawler user=crawler password=tojegeslo")
    conn.autocommit = True

    cur = conn.cursor()

    url = "http://{}/robots.txt"
    robots_data = get_robots_data(url)
    cur.execute("""INSERT INTO crawldb.site (domain, robots_content, sitemap_content) VALUES ('%s', '%s', '%s')""", (domain, robots_data[0], robots_data[1]))

    cur.close()
    conn.close()

def get_robots_data(url):
    #TODO: return (sitemap_data, robots_data)

    rp = urllib.robotparser.RobotFileParser(url=url)
    rp.read()
    return ("test_sitemap","test_robots")


    #s = rp.site_maps()

    # if rp.request_rate() > 5:
    #     request_rate = rp.request_rate(user_agent)

lock = threading.Lock()

with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    print(f"\n ... executing workers ...\n")
    for domain in domains:
        executor.submit(put_site_in_db, domain)